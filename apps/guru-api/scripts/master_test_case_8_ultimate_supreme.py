#!/usr/bin/env python3
"""
MASTER TEST CASE #8 — ULTIMATE SUPREME STRESS TEST (Cloud-only)

Validates: multi-planet retrograde, Chandrashtama, Tara Naidhana, Sade Sati,
Ashtama Saturn, low bindu stress, weak Mahadasha filter, authority order,
declaration integrity, retrograde proof, nakshatra throne, no fluff.
Cloud only. No local override. Do not modify API, prompts, backend, or validators.
"""

import re
import sys
from typing import Dict, Any, List

import requests

# Cloud only — DO NOT use GURU_API_URL override
API_URL = "https://guru-api-660206747784.asia-south1.run.app/api/v1/predict"

PAYLOAD = {
    "timescale": "daily",
    "birth_details": {
        "name": "Ultimate Stress Native",
        "dob": "1984-03-21",
        "time": "02:14",
        "lat": 28.6139,
        "lon": 77.2090,
        "timezone": "Asia/Kolkata",
    },
}

# Match backend SIGN_INDEX_TO_DISPLAY (0–11)
SIGN_INDEX_TO_DISPLAY = {
    0: "Aries (Mesha)",
    1: "Taurus (Vrishabha)",
    2: "Gemini (Mithuna)",
    3: "Cancer (Karka)",
    4: "Leo (Simha)",
    5: "Virgo (Kanya)",
    6: "Libra (Tula)",
    7: "Scorpio (Vrischika)",
    8: "Sagittarius (Dhanu)",
    9: "Capricorn (Makara)",
    10: "Aquarius (Kumbha)",
    11: "Pisces (Meena)",
}


def _house_ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        return f"{n}th"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def main() -> None:
    failures: List[str] = []

    print("Calling Cloud API...")
    try:
        r = requests.post(API_URL, json=PAYLOAD, timeout=90)
        r.raise_for_status()
    except Exception as e:
        print("API ERROR:", e)
        sys.exit(1)

    data = r.json()
    guidance = data.get("guidance", "")
    context = data.get("context", {})

    transit = context.get("transit") or {}
    natal = context.get("natal") or {}
    natal_planets = natal.get("planets") or natal.get("planets_d1") or {}
    janma = context.get("janma_nakshatra") or {}
    tara_bala = context.get("tara_bala") or {}
    panchanga_raw = context.get("panchanga") or {}
    if isinstance(panchanga_raw, dict) and panchanga_raw.get("panchanga"):
        panchanga_raw = panchanga_raw.get("panchanga") or panchanga_raw
    panchanga = panchanga_raw
    time_block = context.get("time") or {}
    quality = context.get("quality") or {}
    yearly = context.get("yearly_transits") or []
    monthly = context.get("monthly_transits") or []

    g = guidance.lower()

    # -------------------------------------------------------------------------
    # RULE 1 — Panchanga presence (tithi and nakshatra must appear in guidance)
    # -------------------------------------------------------------------------
    if isinstance(panchanga, dict):
        tithi_obj = panchanga.get("tithi")
        tithi_name = None
        if isinstance(tithi_obj, dict):
            cur = tithi_obj.get("current") or {}
            tithi_name = (cur.get("name") if isinstance(cur, dict) else None) or tithi_obj.get("name")
        elif isinstance(tithi_obj, str):
            tithi_name = tithi_obj
        nak_obj = panchanga.get("nakshatra")
        nak_name = (nak_obj.get("name") if isinstance(nak_obj, dict) else None) or (nak_obj if isinstance(nak_obj, str) else None)
        if tithi_name and tithi_name.lower() not in g:
            failures.append("FAIL_PANCHANGA_TITHI")
        if nak_name and nak_name.lower() not in g:
            failures.append("FAIL_PANCHANGA_NAKSHATRA")

    # -------------------------------------------------------------------------
    # RULE 2 — Authority order (first "currently transits" sentence MUST contain Mahadasha Lord)
    # -------------------------------------------------------------------------
    mahadasha = (time_block.get("mahadasha_lord") or "").strip()
    match = re.search(r"([A-Za-z]+)\s+currently\s+transits", guidance, re.IGNORECASE)
    if match:
        first_planet = match.group(1).strip().lower()
        if mahadasha and first_planet != mahadasha.lower():
            failures.append("FAIL_MAHADASHA_ORDER")
    else:
        failures.append("FAIL_MAHADASHA_ORDER")

    # -------------------------------------------------------------------------
    # RULE 3 — Planetary declaration lock: exact pattern "{Planet} currently transits {Sign} in your {N}th house."
    # -------------------------------------------------------------------------
    for planet, pdata in transit.items():
        if not isinstance(pdata, dict):
            continue
        sign_index = pdata.get("sign_index")
        house = pdata.get("transit_house") or pdata.get("house_from_lagna")
        if sign_index is None or house is None:
            continue
        sign_display = SIGN_INDEX_TO_DISPLAY.get(sign_index % 12, "")
        if not sign_display:
            continue
        sign_en = sign_display.split(" ")[0]
        house_ord = _house_ordinal(house)
        # Exact pattern: Planet currently transits ... in your Nth house. (Sign must match SIGN_INDEX_TO_DISPLAY, house must match transit_house)
        decl_pat = re.compile(
            re.escape(planet) + r"\s+currently\s+transits\s+.+?\s+in\s+your\s+" + re.escape(house_ord) + r"\s+house\.(?:\s*\(Retrograde\))?",
            re.IGNORECASE,
        )
        mo = decl_pat.search(guidance)
        if not mo:
            failures.append(f"FAIL_DECLARATION_{planet}")
            continue
        # Sign must appear in guidance (declaration uses full sign_display e.g. "Aries (Mesha)")
        if sign_en.lower() not in g and (len(sign_display.split()) > 1 and sign_display.split(" ")[1].strip("()").lower() not in g):
            failures.append(f"FAIL_DECLARATION_{planet}")

    # -------------------------------------------------------------------------
    # RULE 4 — Retrograde proof (allowed_retro from transit + natal + shifts)
    # -------------------------------------------------------------------------
    allowed_retro = set()
    for p, pdata in transit.items():
        if isinstance(pdata, dict) and pdata.get("is_retrograde") is True:
            allowed_retro.add((p or "").lower())
    for p, pdata in natal_planets.items():
        if isinstance(pdata, dict) and pdata.get("is_retrograde") is True:
            allowed_retro.add((p or "").lower())
    for shift in yearly + monthly:
        if shift.get("is_retrograde"):
            allowed_retro.add((shift.get("planet") or "").lower())

    _decl_re = re.compile(
        r"^\s*(?:\s*\(Retrograde\)\s*\n?)?"
        r"(Mercury|Venus|Mars|Jupiter|Saturn|Sun|Moon)\s+currently\s+transits\s+.+?\s+in\s+your\s+\d+(?:st|nd|rd|th)\s+house\.?(?:\s*\(Retrograde\))?\s*$",
        re.IGNORECASE | re.DOTALL,
    )
    for sentence in re.split(r"(?<=[.!?])\s+(?!\s*\(Retrograde\))", guidance):
        sent = sentence.strip()
        if not sent or len(sent) < 5:
            continue
        if _decl_re.match(sent):
            continue
        lower = sent.lower()
        if "retrograde" not in lower and "vakri" not in lower:
            continue
        planet_found = None
        for p in transit.keys():
            if p.lower() in lower:
                planet_found = p.lower()
                break
        if planet_found is not None and planet_found not in allowed_retro:
            failures.append(f"FAIL_RETROGRADE_{planet_found}")

    # -------------------------------------------------------------------------
    # RULE 5 — Chandrashtama (transit Moon 8th from natal Moon → exact sentence)
    # -------------------------------------------------------------------------
    natal_moon_house = (natal_planets.get("Moon") or {}).get("house") if isinstance(natal_planets.get("Moon"), dict) else None
    transit_moon = transit.get("Moon") or {}
    transit_moon_house = (transit_moon.get("transit_house") or transit_moon.get("house_from_lagna")) if isinstance(transit_moon, dict) else None
    if natal_moon_house is not None and transit_moon_house is not None:
        eighth_from_moon = ((natal_moon_house - 1 + 7) % 12) + 1
        if transit_moon_house == eighth_from_moon:
            if "do not initiate major ventures today" not in g:
                failures.append("FAIL_CHANDRASHTAMA")

    # -------------------------------------------------------------------------
    # RULE 6 — Tara Naidhana override (no positive fluff when Vipat/Naidhana)
    # -------------------------------------------------------------------------
    tara_cat = (tara_bala.get("tara_category") or "").strip()
    if tara_cat in ["Vipat", "Naidhana"]:
        for phrase in ["great opportunity", "excellent day", "success likely", "unlimited success"]:
            if phrase in g:
                failures.append("FAIL_TARA_OVERRIDE")
                break

    # -------------------------------------------------------------------------
    # RULE 7 — Sade Sati / Ashtama Saturn
    # -------------------------------------------------------------------------
    natal_moon_h = (natal_planets.get("Moon") or {}).get("house") if isinstance(natal_planets.get("Moon"), dict) else None
    saturn_data = transit.get("Saturn") or {}
    saturn_house = (saturn_data.get("transit_house") or saturn_data.get("house_from_lagna")) if isinstance(saturn_data, dict) else None
    if natal_moon_h is not None and saturn_house is not None:
        pos_from_moon = (saturn_house - natal_moon_h) % 12 or 12
        if pos_from_moon in (12, 1, 2):
            if "pressure" not in g and "discipline" not in g:
                failures.append("FAIL_SATURN_POSITION")
        elif pos_from_moon == 8:
            if "discipline phase" not in g and "restriction" not in g:
                failures.append("FAIL_SATURN_POSITION")

    # -------------------------------------------------------------------------
    # RULE 8 — Low bindu stress (any transit planet with bindu <= 1)
    # -------------------------------------------------------------------------
    stress_words = ["effort", "strain", "pressure", "discipline", "delay"]
    transit_planets_low_bindu = []
    for planet in transit:
        qdata = quality.get(planet) if isinstance(quality, dict) else {}
        if isinstance(qdata, dict):
            bindu = qdata.get("bindu")
            if bindu is not None and bindu <= 1:
                transit_planets_low_bindu.append(planet)
    if transit_planets_low_bindu and not any(w in g for w in stress_words):
        failures.append("FAIL_BINDU_STRESS")

    # -------------------------------------------------------------------------
    # RULE 9 — Weak Mahadasha filter (MD lord bindu <= 1 → no "major success" / "strong expansion")
    # -------------------------------------------------------------------------
    maha_lord = (time_block.get("mahadasha_lord") or "").strip()
    if maha_lord and isinstance(quality, dict) and maha_lord in quality:
        qdata = quality.get(maha_lord)
        if isinstance(qdata, dict):
            maha_bindu = qdata.get("bindu")
            if maha_bindu is not None and maha_bindu <= 1:
                if "major success" in g or "strong expansion" in g:
                    failures.append("FAIL_DASHA_FILTER")

    # -------------------------------------------------------------------------
    # RULE 10 — Nakshatra throne block
    # -------------------------------------------------------------------------
    if "you were born under" not in g:
        failures.append("FAIL_NAKSHATRA_THRONE")
    else:
        janma_name = (janma.get("name") or "").strip().lower()
        any_in_same_nak = False
        for planet, pdata in transit.items():
            if not isinstance(pdata, dict):
                continue
            pnak = (pdata.get("nakshatra") or pdata.get("nakshatra_name") or "").strip().lower()
            if janma_name and pnak and janma_name == pnak:
                any_in_same_nak = True
                break
        if not any_in_same_nak and "today, no transit planet activates your throne" not in g:
            failures.append("FAIL_NAKSHATRA_THRONE")

    # -------------------------------------------------------------------------
    # RULE 11 — No fluff language
    # -------------------------------------------------------------------------
    fluff = ["amazing day", "fantastic", "incredible", "life-changing", "magic energy", "positive vibes"]
    for phrase in fluff:
        if phrase in g:
            failures.append("FAIL_FLUFF_LANGUAGE")
            break

    # -------------------------------------------------------------------------
    # Output
    # -------------------------------------------------------------------------
    if failures:
        print("FAILED RULES:")
        for f in failures:
            print("-", f)
        print("\nFirst 1000 chars of guidance:\n")
        print(guidance[:1000])
        sys.exit(1)

    print("GURUSUITE — MASTER TEST CASE #8 PASSED (Ultimate Supreme Integrity)")
    sys.exit(0)


if __name__ == "__main__":
    main()
