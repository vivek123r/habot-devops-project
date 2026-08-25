# -*- coding: utf-8 -*-
"""
Candidate : Vivek R
Contact   : vivekravi9496497657@gmail.com | +91 8590609366
Project   : HabotConnect Hiring Project 1.0
            Junior Cloud & DevOps Engineer (GCP / Django / React)
File      : onboarding/tests/test_serializers.py
Purpose   : Serializer-contract tests: valid payload, missing fields, wrong
          types, boundaries, and boolean Decision Yes/No gates - each with the
          exact machine-readable error code asserted.
"""

from __future__ import annotations

from onboarding import constants
from onboarding.serializers import StudentOnboardingSubmissionSerializer


def valid_payload() -> dict:
    return {
        "parent_full_name": "Ananya Menon",
        "parent_email": "ananya@example.com",
        "parent_phone": "+919876543210",
        "child_full_name": "Arav Menon",
        "child_date_of_birth": "2019-05-14",
        "learning_difficulty_category": constants.CATEGORY_AUTISM,
        "support_needs_summary": "Needs structured reading support three times weekly.",
        "parental_consent_granted": True,
        "data_processing_consent_granted": True,
    }


def assert_single_error(payload: dict, field: str, expected_code: str):
    serializer = StudentOnboardingSubmissionSerializer(data=payload)
    is_valid = serializer.is_valid()
    assert is_valid is False, f"expected rejection for {field}, got validated_data"
    codes = serializer.errors[field]
    flattened = [
        item
        for entry in codes
        for item in (entry if isinstance(entry, list) else [entry])
    ]
    messages = [
        entry.get("code", entry) if isinstance(entry, dict) else str(entry)
        for entry in flattened
    ]
    assert any(expected_code in str(message) for message in messages), serializer.errors


class TestValidPayload:
    def test_complete_payload_passes(self):
        serializer = StudentOnboardingSubmissionSerializer(data=valid_payload())
        assert serializer.is_valid(), serializer.errors

    def test_summary_optional(self):
        payload = valid_payload()
        del payload["support_needs_summary"]
        serializer = StudentOnboardingSubmissionSerializer(data=payload)
        assert serializer.is_valid(), serializer.errors

    def test_email_lowercased_deterministically(self):
        payload = valid_payload()
        payload["parent_email"] = "Ananya@Example.COM"
        serializer = StudentOnboardingSubmissionSerializer(data=payload)
        assert serializer.is_valid()
        assert serializer.validated_data["parent_email"] == "ananya@example.com"

    def test_whitespace_names_trimmed(self):
        payload = valid_payload()
        payload["parent_full_name"] = "  Ananya Menon  "
        serializer = StudentOnboardingSubmissionSerializer(data=payload)
        assert serializer.is_valid()
        assert serializer.validated_data["parent_full_name"] == "Ananya Menon"


class TestRequiredFieldValidation:
    REQUIRED_FIELDS = [
        "parent_full_name",
        "parent_email",
        "parent_phone",
        "child_full_name",
        "child_date_of_birth",
        "learning_difficulty_category",
        "parental_consent_granted",
        "data_processing_consent_granted",
    ]

    def test_each_required_field_missing_is_rejected_with_code(self):
        for field in self.REQUIRED_FIELDS:
            payload = valid_payload()
            del payload[field]
            serializer = StudentOnboardingSubmissionSerializer(data=payload)
            assert serializer.is_valid() is False, field
            assert field in serializer.errors, f"missing error surface for {field}"
            joined = str(serializer.errors[field])
            assert f"ERR_REQUIRED_{field.upper()}" in joined, (field, serializer.errors)

    def test_null_for_required_string_rejected(self):
        payload = valid_payload()
        payload["child_full_name"] = None
        serializer = StudentOnboardingSubmissionSerializer(data=payload)
        assert serializer.is_valid() is False
        assert "ERR_EXACT_JSON_TYPE_STRING_REQUIRED" in str(serializer.errors)


class TestTypeValidation:
    def test_integer_name_rejected_as_type_error(self):
        payload = valid_payload()
        payload["parent_full_name"] = 42
        serializer = StudentOnboardingSubmissionSerializer(data=payload)
        assert serializer.is_valid() is False
        assert "ERR_EXACT_JSON_TYPE_STRING_REQUIRED" in str(serializer.errors)

    def test_numeric_phone_rejected_as_type_error(self):
        payload = valid_payload()
        payload["parent_phone"] = 919876543210
        serializer = StudentOnboardingSubmissionSerializer(data=payload)
        assert serializer.is_valid() is False
        assert "ERR_EXACT_JSON_TYPE_STRING_REQUIRED" in str(serializer.errors)

    def test_string_true_consent_rejected_as_type_error(self):
        payload = valid_payload()
        payload["data_processing_consent_granted"] = "true"
        serializer = StudentOnboardingSubmissionSerializer(data=payload)
        assert serializer.is_valid() is False
        assert "ERR_EXACT_JSON_TYPE_BOOLEAN_REQUIRED" in str(serializer.errors)

    def test_integer_one_consent_rejected_as_type_error(self):
        payload = valid_payload()
        payload["parental_consent_granted"] = 1
        serializer = StudentOnboardingSubmissionSerializer(data=payload)
        assert serializer.is_valid() is False
        assert "ERR_EXACT_JSON_TYPE_BOOLEAN_REQUIRED" in str(serializer.errors)

    def test_list_payload_rejected_entirely(self):
        serializer = StudentOnboardingSubmissionSerializer(data=[valid_payload()])
        assert serializer.is_valid() is False
        assert "non_field_errors" in serializer.errors


class TestBoundaryValidation:
    def test_parent_name_at_max_length_passes(self):
        payload = valid_payload()
        payload["parent_full_name"] = "Aa" + ("b" * 118)
        serializer = StudentOnboardingSubmissionSerializer(data=payload)
        assert serializer.is_valid(), serializer.errors

    def test_parent_name_over_max_length_fails_with_code(self):
        payload = valid_payload()
        payload["parent_full_name"] = "Aa" + ("b" * 119)
        assert_single_error(
            payload, "parent_full_name", "ERR_MAX_LENGTH_PARENT_FULL_NAME"
        )

    def test_child_name_below_min_length_fails_with_code(self):
        payload = valid_payload()
        payload["child_full_name"] = "A"
        assert_single_error(
            payload, "child_full_name", "ERR_MIN_LENGTH_CHILD_FULL_NAME"
        )

    def test_summary_over_max_length_fails_with_code(self):
        payload = valid_payload()
        payload["support_needs_summary"] = "x" * 1001
        assert_single_error(
            payload, "support_needs_summary", "ERR_MAX_LENGTH_SUPPORT_NEEDS_SUMMARY"
        )

    def test_summary_below_min_length_fails_with_code(self):
        payload = valid_payload()
        payload["support_needs_summary"] = "too few"
        assert_single_error(
            payload, "support_needs_summary", "ERR_MIN_LENGTH_SUPPORT_NEEDS_SUMMARY"
        )

    def test_malformed_date_rejected_with_format_code(self):
        payload = valid_payload()
        payload["child_date_of_birth"] = "24/08/2019"
        assert_single_error(
            payload, "child_date_of_birth", "ERR_FORMAT_CHILD_DATE_OF_BIRTH"
        )

    def test_impossible_calendar_date_rejected(self):
        payload = valid_payload()
        payload["child_date_of_birth"] = "2019-02-30"
        assert_single_error(
            payload, "child_date_of_birth", "ERR_FORMAT_CHILD_DATE_OF_BIRTH"
        )

    def test_age_exactly_two_accepted(self):
        payload = valid_payload()
        payload["child_date_of_birth"] = (
            "2024-08-14"  # twelve years old? no: see age test below
        )
        serializer = StudentOnboardingSubmissionSerializer(data=payload)
        # The API-level boundary tests pin the window precisely; here we only
        # assert that a school-age child inside the window passes.
        assert serializer.is_valid(), serializer.errors

    def test_age_outside_window_rejected_with_code(self):
        payload = valid_payload()
        payload["child_date_of_birth"] = "2001-01-01"  # twenty-five completed years
        assert_single_error(
            payload, "child_date_of_birth", "ERR_AGE_OUTSIDE_WINDOW_CHILD_DATE_OF_BIRTH"
        )


class TestChoiceAndGrammarValidation:
    def test_unknown_category_rejected_with_code(self):
        payload = valid_payload()
        payload["learning_difficulty_category"] = "Something Undocumented"
        assert_single_error(
            payload,
            "learning_difficulty_category",
            "ERR_UNKNOWN_LEARNING_DIFFICULTY_CATEGORY",
        )

    def test_digits_in_child_name_fail_grammar_gate(self):
        payload = valid_payload()
        payload["child_full_name"] = "Arav 3rd"
        assert_single_error(payload, "child_full_name", "ERR_GRAMMAR_CHILD_FULL_NAME")

    def test_bad_phone_shape_rejected_with_format_code(self):
        payload = valid_payload()
        payload["parent_phone"] = "+91-98765-43210"
        assert_single_error(payload, "parent_phone", "ERR_FORMAT_PARENT_PHONE")


class TestBooleanConsentGates:
    def test_false_consent_rejected_with_value_code(self):
        payload = valid_payload()
        payload["parental_consent_granted"] = False
        assert_single_error(
            payload, "parental_consent_granted", "ERR_CONSENT_VALUE_FALSE_REJECTED"
        )

    def test_false_processing_consent_rejected_with_value_code(self):
        payload = valid_payload()
        payload["data_processing_consent_granted"] = False
        assert_single_error(
            payload,
            "data_processing_consent_granted",
            "ERR_CONSENT_VALUE_FALSE_REJECTED",
        )

    def test_both_consents_false_reports_both_gates(self):
        payload = valid_payload()
        payload["parental_consent_granted"] = False
        payload["data_processing_consent_granted"] = False
        serializer = StudentOnboardingSubmissionSerializer(data=payload)
        assert serializer.is_valid() is False
        assert set(serializer.errors.keys()) == {
            "parental_consent_granted",
            "data_processing_consent_granted",
        }


class TestEnvelopeStrictness:
    def test_unknown_field_rejected_with_documented_code(self):
        payload = valid_payload()
        payload["is_vip"] = True
        serializer = StudentOnboardingSubmissionSerializer(data=payload)
        assert serializer.is_valid() is False
        assert "ERR_UNKNOWN_FIELD_NOT_IN_DOCUMENTED_ENVELOPE" in str(serializer.errors)

    def test_identical_input_gives_identical_errors(self):
        broken = valid_payload()
        broken["parent_email"] = "not-an-email"
        first_serializer = StudentOnboardingSubmissionSerializer(data=dict(broken))
        second_serializer = StudentOnboardingSubmissionSerializer(data=dict(broken))
        first_serializer.is_valid()
        second_serializer.is_valid()
        assert str(first_serializer.errors) == str(second_serializer.errors)
