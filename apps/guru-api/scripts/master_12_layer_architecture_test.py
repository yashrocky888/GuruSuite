#!/usr/bin/env python3

import requests
import re
import sys

API = "https://guru-api-660206747784.asia-south1.run.app/api/v1/predict"

FAILURES = []


def call_api(payload):
    r = requests.post(API, json=payload, timeout=60)
    r.raise_for_status()
    return r.json().get("guidance", "")


def assert_no_doctrine(text):
    forbidden = [
        "dusthana", "kendra", "trikona", "bindu",
        "shadbala", "low_bindu", "As lord of",
        "lordship function", "structural support"
    ]
    for f in forbidden:
        if f.lower() in text.lower():
            FAILURES.append(f"Doctrinal leak detected: {f}")


def assert_structure(text):
    required = [
        "CURRENT SKY POSITION",
        "PANCHANGA OF THE DAY",
        "DASHA AUTHORITY",
        "CHANDRA BALA",
        "TARA BALA",
        "MAJOR TRANSITS",
        "DHARMA GUIDANCE",
        "JANMA NAKSHATRA THRONE",
        "MOON MOVEMENT"
    ]
    for h in required:
        if h not in text:
            FAILURES.append(f"Missing section: {h}")


def assert_identity_anchor(text):
    first_lines = "\n".join(text.split("\n")[:5])
    if "I have" not in first_lines and "contemplated" not in first_lines:
        FAILURES.append("Identity anchor missing or weak")


def assert_no_gemstones(text):
    if any(x in text.lower() for x in ["ruby", "emerald", "sapphire", "diamond", "gemstone"]):
        FAILURES.append("Gemstone detected")


def assert_spiritual_limit(text):
    spiritual_terms = ["mantra", "fast", "lamp", "dana", "silence practice"]
    count = sum(text.lower().count(t) for t in spiritual_terms)
    if count > 1:
        FAILURES.append("More than one spiritual suggestion detected")


def assert_no_repetition(text):
    if text.count("Energy drains") > 2:
        FAILURES.append("Repetition creep: Energy drains")
    if text.count("What appears") > 2:
        FAILURES.append("Repetition creep: What appears")


def assert_closure_variation(text1, text2):
    closing1 = text1.strip().split("\n")[-2:]
    closing2 = text2.strip().split("\n")[-2:]
    if closing1 == closing2:
        FAILURES.append("Dynamic closure not varying")


# ------------------------------------------
# TEST CASE A — SUPPORTIVE DAY
# ------------------------------------------
payload_A = {
    "timescale": "daily",
    "calculation_date": "2026-02-12T12:00:00",
    "birth_details": {
        "name": "Yogesh",
        "dob": "1995-05-16",
        "time": "18:38",
        "lat": 12.9716,
        "lon": 77.5946,
        "timezone": "Asia/Kolkata"
    }
}

text_A = call_api(payload_A)

assert_structure(text_A)
assert_identity_anchor(text_A)
assert_no_doctrine(text_A)
assert_no_gemstones(text_A)
assert_no_repetition(text_A)

# ------------------------------------------
# TEST CASE B — MODERATE STRESS
# ------------------------------------------
payload_B = {
    "timescale": "daily",
    "calculation_date": "2026-02-15T12:00:00",
    "birth_details": {
        "name": "TestModerate",
        "dob": "1990-09-14",
        "time": "02:18",
        "lat": 12.9716,
        "lon": 77.5946,
        "timezone": "Asia/Kolkata"
    }
}

text_B = call_api(payload_B)

assert_no_gemstones(text_B)
if any(x in text_B.lower() for x in ["mantra", "fast", "lamp"]):
    FAILURES.append("Spiritual suggestion incorrectly triggered in moderate stress")

# ------------------------------------------
# TEST CASE C — SEVERE STRESS
# ------------------------------------------
payload_C = {
    "timescale": "daily",
    "calculation_date": "2026-02-08T12:00:00",
    "birth_details": {
        "name": "TestSevere",
        "dob": "1975-06-20",
        "time": "06:00",
        "lat": 12.9716,
        "lon": 77.5946,
        "timezone": "Asia/Kolkata"
    }
}

text_C = call_api(payload_C)

assert_spiritual_limit(text_C)
assert_no_gemstones(text_C)

# ------------------------------------------
# TEST CASE D — CLOSURE VARIATION
# ------------------------------------------
payload_D1 = payload_A
payload_D2 = {
    **payload_A,
    "calculation_date": "2026-02-13T12:00:00"
}

text_D1 = call_api(payload_D1)
text_D2 = call_api(payload_D2)

assert_closure_variation(text_D1, text_D2)

# ------------------------------------------

if FAILURES:
    print("\n❌ ARCHITECTURE VALIDATION FAILED\n")
    for f in FAILURES:
        print("-", f)
    sys.exit(1)
else:
    print("\n✅ ALL 12-LAYER ARCHITECTURE CHECKS PASSED\n")
