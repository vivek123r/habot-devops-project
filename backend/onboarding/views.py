# -*- coding: utf-8 -*-
"""
Candidate : Vivek R
Contact   : vivekravi9496497657@gmail.com | +91 8590609366
Project   : HabotConnect Hiring Project 1.0
            Junior Cloud & DevOps Engineer (GCP / Django / React)
File      : onboarding/views.py
Purpose   : The single ingestion endpoint.

          Contract (binary, deterministic):
            - All twelve Decision Yes/No rules evaluate YES:
                HTTP 201 with the submission identifier and the full decision
                record; the payload is persisted and published downstream.
            - Any rule evaluates NO:
                HTTP 400 with per-field machine-readable error codes plus the
                same full decision record, so callers and auditors see exactly
                which binary rule failed. Nothing is persisted or published.
"""

from __future__ import annotations

import logging

from django.conf import settings
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from onboarding import constants, dcyn
from onboarding.models import StudentOnboardingSubmission
from onboarding.publishers import get_publisher
from onboarding.serializers import StudentOnboardingSubmissionSerializer

logger = logging.getLogger("onboarding.views")


class StudentOnboardingAPIView(APIView):
    """Accepts or rejects one student onboarding form submission."""

    def post(self, request: Request) -> Response:
        serializer = StudentOnboardingSubmissionSerializer(data=request.data)

        if not serializer.is_valid():
            decision_record = dcyn.evaluate_submission(
                request.data if isinstance(request.data, dict) else {}
            )
            logger.info(
                "onboarding rejected",
                extra={
                    "all_rules_passed": False,
                    "failed_rules": [
                        d.rule_id
                        for d in decision_record.decisions
                        if d.outcome == constants.OUTCOME_NO
                    ],
                },
            )
            return Response(
                {
                    "status": "REJECTED",
                    "errors": serializer.errors,
                    "dcyn_decision": decision_record.as_dict(),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated = serializer.validated_data

        # The Decision Yes/No evaluator speaks wire format (pure JSON types),
        # so the accepted payload is projected back onto its exact document
        # representation before the audit record is computed.
        canonical_payload = dict(validated)
        canonical_payload["child_date_of_birth"] = canonical_payload[
            "child_date_of_birth"
        ].isoformat()
        decision_record = dcyn.evaluate_submission(canonical_payload)

        # Persist first: an accepted submission must survive even if the
        # downstream publisher is unavailable; replay covers the gap.
        submission = StudentOnboardingSubmission.objects.create(
            parent_full_name=validated["parent_full_name"],
            parent_email=validated["parent_email"],
            parent_phone=validated["parent_phone"],
            child_full_name=validated["child_full_name"],
            child_date_of_birth=validated["child_date_of_birth"],
            learning_difficulty_category=validated["learning_difficulty_category"],
            support_needs_summary=validated.get("support_needs_summary", ""),
            parental_consent_granted=True,
            data_processing_consent_granted=True,
            dcyn_all_rules_passed=decision_record.all_rules_passed,
            dcyn_decision_record=decision_record.as_dict(),
        )

        event_payload = {
            "submission_id": str(submission.submission_id),
            "parent_full_name": submission.parent_full_name,
            "parent_email": submission.parent_email,
            "parent_phone": submission.parent_phone,
            "child_full_name": submission.child_full_name,
            "child_date_of_birth": submission.child_date_of_birth.isoformat(),
            "learning_difficulty_category": submission.learning_difficulty_category,
            "support_needs_summary": submission.support_needs_summary,
            "parental_consent_granted": True,
            "data_processing_consent_granted": True,
            "dcyn_all_rules_passed": True,
            "submitted_at": submission.submitted_at.isoformat(),
        }

        try:
            get_publisher().publish(event_payload)
        except Exception:  # noqa: BLE001 - publication must never break intake
            logger.exception(
                "downstream publish failed for %s", submission.submission_id
            )

        logger.info(
            "onboarding accepted",
            extra={"submission_id": str(submission.submission_id)},
        )
        return Response(
            {
                "status": "ACCEPTED",
                "submission_id": str(submission.submission_id),
                "topic": settings.ONBOARDING_EVENTS_TOPIC,
                "dcyn_decision": submission.dcyn_decision_record,
            },
            status=status.HTTP_201_CREATED,
        )
