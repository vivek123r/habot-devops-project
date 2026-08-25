# -*- coding: utf-8 -*-
"""
Candidate : Vivek R
Contact   : vivekravi9496497657@gmail.com | +91 8590609366
Project   : HabotConnect Hiring Project 1.0
            Junior Cloud & DevOps Engineer (GCP / Django / React)
File      : onboarding/constants.py
Purpose   : THE single source of truth for every validation limit, choice
            set, error code prefix, and Decision Yes/No rule identifier.

          Why this file exists: the hiring scenario's root cause was a schema
          mismatch that broke downstream analytics. Drift between layers is a
          process smell - so the serializer validators, the standalone
          Decision Yes/No library, the model column limits, the BigQuery
          enforced table definition (terraform/modules/bigquery_staged), and
          the data/schema mapping workbook all quote these exact values.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Field length and format limits (exact, deterministic)
# ---------------------------------------------------------------------------

PARENT_FULL_NAME_MIN_LENGTH = 2
PARENT_FULL_NAME_MAX_LENGTH = 120
CHILD_FULL_NAME_MIN_LENGTH = 2
CHILD_FULL_NAME_MAX_LENGTH = 120
EMAIL_MAX_LENGTH = 254
SUPPORT_NEEDS_SUMMARY_MIN_LENGTH = 10
SUPPORT_NEEDS_SUMMARY_MAX_LENGTH = 1000

# International direct dialing format: plus sign, country code without a
# leading zero, seven to fifteen digits in total after the country code digit.
PHONE_PATTERN = r"^\+[1-9]\d{7,14}$"

# Names accept unicode letters with single spaces, hyphens, apostrophes, or
# periods between letter groups. Digits and symbols are never names.
NAME_PATTERN = r"^[^\W\d_]+(?:[ '.\-][^\W\d_]+)*$"

# ---------------------------------------------------------------------------
# Child age eligibility window, in completed years, at submission time.
# ASSUMPTION A-07 (docs/assumptions.md): HabotConnect matches Learning Support
# Assistants for children of early-childhood and school age; the inclusive
# window is fixed at two through eighteen completed years so the boundary is
# a mathematical fact rather than a judgment call.
# ---------------------------------------------------------------------------

CHILD_AGE_MIN_YEARS = 2
CHILD_AGE_MAX_YEARS = 18

# ---------------------------------------------------------------------------
# Closed set: primary learning difficulty categories.
# ASSUMPTION A-08: derived from the platform context sentence in the hiring
# document ("children with learning difficulties"); each value maps to one
# BigQuery clustered value, byte-for-byte identical.
# ---------------------------------------------------------------------------

CATEGORY_ADHD = "Attention Deficit Hyperactivity Disorder"
CATEGORY_AUTISM = "Autism Spectrum Disorder"
CATEGORY_DYSLEXIA = "Dyslexia"
CATEGORY_DYSGRAPHIA = "Dysgraphia"
CATEGORY_DYSCALCULIA = "Dyscalculia"
CATEGORY_SPEECH_LANGUAGE = "Speech and Language Impairment"
CATEGORY_OTHER = "Other Diagnosed Learning Difficulty"

LEARNING_DIFFICULTY_CATEGORIES: tuple[str, ...] = (
    CATEGORY_ADHD,
    CATEGORY_AUTISM,
    CATEGORY_DYSLEXIA,
    CATEGORY_DYSGRAPHIA,
    CATEGORY_DYSCALCULIA,
    CATEGORY_SPEECH_LANGUAGE,
    CATEGORY_OTHER,
)

# ---------------------------------------------------------------------------
# Decision Yes/No rule identifiers (stable, auditable, never renumbered)
# ---------------------------------------------------------------------------

RULE_R01_PARENT_FULL_NAME = "R01"
RULE_R02_PARENT_EMAIL = "R02"
RULE_R03_PARENT_PHONE = "R03"
RULE_R04_CHILD_FULL_NAME = "R04"
RULE_R05_CHILD_DATE_OF_BIRTH_FORMAT = "R05"
RULE_R06_CHILD_AGE_WINDOW = "R06"
RULE_R07_LEARNING_DIFFICULTY_CATEGORY = "R07"
RULE_R08_SUPPORT_NEEDS_SUMMARY = "R08"
RULE_R09_PARENTAL_CONSENT_TRUE = "R09"
RULE_R10_DATA_PROCESSING_CONSENT_TRUE = "R10"
RULE_R11_NO_UNKNOWN_FIELDS = "R11"
RULE_R12_EXACT_FIELD_TYPES = "R12"

ALL_RULE_IDS: tuple[str, ...] = (
    RULE_R01_PARENT_FULL_NAME,
    RULE_R02_PARENT_EMAIL,
    RULE_R03_PARENT_PHONE,
    RULE_R04_CHILD_FULL_NAME,
    RULE_R05_CHILD_DATE_OF_BIRTH_FORMAT,
    RULE_R06_CHILD_AGE_WINDOW,
    RULE_R07_LEARNING_DIFFICULTY_CATEGORY,
    RULE_R08_SUPPORT_NEEDS_SUMMARY,
    RULE_R09_PARENTAL_CONSENT_TRUE,
    RULE_R10_DATA_PROCESSING_CONSENT_TRUE,
    RULE_R11_NO_UNKNOWN_FIELDS,
    RULE_R12_EXACT_FIELD_TYPES,
)

# Binary outcomes - the entire library speaks exactly this vocabulary.
OUTCOME_YES = "YES"
OUTCOME_NO = "NO"
