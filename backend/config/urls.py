# -*- coding: utf-8 -*-
"""
Candidate : Vivek R
Contact   : vivekravi9496497657@gmail.com | +91 8590609366
Project   : HabotConnect Hiring Project 1.0
            Junior Cloud & DevOps Engineer (GCP / Django / React)
File      : config/urls.py
"""

from django.urls import include, path

urlpatterns = [
    path("api/v1/onboarding/", include("onboarding.urls")),
]
