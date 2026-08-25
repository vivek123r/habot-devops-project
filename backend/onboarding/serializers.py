# -*- coding: utf-8 -*-
"""
Candidate : Vivek R
Contact   : vivekravi9496497657@gmail.com | +91 8590609366
Project   : HabotConnect Hiring Project 1.0
            Junior Cloud & DevOps Engineer (GCP / Django / React)
File      : onboarding/serializers.py
Purpose   : The Django Rest Framework serializer demanded by Task 3.

          Every limit is imported from onboarding/constants.py - the same
          file the Decision Yes/No library and the BigQuery enforced schema
          quote - so no layer can silently drift from another. Validation is
          deterministic: identical input always produces identical field
          errors with stable machine-readable codes.
"""

from __future__ import annotations

import re

from django.utils import timezone
from rest_framework import serializers

from onboarding import constants, dcyn
from onboarding.models import StudentOnboardingSubmission


class StrictEnvelopeSerializerMixin:
    """
    Envelope and exact-type law, enforced before any field machinery runs.

    Default Rest Framework behavior silently drops unknown keys and coerces
    scalars (the integer forty two becomes the string forty two), which would
    make the accepted-payload contract unfalsifiable and reintroduce exactly
    the silent judgment Task 3 eliminates. Rules R11 and R12 depend on this
    mixin.
    """

    EXACT_STRING_FIELDS: tuple[str, ...] = ()
    EXACT_BOOLEAN_FIELDS: tuple[str, ...] = ()

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError(
                {"non_field_errors": ["Payload must be a JSON object."]}
            )
        unknown = sorted(set(data.keys()) - set(self.fields.keys()))
        if unknown:
            raise serializers.ValidationError(
                {
                    field: ["ERR_UNKNOWN_FIELD_NOT_IN_DOCUMENTED_ENVELOPE"]
                    for field in unknown
                }
            )
        for field_name in self.EXACT_STRING_FIELDS:
            if field_name in data and not isinstance(data[field_name], str):
                raise serializers.ValidationError(
                    {field_name: ["ERR_EXACT_JSON_TYPE_STRING_REQUIRED"]}
                )
        for field_name in self.EXACT_BOOLEAN_FIELDS:
            if field_name in data and not isinstance(data[field_name], bool):
                raise serializers.ValidationError(
                    {field_name: ["ERR_EXACT_JSON_TYPE_BOOLEAN_REQUIRED"]}
                )
        return super().to_internal_value(data)


class StudentOnboardingSubmissionSerializer(
    StrictEnvelopeSerializerMixin,
    serializers.Serializer,
):
    """
    Input contract for a student onboarding submission.

    This is an explicit Serializer rather than a ModelSerializer on purpose:
    incoming JSON is untrusted external input with its own strict grammar;
    persistence happens only after validation plus the Decision Yes/No record
    both succeed, in the view layer.
    """

    EXACT_STRING_FIELDS = (
        "parent_full_name",
        "parent_email",
        "parent_phone",
        "child_full_name",
        "child_date_of_birth",
        "learning_difficulty_category",
        "support_needs_summary",
    )

    EXACT_BOOLEAN_FIELDS = (
        "parental_consent_granted",
        "data_processing_consent_granted",
    )

    parent_full_name = serializers.CharField(
        required=True,
        allow_null=False,
        min_length=constants.PARENT_FULL_NAME_MIN_LENGTH,
        max_length=constants.PARENT_FULL_NAME_MAX_LENGTH,
        error_messages={
            "required": "ERR_REQUIRED_PARENT_FULL_NAME",
            "null": "ERR_REQUIRED_PARENT_FULL_NAME",
            "blank": "ERR_BLANK_PARENT_FULL_NAME",
            "min_length": "ERR_MIN_LENGTH_PARENT_FULL_NAME",
            "max_length": "ERR_MAX_LENGTH_PARENT_FULL_NAME",
            "invalid": "ERR_INVALID_TYPE_PARENT_FULL_NAME",
        },
    )
    parent_email = serializers.EmailField(
        required=True,
        allow_null=False,
        max_length=constants.EMAIL_MAX_LENGTH,
        error_messages={
            "required": "ERR_REQUIRED_PARENT_EMAIL",
            "null": "ERR_REQUIRED_PARENT_EMAIL",
            "blank": "ERR_BLANK_PARENT_EMAIL",
            "invalid": "ERR_INVALID_PARENT_EMAIL",
            "max_length": "ERR_MAX_LENGTH_PARENT_EMAIL",
        },
    )
    parent_phone = serializers.RegexField(
        regex=re.compile(constants.PHONE_PATTERN),
        required=True,
        allow_null=False,
        error_messages={
            "required": "ERR_REQUIRED_PARENT_PHONE",
            "null": "ERR_REQUIRED_PARENT_PHONE",
            "blank": "ERR_BLANK_PARENT_PHONE",
            "invalid": "ERR_FORMAT_PARENT_PHONE",
        },
    )
    child_full_name = serializers.CharField(
        required=True,
        allow_null=False,
        min_length=constants.CHILD_FULL_NAME_MIN_LENGTH,
        max_length=constants.CHILD_FULL_NAME_MAX_LENGTH,
        error_messages={
            "required": "ERR_REQUIRED_CHILD_FULL_NAME",
            "null": "ERR_REQUIRED_CHILD_FULL_NAME",
            "blank": "ERR_BLANK_CHILD_FULL_NAME",
            "min_length": "ERR_MIN_LENGTH_CHILD_FULL_NAME",
            "max_length": "ERR_MAX_LENGTH_CHILD_FULL_NAME",
            "invalid": "ERR_INVALID_TYPE_CHILD_FULL_NAME",
        },
    )
    child_date_of_birth = serializers.DateField(
        required=True,
        allow_null=False,
        format="%Y-%m-%d",
        input_formats=["%Y-%m-%d"],
        error_messages={
            "required": "ERR_REQUIRED_CHILD_DATE_OF_BIRTH",
            "null": "ERR_REQUIRED_CHILD_DATE_OF_BIRTH",
            "invalid": "ERR_FORMAT_CHILD_DATE_OF_BIRTH",
        },
    )
    learning_difficulty_category = serializers.ChoiceField(
        required=True,
        allow_null=False,
        choices=list(constants.LEARNING_DIFFICULTY_CATEGORIES),
        error_messages={
            "required": "ERR_REQUIRED_LEARNING_DIFFICULTY_CATEGORY",
            "null": "ERR_REQUIRED_LEARNING_DIFFICULTY_CATEGORY",
            "invalid_choice": "ERR_UNKNOWN_LEARNING_DIFFICULTY_CATEGORY",
        },
    )
    support_needs_summary = serializers.CharField(
        required=False,
        allow_null=False,
        allow_blank=True,
        max_length=constants.SUPPORT_NEEDS_SUMMARY_MAX_LENGTH,
        trim_whitespace=True,
        error_messages={
            "max_length": "ERR_MAX_LENGTH_SUPPORT_NEEDS_SUMMARY",
            "invalid": "ERR_INVALID_TYPE_SUPPORT_NEEDS_SUMMARY",
            "null": "ERR_NULL_NOT_PERMITTED_SUPPORT_NEEDS_SUMMARY",
        },
    )
    parental_consent_granted = serializers.BooleanField(
        required=True,
        allow_null=False,
        error_messages={
            "required": "ERR_REQUIRED_PARENTAL_CONSENT_GRANTED",
            "null": "ERR_REQUIRED_PARENTAL_CONSENT_GRANTED",
            "invalid": "ERR_CONSENT_MUST_BE_BOOLEAN_TRUE",
        },
    )
    data_processing_consent_granted = serializers.BooleanField(
        required=True,
        allow_null=False,
        error_messages={
            "required": "ERR_REQUIRED_DATA_PROCESSING_CONSENT_GRANTED",
            "null": "ERR_REQUIRED_DATA_PROCESSING_CONSENT_GRANTED",
            "invalid": "ERR_CONSENT_MUST_BE_BOOLEAN_TRUE",
        },
    )

    # ----------------------------------------------------------------------
    # Deterministic refinements layered above declarative checks
    # ----------------------------------------------------------------------

    def validate_parent_full_name(self, value: str) -> str:
        cleaned = value.strip()
        if re.match(constants.NAME_PATTERN, cleaned) is None:
            raise serializers.ValidationError("ERR_GRAMMAR_PARENT_FULL_NAME")
        return cleaned

    def validate_child_full_name(self, value: str) -> str:
        cleaned = value.strip()
        if re.match(constants.NAME_PATTERN, cleaned) is None:
            raise serializers.ValidationError("ERR_GRAMMAR_CHILD_FULL_NAME")
        return cleaned

    def validate_parent_email(self, value: str) -> str:
        # Canonical form: one identity, one spelling, forever comparable.
        return value.strip().lower()

    def validate_support_needs_summary(self, value: str) -> str:
        cleaned = value.strip()
        if cleaned and len(cleaned) < constants.SUPPORT_NEEDS_SUMMARY_MIN_LENGTH:
            raise serializers.ValidationError("ERR_MIN_LENGTH_SUPPORT_NEEDS_SUMMARY")
        return cleaned

    def validate_child_date_of_birth(self, value):
        evaluation_date = timezone.localdate()
        age_years = dcyn.completed_years(value, evaluation_date)
        if not (
            constants.CHILD_AGE_MIN_YEARS <= age_years <= constants.CHILD_AGE_MAX_YEARS
        ):
            raise serializers.ValidationError(
                "ERR_AGE_OUTSIDE_WINDOW_CHILD_DATE_OF_BIRTH"
            )
        return value

    def validate_parental_consent_granted(self, value: bool) -> bool:
        # BooleanField already coerces nothing here because StrictBoolean gate
        # below rejects non-boolean JSON types before this method runs.
        if value is not True:
            raise serializers.ValidationError("ERR_CONSENT_VALUE_FALSE_REJECTED")
        return True

    def validate_data_processing_consent_granted(self, value: bool) -> bool:
        if value is not True:
            raise serializers.ValidationError("ERR_CONSENT_VALUE_FALSE_REJECTED")
        return True


class AcceptedSubmissionModelSerializer(serializers.ModelSerializer):
    """Read-only projection of accepted submissions for audit endpoints."""

    class Meta:
        model = StudentOnboardingSubmission
        fields = [
            "submission_id",
            "parent_full_name",
            "parent_email",
            "parent_phone",
            "child_full_name",
            "child_date_of_birth",
            "learning_difficulty_category",
            "support_needs_summary",
            "parental_consent_granted",
            "data_processing_consent_granted",
            "dcyn_all_rules_passed",
            "dcyn_decision_record",
            "submitted_at",
        ]
        read_only_fields = fields
