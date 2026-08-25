# -*- coding: utf-8 -*-
"""
Candidate : Vivek R
Contact   : vivekravi9496497657@gmail.com | +91 8590609366
Project   : HabotConnect Hiring Project 1.0
            Junior Cloud & DevOps Engineer (GCP / Django / React)
File      : onboarding/dcyn.py
Purpose   : The Decision Yes/No (DCYN) library - Task 3's binary logic core.

          Every rule in the hiring document's vocabulary reduces to exactly
          one of two outcomes, YES or NO. There is no third state, no
          severity score, no human judgment anywhere in this module.

          Design properties:
            - Framework-free: pure Python over plain dictionaries, so the
              identical evaluator runs inside Django Rest Framework views,
              inside tests, and against archived payloads replayed from the
              D0 raw landing bucket.
            - Total: evaluate_submission always returns a DecisionRecord with
              one entry per rule identifier; a missing input can never yield
              a missing verdict.
            - Deterministic: same inputs plus the same evaluation date give
              byte-identical records forever, which is what makes the audit
              trail in BigQuery meaningful.
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import json
import re
from typing import Any, Mapping

from onboarding import constants


@dataclasses.dataclass(frozen=True)
class RuleDecision:
    """One rule, one binary outcome, one factual detail string."""

    rule_id: str
    description: str
    outcome: str  # constants.OUTCOME_YES or constants.OUTCOME_NO
    detail: str

    def as_dict(self) -> dict[str, str]:
        return {
            "rule_id": self.rule_id,
            "description": self.description,
            "outcome": self.outcome,
            "detail": self.detail,
        }


@dataclasses.dataclass(frozen=True)
class DecisionRecord:
    """The complete, ordered set of rule outcomes for one submission."""

    decisions: tuple[RuleDecision, ...]

    @property
    def all_rules_passed(self) -> bool:
        return all(d.outcome == constants.OUTCOME_YES for d in self.decisions)

    def as_dict(self) -> dict[str, Any]:
        return {
            "all_rules_passed": self.all_rules_passed,
            "rules": [d.as_dict() for d in self.decisions],
        }

    def to_json(self) -> str:
        return json.dumps(self.as_dict(), sort_keys=True, separators=(",", ":"))


# ---------------------------------------------------------------------------
# Primitive predicates - each returns exactly True or False.
# ---------------------------------------------------------------------------

_NAME_RE = re.compile(constants.NAME_PATTERN, re.UNICODE)
_PHONE_RE = re.compile(constants.PHONE_PATTERN)


def _is_exact_type(value: Any, expected: type) -> bool:
    return isinstance(value, expected) and not isinstance(value, bool)


def is_valid_name(value: Any, min_length: int, max_length: int) -> bool:
    if not _is_exact_type(value, str):
        return False
    candidate = value.strip()
    if not (min_length <= len(candidate) <= max_length):
        return False
    return _NAME_RE.match(candidate) is not None


def is_valid_email(value: Any) -> bool:
    # Structural check only: exactly one commercial at sign, non-empty local
    # part and domain, domain carries at least one dot, no whitespace anywhere.
    if not _is_exact_type(value, str):
        return False
    candidate = value.strip().lower()
    if not candidate or len(candidate) > constants.EMAIL_MAX_LENGTH:
        return False
    if candidate.count("@") != 1 or " " in candidate:
        return False
    local, _, domain = candidate.partition("@")
    if not local or not domain:
        return False
    if domain.count(".") < 1 or domain.startswith(".") or domain.endswith("."):
        return False
    return True


def is_valid_phone(value: Any) -> bool:
    if not _is_exact_type(value, str):
        return False
    return _PHONE_RE.match(value.strip()) is not None


def parse_iso_date(value: Any) -> dt.date | None:
    if not _is_exact_type(value, str):
        return None
    try:
        parsed = dt.date.fromisoformat(value)
    except ValueError:
        return None
    # Reject zero padded month/day outside real calendar ranges - fromisoformat
    # already guarantees a real date, so any returned value is well formed.
    return parsed


def completed_years(birth_date: dt.date, on_date: dt.date) -> int:
    years = on_date.year - birth_date.year
    before_birthday = (on_date.month, on_date.day) < (birth_date.month, birth_date.day)
    return years - 1 if before_birthday else years


def is_within_age_window(birth_date: dt.date, on_date: dt.date) -> bool:
    age = completed_years(birth_date, on_date)
    return constants.CHILD_AGE_MIN_YEARS <= age <= constants.CHILD_AGE_MAX_YEARS


def is_known_category(value: Any) -> bool:
    return (
        _is_exact_type(value, str) and value in constants.LEARNING_DIFFICULTY_CATEGORIES
    )


def is_true_boolean(value: Any) -> bool:
    # Exactly the JSON boolean true. Strings like "true" and numbers like 1
    # are type violations, not consent - that distinction is the whole point
    # of rules R09 and R10.
    return isinstance(value, bool) and value is True


# ---------------------------------------------------------------------------
# Allowed payload envelope
# ---------------------------------------------------------------------------

ALLOWED_FIELD_NAMES: frozenset[str] = frozenset(
    {
        "parent_full_name",
        "parent_email",
        "parent_phone",
        "child_full_name",
        "child_date_of_birth",
        "learning_difficulty_category",
        "support_needs_summary",
        "parental_consent_granted",
        "data_processing_consent_granted",
    }
)

REQUIRED_FIELD_NAMES: frozenset[str] = ALLOWED_FIELD_NAMES - {"support_needs_summary"}

_EXACT_TYPE_EXPECTATIONS: dict[str, tuple[type, ...]] = {
    "parent_full_name": (str,),
    "parent_email": (str,),
    "parent_phone": (str,),
    "child_full_name": (str,),
    "child_date_of_birth": (str,),
    "learning_difficulty_category": (str,),
    "support_needs_summary": (str,),
    "parental_consent_granted": (bool,),
    "data_processing_consent_granted": (bool,),
}


# ---------------------------------------------------------------------------
# The evaluator
# ---------------------------------------------------------------------------


def evaluate_submission(
    payload: Mapping[str, Any],
    evaluation_date: dt.date | None = None,
) -> DecisionRecord:
    """
    Deconstruct one incoming onboarding payload into its full set of binary
    rule outcomes. ``evaluation_date`` defaults to today (UTC) and exists so
    tests and audits can reproduce any historical decision exactly.
    """
    on_date = evaluation_date or dt.datetime.now(dt.timezone.utc).date()
    unknown = sorted(set(payload.keys()) - ALLOWED_FIELD_NAMES)

    decisions: list[RuleDecision] = []

    def add(rule_id: str, description: str, passed: bool, detail: str) -> None:
        outcome = constants.OUTCOME_YES if passed else constants.OUTCOME_NO
        decisions.append(RuleDecision(rule_id, description, outcome, detail))

    # R11 - envelope strictness first: unknown keys make every downstream
    # guarantee unprovable, so they fail their own rule explicitly.
    add(
        constants.RULE_R11_NO_UNKNOWN_FIELDS,
        "Payload contains only the nine documented field names.",
        not unknown,
        f"unknown_fields={unknown}" if unknown else "no unknown fields",
    )

    # R12 - exact types for every present field; absence of a required field
    # is itself a violation because absence is never an exact-type pass.
    wrong_types: list[str] = []
    for field_name, expected_type in _EXACT_TYPE_EXPECTATIONS.items():
        if field_name not in payload:
            if field_name in REQUIRED_FIELD_NAMES:
                wrong_types.append(field_name)
        elif not isinstance(payload[field_name], expected_type):
            wrong_types.append(field_name)
    wrong_types.sort()
    add(
        constants.RULE_R12_EXACT_FIELD_TYPES,
        "Every present field has exactly its documented JSON type.",
        not wrong_types,
        f"type_violations={wrong_types}" if wrong_types else "all types exact",
    )

    # R01 - parent full name presence, length window, character grammar.
    name_ok = is_valid_name(
        payload.get("parent_full_name"),
        constants.PARENT_FULL_NAME_MIN_LENGTH,
        constants.PARENT_FULL_NAME_MAX_LENGTH,
    )
    add(
        constants.RULE_R01_PARENT_FULL_NAME,
        "Parent full name present, two to one hundred twenty characters, letters with single spaces hyphens apostrophes periods.",
        name_ok,
        "valid" if name_ok else "invalid or absent",
    )

    # R02 - parent email structural validity.
    email_ok = is_valid_email(payload.get("parent_email"))
    add(
        constants.RULE_R02_PARENT_EMAIL,
        "Parent email present, at most two hundred fifty four characters, structurally valid.",
        email_ok,
        "valid" if email_ok else "invalid or absent",
    )

    # R03 - parent phone in international direct dialing format.
    phone_ok = is_valid_phone(payload.get("parent_phone"))
    add(
        constants.RULE_R03_PARENT_PHONE,
        "Parent phone present in international format plus country code and seven to fifteen digits.",
        phone_ok,
        "valid" if phone_ok else "invalid or absent",
    )

    # R04 - child full name under the same grammar as the parent name.
    child_ok = is_valid_name(
        payload.get("child_full_name"),
        constants.CHILD_FULL_NAME_MIN_LENGTH,
        constants.CHILD_FULL_NAME_MAX_LENGTH,
    )
    add(
        constants.RULE_R04_CHILD_FULL_NAME,
        "Child full name present, two to one hundred twenty characters, letters with single spaces hyphens apostrophes periods.",
        child_ok,
        "valid" if child_ok else "invalid or absent",
    )

    # R05 - child date of birth parses as an ISO eight sixty sixty one date.
    birth_date = parse_iso_date(payload.get("child_date_of_birth"))
    add(
        constants.RULE_R05_CHILD_DATE_OF_BIRTH_FORMAT,
        "Child date of birth present as a valid ISO calendar date.",
        birth_date is not None,
        "valid ISO date" if birth_date else "invalid or absent",
    )

    # R06 - completed age inside the inclusive two-to-eighteen window.
    age_ok = birth_date is not None and is_within_age_window(birth_date, on_date)
    if birth_date is None:
        age_detail = "not evaluable without a valid date of birth"
    else:
        age_detail = f"completed_years={completed_years(birth_date, on_date)}"
    add(
        constants.RULE_R06_CHILD_AGE_WINDOW,
        "Child completed age between two and eighteen inclusive at evaluation time.",
        age_ok,
        age_detail,
    )

    # R07 - category membership in the closed seven-value set.
    category_ok = is_known_category(payload.get("learning_difficulty_category"))
    add(
        constants.RULE_R07_LEARNING_DIFFICULTY_CATEGORY,
        "Learning difficulty category equals one of the seven documented values.",
        category_ok,
        "member of closed set" if category_ok else "not in closed set or absent",
    )

    # R08 - optional summary, but bounded when present.
    summary_value = payload.get("support_needs_summary")
    if summary_value is None:
        summary_ok, summary_detail = True, "absent and therefore permitted"
    elif not _is_exact_type(summary_value, str):
        summary_ok, summary_detail = False, "present but not a string"
    else:
        stripped = summary_value.strip()
        summary_ok = (
            constants.SUPPORT_NEEDS_SUMMARY_MIN_LENGTH
            <= len(stripped)
            <= constants.SUPPORT_NEEDS_SUMMARY_MAX_LENGTH
        ) or len(stripped) == 0
        # Empty after stripping means the parent chose not to provide context;
        # that is stored as absent rather than rejected.
        if len(stripped) == 0:
            summary_ok, summary_detail = True, "empty after trimming, treated as absent"
        elif summary_ok:
            summary_detail = f"length={len(stripped)} within bounds"
        else:
            summary_detail = f"length={len(stripped)} outside bounds"
    add(
        constants.RULE_R08_SUPPORT_NEEDS_SUMMARY,
        "Optional support needs summary either absent or between ten and one thousand characters after trimming.",
        summary_ok,
        summary_detail,
    )

    # R09 and R10 - the consent gates. Only literal boolean true passes.
    parental_ok = is_true_boolean(payload.get("parental_consent_granted"))
    add(
        constants.RULE_R09_PARENTAL_CONSENT_TRUE,
        "Parental consent granted is exactly the boolean true value.",
        parental_ok,
        "true" if parental_ok else "false, absent, mistyped, or null",
    )

    processing_ok = is_true_boolean(payload.get("data_processing_consent_granted"))
    add(
        constants.RULE_R10_DATA_PROCESSING_CONSENT_TRUE,
        "Data processing consent granted is exactly the boolean true value.",
        processing_ok,
        "true" if processing_ok else "false, absent, mistyped, or null",
    )

    return DecisionRecord(decisions=tuple(decisions))
