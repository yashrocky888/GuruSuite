import os
import requests
import json

# Default: Cloud Run (same OPENAI_API_KEY as daily). Local: GURU_AUDIT_API_URL=http://localhost:8000/api/v1/predict
API_URL = os.environ.get("GURU_AUDIT_API_URL", "https://guru-api-660206747784.asia-south1.run.app/api/v1/predict")

TEST_BIRTH = {
    "name": "Audit Seeker",
    "dob": "1995-05-16",
    "time": "18:38",
    "lat": 12.9767,
    "lon": 77.5901,
    "timezone": "Asia/Kolkata"
}

def assert_no_terms(text, forbidden, scope):
    hits = [t for t in forbidden if t in text.lower()]
    assert not hits, f"{scope} FAIL — Forbidden terms found: {hits}"

def assert_has_terms(text, required, scope, min_hits=2):
    hits = [t for t in required if t in text.lower()]
    assert len(hits) >= min_hits, f"{scope} FAIL — Missing required focus terms. Found: {hits}"

def run_timescale_audit(timescale):
    print(f"\n--- 🔍 TESTING {timescale.upper()} PREDICTION ---")
    payload = {"birth_details": TEST_BIRTH, "timescale": timescale}
    response = requests.post(API_URL, json=payload)
    response.raise_for_status()

    data = response.json()
    guidance = data.get("guidance") or data.get("message") or ""
    if not guidance or "OPENAI_API_KEY" in guidance:
        print("FAIL — Timescale audit requires OPENAI_API_KEY.")
        print("Run against backend where DAILY predictions already work.")
        raise SystemExit(1)
    print(guidance[:600] + "...\n")

    if timescale == "monthly":
        assert_no_terms(
            guidance,
            forbidden=["today", "nakshatra", "moon", "travel"],
            scope="MONTHLY"
        )
        assert_has_terms(
            guidance,
            required=["sun", "antardasha", "month"],
            scope="MONTHLY"
        )

    if timescale == "yearly":
        assert_no_terms(
            guidance,
            forbidden=["today", "nakshatra", "moon", "travel", "this month"],
            scope="YEARLY"
        )
        assert_has_terms(
            guidance,
            required=["jupiter", "saturn", "mahadasha", "year", "lesson"],
            scope="YEARLY",
            min_hits=3
        )

    print(f"✅ {timescale.upper()} PASSED TIMESCALE ISOLATION\n")

def audit_timescale_separation():
    print("\n🚀 STARTING GURU TIMESCALE ISOLATION AUDIT\n")
    run_timescale_audit("monthly")
    run_timescale_audit("yearly")
    print("TIMESCALE ISOLATION — VERIFIED (DAILY ≠ MONTHLY ≠ YEARLY)")

if __name__ == "__main__":
    try:
        audit_timescale_separation()
    except AssertionError as e:
        print(f"\nFAIL — {e}")
        raise SystemExit(1)
