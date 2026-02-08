#!/usr/bin/env python3
"""
GURUSUITE — Master Test Case #4: AI Text + Daivajna Integrity.

Calls live /api/v1/predict, extracts backend truth, validates guidance text.
Writes AI output to ai_prediction_snapshot.txt for manual audit.
"""

import os
import re
import sys
from typing import Any, Dict

import requests

# ==========================================
# CONFIG
# ==========================================

API_URL = os.environ.get(
    "GURU_API_URL",
    "https://guru-api-660206747784.asia-south1.run.app/api/v1/predict",
)

PAYLOAD = {
    "timescale": "daily",
    "birth_details": {
        "name": "Daivajna Integrity Native",
        "dob": "1990-02-14",
        "time": "05:42",
        "lat": 28.6139,
        "lon": 77.2090,
        "timezone": "Asia/Kolkata",
    },
}

OUTPUT_FILE = "ai_prediction_snapshot.txt"

SIGN_NAMES = [
    "Aries (Mesha)",
    "Taurus (Vrishabha)",
    "Gemini (Mithuna)",
    "Cancer (Karka)",
    "Leo (Simha)",
    "Virgo (Kanya)",
    "Libra (Tula)",
    "Scorpio (Vrischika)",
    "Sagittarius (Dhanu)",
    "Capricorn (Makara)",
    "Aquarius (Kumbha)",
    "Pisces (Meena)",
]




def main() -> None:
    # ==========================================
    # STEP 1 — REAL API CALL
    # ==========================================
    try:
        response = requests.post(API_URL, json=PAYLOAD, timeout=120)
        response.raise_for_status()
    except Exception as e:
        print("API call failed:", e)
        sys.exit(1)

    data = response.json()
    guidance = data.get("guidance") or ""
    context = data.get("context") or {}

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(guidance)
    print("AI output stored in:", OUTPUT_FILE)

    # ==========================================
    # STEP 2 — BACKEND TRUTH EXTRACTION
    # ==========================================

    panchanga_raw = context.get("panchanga") or {}
    if isinstance(panchanga_raw, dict) and "panchanga" in panchanga_raw:
        panchanga_raw = panchanga_raw.get("panchanga") or panchanga_raw
    panchanga = panchanga_raw

    tithi_block = panchanga.get("tithi")
    tithi_name = None
    if isinstance(tithi_block, dict):
        current = tithi_block.get("current") or {}
        tithi_name = (current.get("name") if isinstance(current, dict) else None) or tithi_block.get("name")

    nak_block = panchanga.get("nakshatra")
    nakshatra_name = None
    if isinstance(nak_block, dict):
        nakshatra_name = nak_block.get("name") or (nak_block.get("current") or {}).get("name")

    transit = context.get("transit") or {}
    quality = context.get("quality") or {}
    time_block = context.get("time") or {}
    tara_bala = context.get("tara_bala") or {}
    janma = context.get("janma_nakshatra") or {}

    natal = context.get("natal") or {}
    natal_planets = natal.get("planets") or natal.get("planets_d1") or {}

    mahadasha = (time_block.get("mahadasha_lord") or "").strip()
    antardasha = (time_block.get("antardasha_lord") or "").strip()

    # ==========================================
    # STEP 3 — VALIDATION RULES
    # ==========================================

    errors: list[str] = []
    g = guidance.lower()

    # RULE 1 — Panchanga present in text
    if tithi_name and tithi_name.lower() not in g:
        errors.append("Panchanga Tithi missing in output.")
    if nakshatra_name and nakshatra_name.lower() not in g:
        errors.append("Panchanga Nakshatra missing in output.")

    # RULE 2 — Authority order (first "X currently transits" = Mahadasha Lord)
    first_transit_sentence = re.search(r"([A-Za-z]+)\s+currently\s+transits", guidance, re.IGNORECASE)
    if first_transit_sentence:
        first_planet = first_transit_sentence.group(1).strip()
        if mahadasha and first_planet.lower() != mahadasha.lower():
            errors.append("Authority violation: Mahadasha Lord not first.")
    else:
        if mahadasha and mahadasha.lower() not in g:
            errors.append("No transit sentence found or Mahadasha not referenced.")

    # RULE 3 — Sign & House correctness (each transit planet's sign and house appear in guidance)
    for planet, pdata in transit.items():
        if not isinstance(pdata, dict):
            continue
        sign_index = pdata.get("sign_index")
        house = pdata.get("transit_house") or pdata.get("house_from_lagna")
        if sign_index is None:
            continue
        correct_sign = SIGN_NAMES[sign_index % 12]
        sign_english = correct_sign.split("(")[0].strip()
        sign_sanskrit = (correct_sign.split("(")[1].replace(")", "").strip() if "(" in correct_sign else "")
        if correct_sign not in guidance and sign_english not in guidance and (not sign_sanskrit or sign_sanskrit not in guidance):
            errors.append(f"{planet} sign mismatch.")
        if house is not None:
            if house % 100 in (11, 12, 13):
                suf = "th"
            else:
                suf = {1: "st", 2: "nd", 3: "rd"}.get(house % 10, "th")
            house_phrase = f"{house}{suf} house"
            if house_phrase not in guidance and f"your {house} " not in g:
                errors.append(f"{planet} house mismatch.")

    # RULE 4 — Retrograde Lock (retrograde mentioned only if JSON has is_retrograde true for that planet)
    if "retrograde" in g or "vakri" in g:
        allowed_retro = set()
        for p, d in transit.items():
            if isinstance(d, dict) and d.get("is_retrograde") is True:
                allowed_retro.add(p.lower())
        for p, d in natal_planets.items():
            if isinstance(d, dict) and d.get("is_retrograde") is True:
                allowed_retro.add(p.lower())
        for shift in context.get("yearly_transits", []) + context.get("monthly_transits", []):
            if shift.get("is_retrograde"):
                allowed_retro.add((shift.get("planet") or "").lower())
        for planet in ["mercury", "venus", "mars", "jupiter", "saturn", "sun", "moon"]:
            if planet in allowed_retro:
                continue
            if re.search(rf"\b{planet}\b.*retrograde|retrograde.*\b{planet}\b", g):
                errors.append("Retrograde mentioned without JSON proof.")
                break

    # RULE 5 — Chandrashtama (8th from natal Moon → exact phrase)
    natal_moon_house = (natal_planets.get("Moon") or {}).get("house")
    moon_transit_data = transit.get("Moon") or {}
    transit_moon_house = moon_transit_data.get("transit_house") or moon_transit_data.get("house_from_lagna")

    if natal_moon_house is not None and transit_moon_house is not None:
        eighth_from_natal = ((natal_moon_house - 1 + 7) % 12) + 1
        if transit_moon_house == eighth_from_natal:
            if "Do not initiate major ventures today." not in guidance and "do not initiate major ventures today." not in g:
                errors.append("Chandrashtama warning missing.")

    # RULE 6 — Tara Bala tone override
    tara_category = (tara_bala.get("tara_category") or "").strip()
    if tara_category in ("Vipat", "Naidhana"):
        if "great opportunity" in g or "excellent day" in g:
            errors.append("Tara Bala override failure.")

    # RULE 7 — Nakshatra Throne integrity
    janma_name = (janma.get("name") or "").strip()
    if janma_name:
        if janma_name not in guidance and janma_name.lower() not in g:
            errors.append("Janma Nakshatra name missing.")
        if "you were born under" not in g:
            errors.append("Nakshatra throne block missing.")

    # ==========================================
    # FINAL RESULT
    # ==========================================

    if errors:
        print("❌ MASTER TEST CASE #4 FAILED")
        for e in errors:
            print(" -", e)
        sys.exit(1)

    print("✅ GURUSUITE — MASTER TEST CASE #4 PASSED (AI TEXT + DAIVAJNA VALIDATED)")


if __name__ == "__main__":
    main()
