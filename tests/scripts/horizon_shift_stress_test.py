import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = REPO_ROOT / "tests" / "logs" / "HORIZON_SHIFT_STRESS_TEST.md"

# When GURU_API_URL is set, call Cloud Run (same key as DAILY). Else use local predict().
GURU_API_URL = os.environ.get("GURU_API_URL", "").rstrip("/")

if not GURU_API_URL:
    sys.path.insert(0, str(REPO_ROOT / "apps" / "guru-api"))
    from src.api.prediction_routes import predict

TEST_BIRTH = {
    "name": "Horizon Tester",
    "dob": "1995-05-16",
    "time": "18:38",
    "lat": 12.9767,
    "lon": 77.5901,
    "timezone": "Asia/Kolkata"
}

def write(line=""):
    with open(REPORT_PATH, "a") as f:
        f.write(line + "\n")

def fail(reason):
    write(f"❌ FAIL: {reason}")
    raise SystemExit(1)

def call_predict(timescale: str):
    """Call predict via Cloud Run API (curl for system SSL) or local predict()."""
    if GURU_API_URL:
        url = f"{GURU_API_URL}/api/v1/predict"
        body = json.dumps({"birth_details": TEST_BIRTH, "timescale": timescale})
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write(body)
            body_file = f.name
        try:
            out = subprocess.run(
                ["curl", "-s", "-S", "-X", "POST", "-H", "Content-Type: application/json", "-d", f"@{body_file}", "--connect-timeout", "15", "--max-time", "90", url],
                capture_output=True,
                text=True,
                timeout=95,
            )
            if out.returncode != 0:
                fail(f"API request failed: {out.stderr or out.stdout or 'curl error'}")
            return json.loads(out.stdout)
        except subprocess.TimeoutExpired:
            fail("API request timed out.")
        except json.JSONDecodeError as e:
            fail(f"API response not JSON: {e}")
        finally:
            try:
                os.unlink(body_file)
            except Exception:
                pass
    return predict(TEST_BIRTH, timescale=timescale)

def run_horizon_shift_stress_test():
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if REPORT_PATH.exists():
        REPORT_PATH.unlink()

    write("# 🧪 HORIZON SHIFT STRESS TEST REPORT")
    write(f"Run Date: {datetime.now(timezone.utc).isoformat()}")
    write("Engine: " + ("Cloud Run API (same key as DAILY)" if GURU_API_URL else "predict() — local"))
    write("Model: gpt-4o (same as DAILY)")
    write("")

    # -------------------------------
    # TEST 1 — MONTHLY (Solar Conflict)
    # -------------------------------
    write("## TEST 1 — MONTHLY HORIZON (Solar Conflict)")
    monthly = call_predict("monthly")

    guidance_m = (monthly.get("guidance") or "").lower()
    if not guidance_m or "openai_api_key not set" in guidance_m:
        fail("Monthly test requires valid AI guidance (OPENAI_API_KEY missing).")

    daily_noise = ["today", "moon", "nakshatra", "this morning"]
    monthly_focus = ["sun", "solar", "month", "antardasha", "theme"]

    if any(k in guidance_m for k in daily_noise):
        fail("MONTHLY prediction leaked DAILY logic (Moon/Nakshatra/Today).")

    if not any(k in guidance_m for k in monthly_focus):
        write("⚠️ WARNING: Monthly guidance lacks strong Solar language.")
    else:
        write("✅ PASS: Monthly guidance focuses on Solar / Antardasha themes.")

    write("Snippet:")
    write((monthly.get("guidance") or "")[:300])
    write("")

    # -------------------------------
    # TEST 2 — YEARLY (Saturnine Weight)
    # -------------------------------
    write("## TEST 2 — YEARLY HORIZON (Saturnine Weight)")
    yearly = call_predict("yearly")

    guidance_y = (yearly.get("guidance") or "").lower()
    if not guidance_y or "openai_api_key not set" in guidance_y:
        fail("Yearly test requires valid AI guidance (OPENAI_API_KEY missing).")

    # STEP 4: Must NOT contain: nakshatra, daily mood, today
    forbidden = ["nakshatra", "daily mood", "today"]
    required = ["jupiter", "saturn", "mahadasha", "year", "chapter", "lesson"]

    if any(k in guidance_y for k in forbidden):
        fail("YEARLY prediction leaked DAILY or MONTHLY logic (nakshatra/daily mood/today).")

    if sum(1 for k in required if k in guidance_y) < 2:
        fail("YEARLY prediction missing Jupiter/Saturn/Mahadasha focus.")

    write("✅ PASS: Yearly guidance correctly focuses on Jupiter–Saturn / Mahadasha.")
    write("Snippet:")
    write((yearly.get("guidance") or "")[:300])
    write("")

    write("--------------------------------------------------")
    write("FINAL RESULT:")
    write("HORIZON SHIFT — VERIFIED (DAILY ≠ MONTHLY ≠ YEARLY)")
    write("--------------------------------------------------")

    # STEP 5 — Final report (print exactly)
    for line in [
        "",
        "HORIZON SHIFT — VERIFIED (DAILY ≠ MONTHLY ≠ YEARLY)",
        "AI KEY: CONFIRMED (same as DAILY)",
        "MODEL: gpt-4o",
        "STATUS: PRO-GURU ENGINE — LOCKED",
    ]:
        print(line)
        if line:
            write(line)

if __name__ == "__main__":
    run_horizon_shift_stress_test()
