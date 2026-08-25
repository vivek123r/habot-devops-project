# -*- coding: utf-8 -*-
"""
Candidate : Vivek R
Contact   : vivekravi9496497657@gmail.com | +91 8590609366
Project   : HabotConnect Hiring Project 1.0
            Junior Cloud & DevOps Engineer (GCP / Django / React)
File      : onboarding/tests/test_api_flow.py
Purpose   : Endpoint-level behavior: binary HTTP outcomes, persistence of
          accepted payloads with their Decision Yes/No record, rejection
          without persistence, and exact age-window boundaries at the API.
"""

from __future__ import annotations

import datetime as dt

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from onboarding import constants
from onboarding.models import StudentOnboardingSubmission


def valid_payload() -> dict:
    return {
        "parent_full_name": "Ananya Menon",
        "parent_email": "ananya@example.com",
        "parent_phone": "+919876543210",
        "child_full_name": "Arav Menon",
        "child_date_of_birth": "2019-05-14",
        "learning_difficulty_category": constants.CATEGORY_DYSLEXIA,
        "parental_consent_granted": True,
        "data_processing_consent_granted": True,
    }


@pytest.fixture
def client() -> Client:
    return Client()


def post_json(client: Client, payload) -> object:
    import json

    url = reverse("onboarding:submission-create")
    return client.post(
        url,
        data=json.dumps(payload),
        content_type="application/json",
    )


class TestAcceptedFlow:
    def test_valid_submission_returns_created_with_decision_record(self, client, db):
        response = post_json(client, valid_payload())
        assert response.status_code == 201
        body = response.json()
        assert body["status"] == "ACCEPTED"
        assert body["dcyn_decision"]["all_rules_passed"] is True

    def test_accepted_submission_is_persisted(self, client, db):
        payload = valid_payload()
        post_json(client, payload)
        stored = StudentOnboardingSubmission.objects.get()
        assert stored.parent_email == payload["parent_email"]
        assert stored.dcyn_all_rules_passed is True
        assert stored.dcyn_decision_record["all_rules_passed"] is True

    def test_repeated_identical_submissions_are_independent_and_deterministic(
        self, client, db
    ):
        first = post_json(client, valid_payload()).json()
        second = post_json(client, valid_payload()).json()
        assert first["submission_id"] != second["submission_id"]
        assert first["dcyn_decision"] == second["dcyn_decision"]


class TestRejectedFlow:
    def test_missing_consent_returns_rejected_with_no_persistence(self, client, db):
        payload = valid_payload()
        del payload["parental_consent_granted"]
        response = post_json(client, payload)
        assert response.status_code == 400
        body = response.json()
        assert body["status"] == "REJECTED"
        assert body["dcyn_decision"]["all_rules_passed"] is False
        assert StudentOnboardingSubmission.objects.count() == 0

    def test_underage_child_rejected_at_boundary_day(self, client, db, monkeypatch):
        monkeypatch.setattr(timezone, "localdate", lambda *a, **k: dt.date(2026, 8, 24))
        payload = valid_payload()
        payload["child_date_of_birth"] = "2024-08-25"
        response = post_json(client, payload)
        assert response.status_code == 400
        assert "ERR_AGE_OUTSIDE_WINDOW_CHILD_DATE_OF_BIRTH" in str(
            response.json()["errors"]
        )

    def test_unknown_field_never_enters_the_pipeline(self, client, db):
        payload = valid_payload()
        payload["role"] = "administrator"
        response = post_json(client, payload)
        assert response.status_code == 400
        assert "ERR_UNKNOWN_FIELD_NOT_IN_DOCUMENTED_ENVELOPE" in str(
            response.json()["errors"]
        )
        assert StudentOnboardingSubmission.objects.count() == 0

    def test_malformed_body_is_rejected_cleanly(self, client, db):
        url = reverse("onboarding:submission-create")
        response = client.post(url, data="not json", content_type="application/json")
        assert response.status_code in {400}


class TestAgeWindowAtApi:
    def test_exactly_two_years_old_accepted_with_frozen_clock(
        self, client, db, monkeypatch
    ):
        fixed_now = dt.datetime(2026, 8, 24, 10, 0, 0, tzinfo=dt.timezone.utc)
        monkeypatch.setattr(timezone, "localdate", lambda *a, **k: dt.date(2026, 8, 24))
        payload = valid_payload()
        payload["child_date_of_birth"] = "2024-08-24"
        response = post_json(client, payload)
        del fixed_now
        assert response.status_code == 201, response.json()

    def test_one_day_short_of_two_years_rejected_with_frozen_clock(
        self, client, db, monkeypatch
    ):
        monkeypatch.setattr(timezone, "localdate", lambda *a, **k: dt.date(2026, 8, 24))
        payload = valid_payload()
        payload["child_date_of_birth"] = "2024-08-25"
        response = post_json(client, payload)
        assert response.status_code == 400

    def test_exactly_eighteen_years_accepted_with_frozen_clock(
        self, client, db, monkeypatch
    ):
        monkeypatch.setattr(timezone, "localdate", lambda *a, **k: dt.date(2026, 8, 24))
        payload = valid_payload()
        payload["child_date_of_birth"] = "2008-08-24"
        response = post_json(client, payload)
        assert response.status_code == 201

    def test_one_day_past_eighteen_rejected_with_frozen_clock(
        self, client, db, monkeypatch
    ):
        monkeypatch.setattr(timezone, "localdate", lambda *a, **k: dt.date(2026, 8, 24))
        payload = valid_payload()
        payload["child_date_of_birth"] = "2007-08-23"
        response = post_json(client, payload)
        assert response.status_code == 400
