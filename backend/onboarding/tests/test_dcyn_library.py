# -*- coding: utf-8 -*-
"""
Candidate : Vivek R
Contact   : vivekravi9496497657@gmail.com | +91 8590609366
Project   : HabotConnect Hiring Project 1.0
            Junior Cloud & DevOps Engineer (GCP / Django / React)
File      : onboarding/tests/test_dcyn_library.py
Purpose   : Exhaustive tests for the standalone Decision Yes/No library.

          Every test fixes the evaluation date, so outcomes are reproducible
          forever - the mathematical cleanliness the hiring document demands.
"""

from __future__ import annotations

import datetime as dt

import pytest

from onboarding import constants, dcyn

EVALUATION_DATE = dt.date(2026, 8, 24)


def valid_payload() -> dict:
    return {
        "parent_full_name": "Ananya Menon",
        "parent_email": "Ananya.Menon@Example.com",
        "parent_phone": "+919876543210",
        "child_full_name": "Arav Menon",
        "child_date_of_birth": "2019-05-14",
        "learning_difficulty_category": constants.CATEGORY_DYSLEXIA,
        "parental_consent_granted": True,
        "data_processing_consent_granted": True,
    }


def outcome_for(record: dcyn.DecisionRecord, rule_id: str) -> str:
    return next(d.outcome for d in record.decisions if d.rule_id == rule_id)


class TestValidPayload:
    def test_every_rule_returns_yes(self):
        record = dcyn.evaluate_submission(
            valid_payload(), evaluation_date=EVALUATION_DATE
        )
        assert record.all_rules_passed is True
        assert len(record.decisions) == len(constants.ALL_RULE_IDS)

    def test_record_is_json_serializable_and_stable(self):
        first = dcyn.evaluate_submission(
            valid_payload(), evaluation_date=EVALUATION_DATE
        )
        second = dcyn.evaluate_submission(
            valid_payload(), evaluation_date=EVALUATION_DATE
        )
        assert first.to_json() == second.to_json()
        assert '"all_rules_passed":true' in first.to_json()


class TestNameRules:
    @pytest.mark.parametrize(
        ("field_name", "rule_id"),
        [
            ("parent_full_name", constants.RULE_R01_PARENT_FULL_NAME),
            ("child_full_name", constants.RULE_R04_CHILD_FULL_NAME),
        ],
    )
    def test_minimum_length_boundary_two_letters(self, field_name, rule_id):
        payload = valid_payload()
        payload[field_name] = "Al"
        assert (
            outcome_for(
                dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE),
                rule_id,
            )
            == constants.OUTCOME_YES
        )

    @pytest.mark.parametrize("field_name", ["parent_full_name", "child_full_name"])
    def test_single_letter_rejected(self, field_name):
        payload = valid_payload()
        payload[field_name] = "A"
        record = dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE)
        assert record.all_rules_passed is False

    def test_hyphenated_and_apostrophe_names_accepted(self):
        payload = valid_payload()
        payload["parent_full_name"] = "María-Jose O'Neill"
        assert (
            outcome_for(
                dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE),
                constants.RULE_R01_PARENT_FULL_NAME,
            )
            == constants.OUTCOME_YES
        )

    def test_digits_inside_name_rejected(self):
        payload = valid_payload()
        payload["child_full_name"] = "Arav2"
        assert (
            outcome_for(
                dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE),
                constants.RULE_R04_CHILD_FULL_NAME,
            )
            == constants.OUTCOME_NO
        )

    def test_maximum_length_boundary_one_twenty(self):
        payload = valid_payload()
        payload["parent_full_name"] = "Ab" + (
            "c" * 118
        )  # exactly one hundred twenty letters
        record = dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE)
        assert (
            outcome_for(record, constants.RULE_R01_PARENT_FULL_NAME)
            == constants.OUTCOME_YES
        )

    def test_over_maximum_length_rejected(self):
        payload = valid_payload()
        payload["parent_full_name"] = "Ab" + ("c" * 119)
        assert (
            outcome_for(
                dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE),
                constants.RULE_R01_PARENT_FULL_NAME,
            )
            == constants.OUTCOME_NO
        )


class TestContactRules:
    def test_email_uppercase_normalized_to_yes(self):
        payload = valid_payload()
        payload["parent_email"] = "PARENT@HABOT.EXAMPLE.ORG"
        assert (
            outcome_for(
                dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE),
                constants.RULE_R02_PARENT_EMAIL,
            )
            == constants.OUTCOME_YES
        )

    @pytest.mark.parametrize(
        "bad_email",
        ["no-at-sign", "two@@at.example", "@leading.example", "trailing.@example", ""],
    )
    def test_invalid_emails_rejected(self, bad_email):
        payload = valid_payload()
        payload["parent_email"] = bad_email
        assert (
            outcome_for(
                dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE),
                constants.RULE_R02_PARENT_EMAIL,
            )
            == constants.OUTCOME_NO
        )

    def test_phone_without_plus_rejected(self):
        payload = valid_payload()
        payload["parent_phone"] = "919876543210"
        assert (
            outcome_for(
                dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE),
                constants.RULE_R03_PARENT_PHONE,
            )
            == constants.OUTCOME_NO
        )

    def test_phone_leading_zero_country_code_rejected(self):
        payload = valid_payload()
        payload["parent_phone"] = "+091987654321"
        assert (
            outcome_for(
                dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE),
                constants.RULE_R03_PARENT_PHONE,
            )
            == constants.OUTCOME_NO
        )

    def test_phone_fifteen_digit_boundary_accepted(self):
        payload = valid_payload()
        payload["parent_phone"] = "+123456789012345"  # plus plus fifteen digits
        assert (
            outcome_for(
                dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE),
                constants.RULE_R03_PARENT_PHONE,
            )
            == constants.OUTCOME_YES
        )

    def test_phone_sixteen_digits_rejected(self):
        payload = valid_payload()
        payload["parent_phone"] = "+1234567890123456"
        assert (
            outcome_for(
                dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE),
                constants.RULE_R03_PARENT_PHONE,
            )
            == constants.OUTCOME_NO
        )


class TestAgeBoundaryRules:
    def test_exactly_second_birthday_accepted(self):
        payload = valid_payload()
        payload["child_date_of_birth"] = (
            "2024-08-24"  # completes two years on evaluation day
        )
        assert (
            outcome_for(
                dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE),
                constants.RULE_R06_CHILD_AGE_WINDOW,
            )
            == constants.OUTCOME_YES
        )

    def test_one_day_before_second_birthday_rejected(self):
        payload = valid_payload()
        payload["child_date_of_birth"] = "2024-08-25"
        assert (
            outcome_for(
                dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE),
                constants.RULE_R06_CHILD_AGE_WINDOW,
            )
            == constants.OUTCOME_NO
        )

    def test_exactly_eighteenth_birthday_accepted(self):
        payload = valid_payload()
        payload["child_date_of_birth"] = "2008-08-24"
        assert (
            outcome_for(
                dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE),
                constants.RULE_R06_CHILD_AGE_WINDOW,
            )
            == constants.OUTCOME_YES
        )

    def test_day_after_nineteenth_birthday_rejected(self):
        # Born 2007-08-23: the nineteenth birthday completed one day before
        # the evaluation date, so the child is now nineteen - outside.
        payload = valid_payload()
        payload["child_date_of_birth"] = "2007-08-23"
        assert (
            outcome_for(
                dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE),
                constants.RULE_R06_CHILD_AGE_WINDOW,
            )
            == constants.OUTCOME_NO
        )

    def test_impossible_future_date_fails_format_then_window(self):
        payload = valid_payload()
        payload["child_date_of_birth"] = "2030-01-01"
        record = dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE)
        assert (
            outcome_for(record, constants.RULE_R05_CHILD_DATE_OF_BIRTH_FORMAT)
            == constants.OUTCOME_YES
        )
        assert (
            outcome_for(record, constants.RULE_R06_CHILD_AGE_WINDOW)
            == constants.OUTCOME_NO
        )


class TestCategoryRule:
    @pytest.mark.parametrize("category", list(constants.LEARNING_DIFFICULTY_CATEGORIES))
    def test_every_documented_category_accepted(self, category):
        payload = valid_payload()
        payload["learning_difficulty_category"] = category
        assert (
            outcome_for(
                dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE),
                constants.RULE_R07_LEARNING_DIFFICULTY_CATEGORY,
            )
            == constants.OUTCOME_YES
        )

    def test_abbreviated_category_rejected(self):
        # Full forms only - an abbreviation is an unknown value, deterministically.
        payload = valid_payload()
        payload["learning_difficulty_category"] = "ADHD"
        assert (
            outcome_for(
                dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE),
                constants.RULE_R07_LEARNING_DIFFICULTY_CATEGORY,
            )
            == constants.OUTCOME_NO
        )

    def test_case_mismatch_rejected(self):
        payload = valid_payload()
        payload["learning_difficulty_category"] = constants.CATEGORY_DYSLEXIA.lower()
        assert (
            outcome_for(
                dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE),
                constants.RULE_R07_LEARNING_DIFFICULTY_CATEGORY,
            )
            == constants.OUTCOME_NO
        )


class TestConsentBooleanRules:
    @pytest.mark.parametrize("falsy_value", [False, None])
    def test_false_or_null_consents_rejected(self, falsy_value):
        payload = valid_payload()
        payload["parental_consent_granted"] = falsy_value
        record = dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE)
        assert (
            outcome_for(record, constants.RULE_R09_PARENTAL_CONSENT_TRUE)
            == constants.OUTCOME_NO
        )

    @pytest.mark.parametrize("mistyped_value", ["true", 1, "yes"])
    def test_mistyped_consents_fail_type_rule_not_consent_semantics(
        self, mistyped_value
    ):
        payload = valid_payload()
        payload["data_processing_consent_granted"] = mistyped_value
        record = dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE)
        assert (
            outcome_for(record, constants.RULE_R12_EXACT_FIELD_TYPES)
            == constants.OUTCOME_NO
        )
        assert (
            outcome_for(record, constants.RULE_R10_DATA_PROCESSING_CONSENT_TRUE)
            == constants.OUTCOME_NO
        )


class TestEnvelopeRules:
    def test_unknown_field_fails_rule_eleven(self):
        payload = valid_payload()
        payload["admin_backdoor"] = True
        record = dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE)
        assert (
            outcome_for(record, constants.RULE_R11_NO_UNKNOWN_FIELDS)
            == constants.OUTCOME_NO
        )
        assert record.all_rules_passed is False

    def test_missing_required_field_reported_by_type_rule(self):
        payload = valid_payload()
        del payload["parent_phone"]
        record = dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE)
        assert (
            outcome_for(record, constants.RULE_R12_EXACT_FIELD_TYPES)
            == constants.OUTCOME_NO
        )
        assert (
            outcome_for(record, constants.RULE_R03_PARENT_PHONE) == constants.OUTCOME_NO
        )

    def test_optional_summary_absent_is_yes(self):
        record = dcyn.evaluate_submission(
            valid_payload(), evaluation_date=EVALUATION_DATE
        )
        assert (
            outcome_for(record, constants.RULE_R08_SUPPORT_NEEDS_SUMMARY)
            == constants.OUTCOME_YES
        )

    def test_empty_string_summary_treated_as_absent(self):
        payload = valid_payload()
        payload["support_needs_summary"] = ""
        record = dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE)
        assert (
            outcome_for(record, constants.RULE_R08_SUPPORT_NEEDS_SUMMARY)
            == constants.OUTCOME_YES
        )

    def test_summary_below_min_length_rejected(self):
        payload = valid_payload()
        payload["support_needs_summary"] = "short"
        assert (
            outcome_for(
                dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE),
                constants.RULE_R08_SUPPORT_NEEDS_SUMMARY,
            )
            == constants.OUTCOME_NO
        )

    def test_summary_at_max_length_accepted(self):
        payload = valid_payload()
        payload["support_needs_summary"] = (
            "word " * 199 + "word"
        )  # one thousand characters
        assert (
            outcome_for(
                dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE),
                constants.RULE_R08_SUPPORT_NEEDS_SUMMARY,
            )
            == constants.OUTCOME_YES
        )

    def test_integer_instead_of_string_rejected_by_type_rule(self):
        payload = valid_payload()
        payload["parent_phone"] = 919876543210
        record = dcyn.evaluate_submission(payload, evaluation_date=EVALUATION_DATE)
        assert (
            outcome_for(record, constants.RULE_R12_EXACT_FIELD_TYPES)
            == constants.OUTCOME_NO
        )


class TestEmptyAndMalformedEnvelopes:
    def test_completely_empty_payload_all_gates_no(self):
        record = dcyn.evaluate_submission({}, evaluation_date=EVALUATION_DATE)
        assert record.all_rules_passed is False
        yes_count = sum(
            1 for d in record.decisions if d.outcome == constants.OUTCOME_YES
        )
        assert yes_count >= 1  # optional summary absent is legitimately YES
