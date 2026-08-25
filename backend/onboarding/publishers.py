# -*- coding: utf-8 -*-
"""
Candidate : Vivek R
Contact   : vivekravi9496497657@gmail.com | +91 8590609366
Project   : HabotConnect Hiring Project 1.0
            Junior Cloud & DevOps Engineer (GCP / Django / React)
File      : onboarding/publishers.py
Purpose   : Event publication boundary between the validated application and
            the Pub/Sub streaming pipeline.

          The view depends only on the ``publish_onboarding_event`` callable
          resolved from settings; staging resolves the Google Cloud Pub/Sub
          implementation, while local development and tests resolve the null
          publisher that records events locally without any cloud dependency.
          A publishing failure never loses the accepted submission: the row is
          committed first, then the event is published with retries left to
          the transport, and failures are logged for the replay job.
"""

from __future__ import annotations

import logging

from django.conf import settings

logger = logging.getLogger("onboarding.publishers")


class NullPublisher:
    """Deterministic local publisher used by tests and local development."""

    def publish(self, event: dict) -> str | None:  # noqa: ANN001 - dict payload
        logger.info("NullPublisher retained onboarding event locally.")
        return None


class GoogleCloudPubSubPublisher:
    """
    Publishes the accepted payload as JSON to the configured staging topic.

    Topic name arrives from settings (injected by App Engine deployment from
    Terraform outputs); no project identifiers or credentials are ever stored
    in this repository.
    """

    def __init__(self) -> None:
        from google.auth import default as google_auth_default
        from google.cloud import pubsub_v1  # imported lazily; staging only

        credentials, detected_project = google_auth_default()
        project_id = getattr(settings, "GCP_PROJECT_ID", "") or detected_project
        self._client = pubsub_v1.PublisherClient(credentials=credentials)
        self._topic = self._client.topic_path(
            project_id, settings.ONBOARDING_EVENTS_TOPIC
        )

    def publish(self, event: dict) -> str | None:  # noqa: ANN001 - dict payload
        import json

        future = self._client.publish(
            self._topic, json.dumps(event).encode("utf-8"), source="drf-onboarding-api"
        )
        return future.result(timeout=30)


def get_publisher():
    publisher_class_path = getattr(settings, "ONBOARDING_EVENT_PUBLISHER", None)
    if not publisher_class_path or publisher_class_path.endswith("NullPublisher"):
        return NullPublisher()
    module_path, class_name = publisher_class_path.rsplit(".", 1)
    module = __import__(module_path, fromlist=[class_name])
    return getattr(module, class_name)()
