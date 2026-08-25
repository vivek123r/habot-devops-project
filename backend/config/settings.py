# -*- coding: utf-8 -*-
"""
Candidate : Vivek R
Contact   : vivekravi9496497657@gmail.com | +91 8590609366
Project   : HabotConnect Hiring Project 1.0
            Junior Cloud & DevOps Engineer (GCP / Django / React)
File      : config/settings.py
Purpose   : Environment-driven configuration.

          Security posture (enforced, not aspirational):
            - No secret is ever stored in this repository. DJANGO_SECRET_KEY
              must be provided by the executing environment; the service
              refuses to boot without it whenever DEBUG is disabled.
            - DEBUG defaults to False and is opt-in per environment.
            - Transport and cookie hardening flags are unconditional in
              production mode so `manage.py check --deploy --fail-level
              WARNING` passes inside the Poka-Yoke pipeline.
            - Database credentials arrive exclusively through environment
              variables; staging additionally uses Identity and Access
              Management database authentication (no password exists).
"""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _env_bool(name: str, default: str = "False") -> bool:
    return os.environ.get(name, default).strip().lower() in {"1", "true", "yes", "on"}


def _env_list(name: str, default: str = "") -> list[str]:
    raw = os.environ.get(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


# ---------------------------------------------------------------------------
# Core switches
# ---------------------------------------------------------------------------

SECRET_KEY = (
    os.environ["DJANGO_SECRET_KEY"]
    if not _env_bool("DJANGO_DEBUG")
    else os.environ.get("DJANGO_SECRET_KEY", "insecure-development-only-key")
)

DEBUG = _env_bool("DJANGO_DEBUG")

ALLOWED_HOSTS = _env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")

CSRF_TRUSTED_ORIGINS = _env_list("DJANGO_CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "rest_framework",
    "onboarding",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": False,
        "OPTIONS": {"context_processors": []},
    }
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# Data stores - selected by environment, never hardcoded credentials
# ---------------------------------------------------------------------------

DATABASE_ENGINE = os.environ.get("DJANGO_DB_ENGINE", "django.db.backends.sqlite3")

if DATABASE_ENGINE == "django.db.backends.sqlite3":
    DATABASES = {
        "default": {
            "ENGINE": DATABASE_ENGINE,
            "NAME": os.environ.get("DJANGO_DB_NAME", str(BASE_DIR / "local.sqlite3")),
        }
    }
else:
    # Staging: private Cloud SQL PostgreSQL reached through the Serverless
    # VPC Access connector; Identity and Access Management authentication
    # means no password materializes anywhere.
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["DJANGO_DB_NAME"],
            "USER": os.environ["DJANGO_DB_USER"],
            "HOST": os.environ["DJANGO_DB_HOST"],
            "PORT": os.environ.get("DJANGO_DB_PORT", "5432"),
        }
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Rest Framework
# ---------------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    # Public form endpoint: authentication is intentionally absent, and
    # keeping these explicit prevents Rest Framework from importing
    # django.contrib.auth models this service does not install.
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    # Prevent Rest Framework from materializing Django AnonymousUser models
    # that this authentication-free service does not install.
    "UNAUTHENTICATED_USER": None,
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.AnonRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {
        "anon": os.environ.get("ONBOARDING_THROTTLE_RATE", "60/min")
    },
    "DEFAULT_THROTTLE_ANON_SCOPE": "anon",
}

# ---------------------------------------------------------------------------
# Onboarding application wiring
# ---------------------------------------------------------------------------

GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "")
ONBOARDING_EVENTS_TOPIC = os.environ.get(
    "ONBOARDING_EVENTS_TOPIC", "student-onboarding-events-staging"
)
ONBOARDING_EVENT_PUBLISHER = os.environ.get(
    "ONBOARDING_EVENT_PUBLISHER", "onboarding.publishers.NullPublisher"
)

# ---------------------------------------------------------------------------
# Internationalization and time - every timestamp is UTC for determinism
# ---------------------------------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static handling (App Engine serves these directly from app.yaml)
# ---------------------------------------------------------------------------

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# ---------------------------------------------------------------------------
# Transport security - active whenever DEBUG is off
# ---------------------------------------------------------------------------

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

# ---------------------------------------------------------------------------
# Logging - structured, no personal data
# ---------------------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
    },
}
