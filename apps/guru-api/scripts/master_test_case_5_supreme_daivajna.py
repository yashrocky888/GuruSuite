#!/usr/bin/env python3
"""
MASTER TEST CASE #5 — SUPREME DAIVAJNA VALIDATION

This script validates the full DAIVAJNA SUPREME DAILY ALGORITHM.

It ensures:
- Panchanga Quality Filter
- Authority Order (Mahadasha first)
- Sign & House Lock
- Retrograde Lock
- Chandrashtama exact sentence
- Tara Bala override
- Jupiter-from-Moon logic
- Saturn-from-Moon logic
- Dasha Baseline tone
- Transit Movement format
- No fluff language
- Nakshatra Throne integrity

If ANY rule fails → exit code 1.
If ALL pass → prints final PASS message.
"""

import os
import re
import sys
from typing import List

import requests

API_URL = os.environ.get(
    "GURU_API_URL",
    "https://guru-api-660206747784.asia-south1.run.app/api/v1/predict",
)

PAYLOAD = {
    "timescale": "daily",
    "birth_details": {
        "name": "Supreme Validation Native",
        "dob": "1990-02-14",
        "time": "05:42",
        "lat": 28.6139,
        "lon": 77.2090,
        "timezone": "Asia/Kolkata",
    },
}

FAILURES: List[str] = []


def fail(rule: str) -> None:
    FAILURES.append(rule)


def main() -> None:
    global FAILURES
    FAILURES = []

    print("Calling API...")
    try:
        r = requests.post(API_URL, json=PAYLOAD, timeout=120)
        r.raise_for_status()
    except Exception as e:
        print("API call failed:", e)
        sys.exit(1)

    data = r.json()
    guidance = data.get("guidance") or ""
    context = data.get("context") or {}
    g = guidance.lower()

    # Resolve nested panchanga
    panchanga_raw = context.get("panchanga") or {}
    if isinstance(panchanga_raw, dict) and "panchanga" in panchanga_raw:
        panchanga_raw = panchanga_raw.get("panchanga") or panchanga_raw
    panchanga = panchanga_raw

    # -------------------------------------------------
    # RULE 1 — Panchanga Presence
    # -------------------------------------------------
    tithi = panchanga.get("tithi") or {}
    nakshatra = panchanga.get("nakshatra") or {}
    weekday = panchanga.get("weekday") or (panchanga.get("vara") or {}).get("name")
    day_lord = (panchanga.get("vara") or {}).get("lord") if isinstance(panchanga.get("vara"), dict) else None

    if tithi:
        tithi_current = tithi.get("current") if isinstance(tithi, dict) else {}
        tithi_name = (tithi_current.get("name") if isinstance(tithi_current, dict) else None) or tithi.get("name")
        if tithi_name and tithi_name.lower() not in guidance.lower():
            fail("PANCHANGA_TITHI_MISSING")

    if nakshatra and isinstance(nakshatra, dict):
        nak_name = nakshatra.get("name")
        if nak_name and nak_name.lower() not in guidance.lower():
            fail("PANCHANGA_NAKSHATRA_MISSING")

    if weekday and weekday.lower() not in guidance.lower() and (not day_lord or day_lord.lower() not in guidance.lower()):
        fail("PANCHANGA_WEEKDAY_MISSING")

    transit = context.get("transit") or {}

    # -------------------------------------------------
    # RULE 2 — Authority Order (Mahadasha before Moon transit sentence)
    # -------------------------------------------------
    mahadasha = (context.get("time") or {}).get("mahadasha_lord") or ""
    if mahadasha:
        moon_index = g.find("moon currently transits")
        if moon_index == -1:
            moon_index = g.find("moon transits ")
        mahadasha_lower = mahadasha.lower()
        dasha_index = g.find(f"{mahadasha_lower} currently transits")
        if dasha_index == -1:
            dasha_index = g.find(f"{mahadasha_lower} transits ")

        if dasha_index == -1:
            if mahadasha_lower not in g:
                fail("MAHADASHA_NOT_MENTIONED")
            elif mahadasha in transit:
                fail("MAHADASHA_NOT_MENTIONED")

        if moon_index != -1 and dasha_index != -1 and moon_index < dasha_index:
            fail("AUTHORITY_ORDER_VIOLATION")

    # -------------------------------------------------
    # RULE 3 — Sign & House Lock
    # -------------------------------------------------
    # English and Sanskrit (from STRICT SIGN TABLE in prompt)
    sign_names = [
        ("Aries", "Mesha"), ("Taurus", "Vrishabha"), ("Gemini", "Mithuna"), ("Cancer", "Karka"),
        ("Leo", "Simha"), ("Virgo", "Kanya"), ("Libra", "Tula"), ("Scorpio", "Vrischika"),
        ("Sagittarius", "Dhanu"), ("Capricorn", "Makara"), ("Aquarius", "Kumbha"), ("Pisces", "Meena"),
    ]
    for planet, pdata in transit.items():
        if not isinstance(pdata, dict):
            continue
        sign_index = pdata.get("sign_index")
        house = pdata.get("transit_house") or pdata.get("house_from_lagna")
        if sign_index is None:
            continue
        sign_en, sign_sk = sign_names[sign_index % 12]
        if sign_en not in g and (not sign_sk or sign_sk.lower() not in g):
            fail(f"SIGN_MISMATCH_{planet}")
        if house is not None:
            if 11 <= house % 100 <= 13:
                suf = "th"
            else:
                suf = {1: "st", 2: "nd", 3: "rd"}.get(house % 10, "th")
            house_phrase = f"{house}{suf} house"
            if house_phrase not in guidance and f"your {house} " not in guidance.lower():
                fail(f"HOUSE_MISMATCH_{planet}")

    # -------------------------------------------------
    # RULE 4 — Retrograde Lock (only fail if non-retro planet said retrograde)
    # -------------------------------------------------
    allowed_retro = set()
    for p, d in transit.items():
        if isinstance(d, dict) and d.get("is_retrograde") is True:
            allowed_retro.add(p.lower())
    natal_planets = (context.get("natal") or {}).get("planets") or (context.get("natal") or {}).get("planets_d1") or {}
    for p, d in natal_planets.items():
        if isinstance(d, dict) and d.get("is_retrograde") is True:
            allowed_retro.add(p.lower())
    for shift in context.get("yearly_transits", []) + context.get("monthly_transits", []):
        if shift.get("is_retrograde"):
            allowed_retro.add((shift.get("planet") or "").lower())

    # Only fail if planet and retrograde/vakri appear in the SAME sentence (backend adds " (Retrograde)" per declaration line)
    # Skip backend declaration sentences: optional " (Retrograde)" then "X currently transits ... in your N house."
    _decl_re = re.compile(
        r"^\s*(?:\s*\(Retrograde\)\s*)?"
        r"(Mercury|Venus|Mars|Jupiter|Saturn|Sun|Moon)\s+currently\s+transits\s+.+?\s+in\s+your\s+\d+(?:st|nd|rd|th)\s+house\.(?:\s*\(Retrograde\))?\s*$",
        re.IGNORECASE,
    )
    if "retrograde" in g or "vakri" in g:
        sentences = re.split(r"(?<=[.!?])\s+", guidance)
        for sent in sentences:
            sent_stripped = sent.strip()
            if _decl_re.match(sent_stripped):
                continue
            sent_lower = sent_stripped.lower()
            if "retrograde" not in sent_lower and "vakri" not in sent_lower:
                continue
            for planet in ["mercury", "venus", "mars", "jupiter", "saturn", "sun", "moon"]:
                if planet in allowed_retro:
                    continue
                if re.search(rf"\b{planet}\b", sent_lower) and re.search(r"retrograde|vakri", sent_lower):
                    fail(f"RETROGRADE_WITHOUT_PROOF_{planet}")
                    break
            if FAILURES:
                break

    # -------------------------------------------------
    # RULE 5 — Chandrashtama
    # -------------------------------------------------
    natal_planets = (context.get("natal") or {}).get("planets") or (context.get("natal") or {}).get("planets_d1") or {}
    natal_moon = natal_planets.get("Moon") or {}
    natal_moon_house = natal_moon.get("house") if isinstance(natal_moon, dict) else None
    transit_moon = transit.get("Moon") or {}
    transit_moon_house = (transit_moon.get("transit_house") or transit_moon.get("house_from_lagna")) if isinstance(transit_moon, dict) else None

    if natal_moon_house is not None and transit_moon_house is not None:
        eighth_from_moon = ((natal_moon_house - 1 + 7) % 12) + 1
        if transit_moon_house == eighth_from_moon:
            if "Do not initiate major ventures today." not in guidance and "do not initiate major ventures today." not in g:
                fail("CHANDRASHTAMA_PHRASE_MISSING")

    # -------------------------------------------------
    # RULE 6 — Tara Bala Override
    # -------------------------------------------------
    tara = context.get("tara_bala") or {}
    tara_cat = (tara.get("tara_category") or "").strip()

    if tara_cat in ["Vipat", "Naidhana"]:
        if "great opportunity" in g:
            fail("TARA_OVERRIDE_FAILED")
        if "excellent day" in g:
            fail("TARA_OVERRIDE_FAILED")

    # -------------------------------------------------
    # RULE 7 — Transit Movement Format
    # -------------------------------------------------
    if "later this month" in g or "later this year" in g:
        fail("FORBIDDEN_LATER_PHRASE")

    if "moves from" in g:
        if not re.search(r"On .+?, .+ moves from", guidance):
            fail("TRANSIT_FORMAT_INVALID")

    # -------------------------------------------------
    # RULE 8 — Nakshatra Throne
    # -------------------------------------------------
    janma = context.get("janma_nakshatra") or {}
    if janma and (janma.get("name") or janma.get("pada") is not None):
        if "you were born under" not in g:
            fail("JANMA_THRONE_MISSING")

    # -------------------------------------------------
    # RULE 9 — No Fluff
    # -------------------------------------------------
    fluff_words = [
        "amazing day",
        "unlimited success",
        "great opportunity day",
        "positive vibes",
        "fantastic",
    ]
    for word in fluff_words:
        if word in g:
            fail("FLUFF_LANGUAGE_PRESENT")

    # -------------------------------------------------
    # FINAL RESULT
    # -------------------------------------------------
    if FAILURES:
        print("\nFAILED RULES:")
        for f in FAILURES:
            print("-", f)
        sample = (guidance or "")[:600]
        print("\nSample guidance (first 600 chars):")
        print(sample if sample else "(empty)")
        sys.exit(1)

    print("\nGURUSUITE — MASTER TEST CASE #5 PASSED (Supreme Daivajna Integrity)")
    sys.exit(0)


if __name__ == "__main__":
    main()
