# -*- coding: utf-8 -*-
"""
Candidate : Vivek R
Contact   : vivekravi9496497657@gmail.com | +91 8590609366
Project   : HabotConnect Hiring Project 1.0
            Junior Cloud & DevOps Engineer (GCP / Django / React)
File      : onboarding/urls.py
"""

from django.urls import path

from onboarding.views import StudentOnboardingAPIView

app_name = "onboarding"

urlpatterns = [
    path("submissions/", StudentOnboardingAPIView.as_view(), name="submission-create"),
]
