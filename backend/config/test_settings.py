# -*- coding: utf-8 -*-
"""
Candidate : Vivek R
Contact   : vivekravi9496497657@gmail.com | +91 8590609366
Project   : HabotConnect Hiring Project 1.0
            Junior Cloud & DevOps Engineer (GCP / Django / React)
File      : config/test_settings.py
Purpose   : Test-only configuration shim.

          The production settings module refuses to boot without a real
          DJANGO_SECRET_KEY whenever DEBUG is disabled - exactly the fail-
          closed behavior wanted in staging. This shim seeds throwaway test
          values into the environment FIRST, then reuses the production
          settings unchanged, so tests always exercise the real contract.
"""

from __future__ import annotations

import os

os.environ.setdefault("DJANGO_DEBUG", "true")
os.environ.setdefault(
    "DJANGO_SECRET_KEY", "poka-yoke-ephemeral-0123456789-abcdefghijklmnopqrstuvwxyz"
)
os.environ.setdefault("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,testserver")

from config.settings import *  # noqa: E402,F403 - deliberate reuse of production settings
