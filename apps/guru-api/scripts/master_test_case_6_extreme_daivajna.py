#!/usr/bin/env python3
"""
MASTER TEST CASE #6 — Extreme Supreme Daivajna Integrity Validation

Validates:
- Panchanga presence (tithi, nakshatra)
- Mahadasha first (before first "currently transits")
- Chandrashtama hard lock (exact sentence)
- Tara Bala override (Vipat/Naidhana)
- Retrograde proof (only when JSON allows)
- Sign/House lock (backend declarations)
- Nakshatra throne ("You were born under")

If ANY rule fails → exit 1.
If ALL pass → print pass message.
"""

import os
import re
import sys
from typing import List

import requests

API_URL = os.getenv(
    "GURU_API_URL",
    "https://guru-api-660206747784.asia-south1.run.app/api/v1/predict",
)

PAYLOAD = {
    "timescale": "daily",
    "birth_details": {
        "name": "Extreme Karma Native",
        "dob": "1984-10-21",
        "time": "03:18",
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
        response = requests.post(API_URL, json=PAYLOAD, timeout=60)
        response.raise_for_status()
    except Exception as e:
        print("API ERROR:", e)
        sys.exit(1)

    data = response.json()
    guidance = data.get("guidance", "")
    context = data.get("context", {})
    g = guidance.lower()

    print("\n--- VALIDATION START ---\n")

    # Resolve nested panchanga (same as test 5)
    panchanga_raw = context.get("panchanga") or {}
    if isinstance(panchanga_raw, dict) and "panchanga" in panchanga_raw:
        panchanga_raw = panchanga_raw.get("panchanga") or panchanga_raw
    panchanga = panchanga_raw

    # -----------------------------------
    # RULE 1 — Panchanga Presence
    # -----------------------------------
    if panchanga:
        tithi = panchanga.get("tithi") or {}
        tithi_current = tithi.get("current") if isinstance(tithi, dict) else {}
        tithi_name = (tithi_current.get("name") if isinstance(tithi_current, dict) else None) or (tithi.get("name") if isinstance(tithi, dict) else None)
        nak = panchanga.get("nakshatra")
        nak_name = nak.get("name") if isinstance(nak, dict) else None

        if tithi_name and tithi_name.lower() not in g:
            fail("PANCHANGA_TITHI_MISSING")
        if nak_name and nak_name.lower() not in g:
            fail("PANCHANGA_NAKSHATRA_MISSING")

    # -----------------------------------
    # RULE 2 — Mahadasha First
    # -----------------------------------
    time_block = context.get("time") or {}
    maha = (time_block.get("mahadasha_lord") or "").strip()

    if maha:
        first_transit_index = g.find("currently transits")
        maha_index = g.find(maha.lower())

        if maha_index == -1:
            fail("MAHADASHA_NOT_MENTIONED")
        elif first_transit_index != -1 and maha_index > first_transit_index:
            fail("MAHADASHA_NOT_FIRST")

    # -----------------------------------
    # RULE 3 — Chandrashtama Hard Lock
    # -----------------------------------
    natal_planets = (context.get("natal") or {}).get("planets") or (context.get("natal") or {}).get("planets_d1") or {}
    natal_moon_house = (natal_planets.get("Moon") or {}).get("house") if isinstance(natal_planets.get("Moon"), dict) else None
    transit = context.get("transit") or {}
    transit_moon = transit.get("Moon") or {}
    transit_moon_house = (transit_moon.get("transit_house") or transit_moon.get("house_from_lagna")) if isinstance(transit_moon, dict) else None

    if natal_moon_house is not None and transit_moon_house is not None:
        eighth_from_natal = ((natal_moon_house - 1 + 7) % 12) + 1
        if transit_moon_house == eighth_from_natal:
            if "Do not initiate major ventures today." not in guidance and "do not initiate major ventures today." not in g:
                fail("CHANDRASHTAMA_SENTENCE_MISSING")

    # -----------------------------------
    # RULE 4 — Tara Bala Override
    # -----------------------------------
    tara = (context.get("tara_bala") or {}).get("tara_category") or ""
    if isinstance(tara, str) and tara.strip() in ["Vipat", "Naidhana"]:
        if "great opportunity" in g:
            fail("TARA_OVERRIDE_FAILED")

    # -----------------------------------
    # RULE 5 — Retrograde Proof (align with test 5: transit + natal + shifts; skip declaration sentences)
    # -----------------------------------
    allowed_retro = set()
    for p, v in transit.items():
        if isinstance(v, dict) and v.get("is_retrograde") is True:
            allowed_retro.add((p or "").lower())
    for p, v in (natal_planets or {}).items():
        if isinstance(v, dict) and v.get("is_retrograde") is True:
            allowed_retro.add((p or "").lower())
    for shift in context.get("yearly_transits", []) + context.get("monthly_transits", []):
        if shift.get("is_retrograde"):
            allowed_retro.add((shift.get("planet") or "").lower())

    _decl_re = re.compile(
        r"^\s*(?:\s*\(Retrograde\)\s*)?"
        r"(Mercury|Venus|Mars|Jupiter|Saturn|Sun|Moon)\s+currently\s+transits\s+.+?\s+in\s+your\s+\d+(?:st|nd|rd|th)\s+house\.(?:\s*\(Retrograde\))?\s*$",
        re.IGNORECASE,
    )

    sentences = re.split(r"(?<=[.!?])\s+", guidance)
    for sent in sentences:
        sent_stripped = sent.strip()
        if not sent_stripped or len(sent_stripped) < 5:
            continue
        if _decl_re.match(sent_stripped):
            continue
        sent_lower = sent_stripped.lower()
        if "retrograde" not in sent_lower and "vakri" not in sent_lower:
            continue
        planet_found = False
        for planet in ["mercury", "venus", "mars", "jupiter", "saturn", "sun", "moon"]:
            if re.search(rf"\b{planet}\b", sent_lower):
                planet_found = True
                if planet not in allowed_retro:
                    fail(f"RETROGRADE_WITHOUT_PROOF_{planet.title()}")
                break
        if not planet_found and len(sent_stripped) > 20:
            fail("RETROGRADE_NO_PLANET_CONTEXT")

    # -----------------------------------
    # RULE 6 — Sign/House Lock
    # -----------------------------------
    SIGN_NAMES = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo",
        "Virgo", "Libra", "Scorpio", "Sagittarius",
        "Capricorn", "Aquarius", "Pisces",
    ]
    SIGN_SANSKRIT = [
        "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha",
        "Kanya", "Tula", "Vrischika", "Dhanu",
        "Makara", "Kumbha", "Meena",
    ]

    for planet, pdata in (transit or {}).items():
        if not isinstance(pdata, dict):
            continue
        sign_index = pdata.get("sign_index")
        house = pdata.get("transit_house") or pdata.get("house_from_lagna")

        if sign_index is None or house is None:
            continue

        expected_sign = SIGN_NAMES[sign_index % 12]
        sign_sk = SIGN_SANSKRIT[sign_index % 12] if sign_index is not None else ""
        if expected_sign not in guidance and (not sign_sk or sign_sk not in guidance):
            fail(f"SIGN_MISMATCH_{planet}")

        if 11 <= house % 100 <= 13:
            suf = "th"
        else:
            suf = {1: "st", 2: "nd", 3: "rd"}.get(house % 10, "th")
        house_phrase = f"{house}{suf} house"
        if house_phrase not in guidance and f"your {house} " not in g:
            fail(f"HOUSE_MISMATCH_{planet}")

    # -----------------------------------
    # RULE 7 — Nakshatra Throne Block
    # -----------------------------------
    janma = context.get("janma_nakshatra") or {}
    if janma and (janma.get("name") or janma.get("pada") is not None):
        if "you were born under" not in g:
            fail("NAKSHATRA_THRONE_MISSING")

    # -----------------------------------
    # FINAL RESULT
    # -----------------------------------
    if FAILURES:
        print("FAILED RULES:")
        for f in FAILURES:
            print("-", f)
        print("\n--- FIRST 800 CHARS OF GUIDANCE ---\n")
        print(guidance[:800])
        sys.exit(1)

    print("GURUSUITE — MASTER TEST CASE #6 PASSED (Extreme Supreme Integrity)")
    sys.exit(0)


if __name__ == "__main__":
    main()
