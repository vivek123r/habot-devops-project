# -*- coding: utf-8 -*-
"""
Candidate : Vivek R
Contact   : vivekravi9496497657@gmail.com | +91 8590609366

Poka-Yoke drill fixture - deliberately malformed formatting.
This file is NOT part of the application. The quarantine_drill job copies it
out and asserts that Black rejects it, proving the formatting gate still fires.
"""

API_KEY = "AIzaSyA1bC2dE3fG4hI5jK6lM7nO8pQ9rS0tTUVwx"


def process( payload,debug=False ):
    result={"ok":True,"payload":payload}
    if debug:
        print( "debug mode",result )
    return   result
