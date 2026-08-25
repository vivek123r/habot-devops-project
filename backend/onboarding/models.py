# -*- coding: utf-8 -*-
"""
Candidate : Vivek R
Contact   : vivekravi9496497657@gmail.com | +91 8590609366
Project   : HabotConnect Hiring Project 1.0
            Junior Cloud & DevOps Engineer (GCP / Django / React)
File      : onboarding/models.py
Purpose   : Persistence for accepted student onboarding submissions.

          Column limits mirror onboarding/constants.py exactly, and the
          column set mirrors the enforced BigQuery table definition in
          terraform/modules/bigquery_staged - one contract, three layers,
          zero drift. The Decision Yes/No record is stored as JSON so every
          acceptance is auditable against the rules that were in force.
"""

from __future__ import annotations

import uuid

from django.db import models

from onboarding import constants


class StudentOnboardingSubmission(models.Model):
    """One validated, accepted student onboarding submission."""

    submission_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    parent_full_name = models.CharField(
        max_length=constants.PARENT_FULL_NAME_MAX_LENGTH
    )
    parent_email = models.EmailField(max_length=constants.EMAIL_MAX_LENGTH)
    parent_phone = models.CharField(max_length=16)

    child_full_name = models.CharField(max_length=constants.CHILD_FULL_NAME_MAX_LENGTH)
    child_date_of_birth = models.DateField()
    learning_difficulty_category = models.CharField(max_length=64)

    support_needs_summary = models.TextField(blank=True, default="")

    parental_consent_granted = models.BooleanField()
    data_processing_consent_granted = models.BooleanField()

    dcyn_all_rules_passed = models.BooleanField(default=True, editable=False)
    dcyn_decision_record = models.JSONField(editable=False)

    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Student Onboarding Submission"
        verbose_name_plural = "Student Onboarding Submissions"
        ordering = ["-submitted_at"]

    def __str__(self) -> str:  # pragma: no cover - display only
        return f"{self.submission_id} ({self.learning_difficulty_category})"
