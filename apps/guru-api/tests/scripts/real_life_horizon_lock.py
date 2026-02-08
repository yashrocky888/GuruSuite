import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.jyotish.ai.guru_payload import build_guru_context

TARGET_DATE = datetime(2026, 5, 15, 12, 0, 0)

USER_PROFILE = {
    "name": "Yogesh",
    "dob": "1995-05-16",
    "time": "18:38",
    "lat": 12.9767,
    "lon": 77.5901,
    "timezone": "Asia/Kolkata"
}

# Repo root: apps/guru-api/tests/scripts -> 4 levels up
REPO_ROOT = Path(__file__).resolve().parents[4]
REPORT_FILE = str(REPO_ROOT / "tests" / "logs" / "REAL_LIFE_LOCK_REPORT.md")

def write(line):
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, "a") as f:
        f.write(line + "\n")
    print(line)

def run():
    if os.path.exists(REPORT_FILE):
        os.remove(REPORT_FILE)

    write("# 🔒 REAL LIFE HORIZON LOCK TEST")
    write("Target Date: 2026-05-15")
    write("User Lagna: Scorpio (Sign 7)")
    write("-" * 40)

    # MONTHLY TEST — SUN
    write("\n## TEST 1 — MONTHLY (Sun in Taurus → 7th House)")
    ctx_m = build_guru_context(USER_PROFILE, "monthly", TARGET_DATE)

    sun = ctx_m["transit"]["Sun"]
    write(f"Sun Sign Index: {sun['sign_index']} (Expected: 1 / Taurus)")
    write(f"Sun House from Lagna: {sun['house_from_lagna']} (Expected: 7)")

    sun_ok = sun["house_from_lagna"] == 7
    write("✅ PASS" if sun_ok else "❌ FAIL")

    # YEARLY TEST — JUPITER & SATURN
    write("\n## TEST 2 — YEARLY (Jupiter 8th, Saturn 5th)")
    ctx_y = build_guru_context(USER_PROFILE, "yearly", TARGET_DATE)

    j = ctx_y["transit"]["Jupiter"]
    s = ctx_y["transit"]["Saturn"]

    write(f"Jupiter Sign: {j['sign_index']} (Expected: 2 / Gemini)")
    write(f"Jupiter House: {j['house_from_lagna']} (Expected: 8)")

    write(f"Saturn Sign: {s['sign_index']} (Expected: 11 / Pisces)")
    write(f"Saturn House: {s['house_from_lagna']} (Expected: 5)")

    year_ok = j["house_from_lagna"] == 8 and s["house_from_lagna"] == 5
    write("✅ PASS" if year_ok else "❌ FAIL")

    write("\n" + "=" * 40)
    if sun_ok and year_ok:
        write("🟢 FINAL VERDICT: LOCKED — REAL ASTRONOMICAL DATA VERIFIED")
    else:
        write("🔴 FINAL VERDICT: UNLOCKED — LOGIC ERROR PRESENT")

if __name__ == "__main__":
    run()
