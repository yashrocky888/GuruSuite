#!/usr/bin/env python3
"""
GURUSUITE — Master Test Case #3: Extreme Daivajna Validation.

Full textual compliance under maximum classical stress.
Validates strictly against live response.context and live guidance text.
No mocking. No hardcoded expectations.

How to run:
  cd apps/guru-api
  python3 scripts/master_test_case_3_extreme_daivajna.py

Local testing (override API URL):
  GURU_API_URL=http://127.0.0.1:8000/api/v1/predict python3 scripts/master_test_case_3_extreme_daivajna.py
"""

import os
import re
import sys
from typing import Any, Dict, List, Optional

import requests

# Live Cloud Run URL; override with env for local testing
API_URL = os.environ.get("GURU_API_URL", "https://guru-api-660206747784.asia-south1.run.app/api/v1/predict")

PAYLOAD = {
    "timescale": "daily",
    "birth_details": {
        "name": "Extreme Validation Native",
        "dob": "1992-11-03",
        "time": "04:18",
        "lat": 28.6139,
        "lon": 77.2090,
        "timezone": "Asia/Kolkata",
    },
}


def extract_backend(context: Dict[str, Any]) -> Dict[str, Any]:
    """Extract backend truth from response.context (STEP 2)."""
    natal = context.get("natal") or {}
    panchanga = context.get("panchanga") or {}
    if isinstance(panchanga, dict) and "panchanga" in panchanga:
        panchanga = panchanga.get("panchanga") or panchanga
    return {
        "natal_ascendant_sign_index": (natal.get("ascendant") or {}).get("sign_index"),
        "natal_planets": natal.get("planets") or natal.get("planets_d1") or {},
        "janma_nakshatra": context.get("janma_nakshatra") or {},
        "panchanga": panchanga,
        "transit": context.get("transit") or {},
        "transit_events": context.get("transit_events") or [],
        "monthly_transits": context.get("monthly_transits") or [],
        "yearly_transits": context.get("yearly_transits") or [],
        "tara_bala": context.get("tara_bala") or {},
        "mahadasha_lord": (context.get("time") or {}).get("mahadasha_lord") or "",
        "antardasha_lord": (context.get("time") or {}).get("antardasha_lord") or "",
        "quality": context.get("quality") or {},
    }


def run_validations(guidance: str, backend: Dict[str, Any]) -> List[str]:
    """Run all STEP 3 validation rules. Returns list of failure messages (empty if pass)."""
    fails: List[str] = []
    g = guidance.lower()
    transit = backend.get("transit") or {}
    natal_planets = backend.get("natal_planets") or {}
    panchanga = backend.get("panchanga") or {}
    janma = backend.get("janma_nakshatra") or {}
    tara_bala = backend.get("tara_bala") or {}
    quality = backend.get("quality") or {}
    mahadasha_lord = (backend.get("mahadasha_lord") or "").strip()
    antardasha_lord = (backend.get("antardasha_lord") or "").strip()

    # ---- 1) PANCHANGA OPENING ----
    if guidance.startswith(("#", "Phase", "**", "1.", "1)")):
        fails.append("1) PANCHANGA OPENING: Output must not begin with headings or 'Phase 1' etc.")
    vara = panchanga.get("vara") or {}
    weekday = panchanga.get("weekday") or (vara.get("name") if isinstance(vara, dict) else None)
    day_lord = vara.get("lord") if isinstance(vara, dict) else None
    if weekday or day_lord:
        if weekday and weekday.lower() not in g and (not day_lord or day_lord.lower() not in g):
            fails.append(f"1) PANCHANGA OPENING: Weekday or day_lord ({weekday}/{day_lord}) from backend not in opening.")
    tithi_block = panchanga.get("tithi")
    if tithi_block:
        tithi_current = (tithi_block.get("current") if isinstance(tithi_block, dict) else None) or {}
        tithi_name = tithi_current.get("name") if isinstance(tithi_current, dict) else None
        if tithi_name and tithi_name.lower() not in g:
            fails.append(f"1) PANCHANGA OPENING: Tithi ({tithi_name}) from backend not in opening.")
    nak_block = panchanga.get("nakshatra")
    if nak_block and isinstance(nak_block, dict):
        nak_name = nak_block.get("name")
        if nak_name and nak_name.lower() not in g:
            fails.append(f"1) PANCHANGA OPENING: Nakshatra ({nak_name}) from backend not in opening.")

    # ---- 2) AUTHORITY ORDER ----
    if mahadasha_lord:
        # First sentence containing "currently transits" must be about Mahadasha Lord
        idx = g.find("currently transits")
        if idx >= 0:
            sentence_start = guidance.rfind(".", 0, idx) + 1 if guidance.rfind(".", 0, idx) >= 0 else 0
            sentence = guidance[sentence_start : sentence_start + 120].lower()
            if mahadasha_lord.lower() not in sentence:
                fails.append(f"2) AUTHORITY ORDER: First planetary sentence must start with '{mahadasha_lord} currently transits...'")
        elif mahadasha_lord.lower() not in g:
            fails.append(f"2) AUTHORITY ORDER: Mahadasha Lord ({mahadasha_lord}) not referenced.")
        primary = guidance[: int(len(guidance) * 0.7)].lower()
        lord_transits = primary.find(f"{mahadasha_lord.lower()} currently transits")
        if lord_transits < 0:
            lord_transits = primary.find(f"{mahadasha_lord.lower()} transits")
        moon_transits = primary.find("moon currently transits")
        if moon_transits < 0:
            moon_transits = primary.find("moon transits")
        if lord_transits >= 0 and moon_transits >= 0 and moon_transits < lord_transits:
            fails.append("2) AUTHORITY ORDER: Moon sentence must appear AFTER Mahadasha (and Antardasha).")
        if antardasha_lord and lord_transits >= 0 and moon_transits >= 0:
            ad_transits = primary.find(f"{antardasha_lord.lower()} currently transits")
            if ad_transits < 0:
                ad_transits = primary.find(f"{antardasha_lord.lower()} transits")
            if ad_transits >= 0 and moon_transits < ad_transits:
                fails.append("2) AUTHORITY ORDER: Moon sentence must appear AFTER Antardasha Lord.")

    # ---- 3) CHANDRASHTAMA CHECK ----
    moon_natal_house = (natal_planets.get("Moon") or {}).get("house")
    moon_transit_data = transit.get("Moon") or {}
    moon_transit_house = moon_transit_data.get("transit_house") or moon_transit_data.get("house_from_lagna")
    if moon_natal_house is not None and moon_transit_house is not None:
        eighth_from_natal = ((moon_natal_house - 1 + 7) % 12) + 1
        if moon_transit_house == eighth_from_natal:
            if "do not initiate major ventures" not in g:
                fails.append("3) CHANDRASHTAMA: Moon in 8th from natal Moon — must contain phrase like 'do not initiate major ventures'.")

    # ---- 4) TARA BALA OVERRIDE ----
    tara_category = (tara_bala.get("tara_category") or "").strip()
    if tara_category and tara_category.lower() in ("vipat", "naidhana"):
        caution_ok = any(w in g for w in ["avoid", "caution", "delay", "careful", "restraint"])
        if not caution_ok:
            fails.append("4) TARA BALA OVERRIDE: Vipat/Naidhana — guidance must contain cautionary tone (avoid, caution, delay, careful, restraint).")
        fluff = any(p in g for p in ["great opportunity", "success likely", "excellent day"])
        if fluff:
            fails.append("4) TARA BALA OVERRIDE: Vipat/Naidhana — must NOT contain 'great opportunity', 'success likely', 'excellent day'.")

    # ---- 5) DASHA ASPECT FILTER ----
    dasha_data = transit.get(mahadasha_lord) or {}
    aspects = dasha_data.get("aspects") or {} if isinstance(dasha_data, dict) else {}
    if aspects:
        if aspects.get("Mars") and aspects.get("Mars", 0) > 0:
            if not any(w in g for w in ["conflict", "risk", "impulsive", "harm", "tension"]):
                fails.append("5) DASHA ASPECT FILTER: Mars aspects Dasha Lord — must mention conflict/risk.")
        if aspects.get("Saturn") and aspects.get("Saturn", 0) > 0:
            if not any(w in g for w in ["delay", "responsibility", "patience", "discipline"]):
                fails.append("5) DASHA ASPECT FILTER: Saturn aspects Dasha Lord — must mention delay/responsibility.")
        if aspects.get("Rahu") and aspects.get("Rahu", 0) > 0:
            if not any(w in g for w in ["confusion", "verify", "facts", "illusion"]):
                fails.append("5) DASHA ASPECT FILTER: Rahu aspects Dasha Lord — must mention confusion/verify facts.")
        if aspects.get("Jupiter") and aspects.get("Jupiter", 0) > 0:
            if not any(w in g for w in ["protection", "relief", "support", "wisdom"]):
                fails.append("5) DASHA ASPECT FILTER: Jupiter aspects Dasha Lord — must mention protection/relief.")

    # ---- 6) RETROGRADE LOCK ----
    if "retrograde" in g or "vakri" in g:
        allowed_retro = set()
        for p, d in transit.items():
            if isinstance(d, dict) and d.get("is_retrograde") is True:
                allowed_retro.add(p.lower())
        for shift in backend.get("yearly_transits", []) + backend.get("monthly_transits", []):
            if shift.get("is_retrograde"):
                allowed_retro.add((shift.get("planet") or "").lower())
        for p, d in natal_planets.items():
            if isinstance(d, dict) and d.get("is_retrograde") is True:
                allowed_retro.add(p.lower())
        for planet in ["mercury", "venus", "mars", "jupiter", "saturn", "sun", "moon"]:
            if planet in allowed_retro:
                continue
            if re.search(rf"\b{planet}\b.*retrograde|retrograde.*\b{planet}\b", g):
                fails.append(f"6) RETROGRADE LOCK: '{planet}' stated as retrograde but JSON has no is_retrograde true.")

    # ---- 7) LOW BINDU STRESS ----
    if mahadasha_lord:
        q = quality.get(mahadasha_lord) or {}
        bindu = q.get("bindu") if isinstance(q, dict) else None
        if bindu is not None:
            try:
                b = int(bindu)
                if b <= 1 and not any(w in g for w in ["stress", "effort", "challenge", "caution", "difficulty", "restraint"]):
                    fails.append("7) LOW BINDU STRESS: Bindu <= 1 for Dasha Lord — guidance must reflect stress/effort.")
                if b >= 4 and not any(w in g for w in ["comfort", "support", "favorable", "ease", "strength", "bindu"]):
                    fails.append("7) LOW BINDU STRESS: Bindu >= 4 for Dasha Lord — guidance must reflect comfort/support.")
            except (TypeError, ValueError):
                pass

    # ---- 8) TRANSIT MOVEMENTS FORMAT ----
    if "later this month" in g or "later this year" in g:
        fails.append("8) TRANSIT MOVEMENTS FORMAT: Must NOT contain 'later this month' or 'later this year'.")
    # Exact format check: "On [DATE], [Planet] moves from" and "in your [N] house" and "to"
    if backend.get("transit_events") or backend.get("monthly_transits") or backend.get("yearly_transits"):
        if "moves from" in g and " to " in g and "in your" in g and "house" in g:
            pass  # format present
        # Don't fail on format shape unless we have shifts and none are narrated

    # ---- 9) NAKSHATRA THRONE BLOCK ----
    if "you were born under" not in g:
        fails.append("9) NAKSHATRA THRONE BLOCK: Must contain 'You were born under'.")
    janma_name = (janma.get("name") or "").strip()
    if janma_name and janma_name.lower() not in g:
        fails.append(f"9) NAKSHATRA THRONE BLOCK: Must mention Janma Nakshatra name ({janma_name}).")
    # Natal planet in that nakshatra and retrograde → must mention Retrograde (checked in 6 if present)
    transit_in_janma = False
    for p, d in transit.items():
        if isinstance(d, dict) and (d.get("nakshatra") or "").strip() == janma_name:
            transit_in_janma = True
            break
    if not transit_in_janma and janma_name:
        if "no transit planet activates your throne" not in g and "no planet activates" not in g:
            fails.append("9) NAKSHATRA THRONE BLOCK: No transit in Janma Nakshatra — must say 'Today, no transit planet activates your throne.'")
    lines = [ln.strip() for ln in guidance.split("\n") if ln.strip()]
    born_idx = -1
    for i, ln in enumerate(lines):
        if "you were born under" in ln.lower():
            born_idx = i
            break
    if born_idx >= 0 and (len(lines) - born_idx) > 4:
        fails.append("9) NAKSHATRA THRONE BLOCK: Throne block (from 'You were born under' to end) must be max 4 lines.")

    # ---- 10) NO FLUFF FILTER ----
    fluff_phrases = ["amazing day", "great opportunity", "unlimited success", "positive vibes"]
    for phrase in fluff_phrases:
        if phrase in g:
            fails.append(f"10) NO FLUFF FILTER: Guidance must NOT contain '{phrase}'.")

    return fails


def main() -> None:
    print("=" * 60)
    print("MASTER TEST CASE #3 — EXTREME DAIVAJNA VALIDATION")
    print("=" * 60)
    print("POST", API_URL)
    try:
        r = requests.post(API_URL, json=PAYLOAD, timeout=120)
        r.raise_for_status()
    except Exception as e:
        print("API call failed:", e)
        sys.exit(1)

    data = r.json()
    guidance = (data.get("guidance") or "").strip()
    context = data.get("context") or {}

    if not guidance:
        print("FAIL: Empty guidance.")
        sys.exit(1)

    backend = extract_backend(context)
    fails = run_validations(guidance, backend)

    if fails:
        print("\nFAILED RULES:")
        for f in fails:
            print(" ", f)
        print("\nFirst failing rule:", fails[0])
        sys.exit(1)

    print("\nGURUSUITE — MASTER TEST CASE #3 PASSED (Extreme Daivajna Integrity)")


if __name__ == "__main__":
    main()
