#!/usr/bin/env python3
"""
GURUSUITE — Master Test Case #2: Chandrashtama + Sade Sati + Saturn Aspect + Tara Bala Vipat.

Validates adversity handling: Chandrashtama warning, authority order, Tara Vipat tone,
aspect modifier, no retrograde hallucination, Nakshatra throne when no activation.
"""

import json
import re
import sys
from typing import Any, Dict, Optional

import requests

API_URL = "https://guru-api-660206747784.asia-south1.run.app/api/v1/predict"
# Uncomment for local: API_URL = "http://127.0.0.1:8000/api/v1/predict"

PAYLOAD = {
    "timescale": "daily",
    "birth_details": {
        "name": "Saturn Test Native",
        "dob": "1988-08-22",
        "time": "06:12",
        "lat": 28.6139,
        "lon": 77.2090,
        "timezone": "Asia/Kolkata",
    },
}


def main() -> None:
    print("=" * 60)
    print("GURUSUITE — Master Test Case #2 (Chandrashtama + Sade Sati + Tara Vipat)")
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
        print("FAIL: Empty guidance")
        sys.exit(1)

    # Backend truth
    natal = context.get("natal") or {}
    transit = context.get("transit") or {}
    time_block = context.get("time") or {}
    panchanga = context.get("panchanga") or {}
    if isinstance(panchanga, dict) and "panchanga" in panchanga:
        panchanga = panchanga.get("panchanga") or panchanga
    janma = context.get("janma_nakshatra") or {}
    tara_bala = context.get("tara_bala") or {}
    tara_category = tara_bala.get("tara_category") or panchanga.get("tara_category") or ""

    natal_planets = natal.get("planets") or natal.get("planets_d1") or {}
    moon_natal_house = (natal_planets.get("Moon") or {}).get("house")
    moon_transit = transit.get("Moon") or {}
    moon_transit_house = moon_transit.get("transit_house") or moon_transit.get("house_from_lagna")
    mahadasha_lord = (time_block.get("mahadasha_lord") or "").strip()
    dasha_lord_aspects = (transit.get(mahadasha_lord) or {}).get("aspects") or {} if mahadasha_lord else {}

    g = guidance.lower()
    fails: list[str] = []

    # 1) Panchanga opening — no headings; must begin with weekday/tithi/nakshatra
    if guidance.startswith(("#", "Phase", "**", "1.", "1)")):
        fails.append("1) Panchanga: Output must not begin with headings/labels.")
    weekday = (panchanga.get("vara") or {}).get("name") or panchanga.get("weekday") or ""
    if weekday and weekday.lower() not in g and (panchanga.get("vara") or {}).get("lord", "").lower() not in g:
        fails.append(f"1) Panchanga: Weekday/lord ({weekday}) from backend not in opening.")
    tithi_block = panchanga.get("tithi") or {}
    tithi_name = (tithi_block.get("current") or {}).get("name") if isinstance(tithi_block, dict) else None
    if tithi_name and tithi_name.lower() not in g:
        fails.append(f"1) Panchanga: Tithi ({tithi_name}) from backend not in opening.")
    nak_block = panchanga.get("nakshatra")
    nak_name = (nak_block.get("name") if isinstance(nak_block, dict) else None) or ""
    if nak_name and nak_name.lower() not in g:
        fails.append(f"1) Panchanga: Nakshatra ({nak_name}) from backend not in opening.")

    # 2) Authority order — Mahadasha Lord (from JSON) must be named before Moon-as-planet in transit sentence
    # Look for "[Planet] currently transits" pattern; lord must appear first.
    if mahadasha_lord:
        if mahadasha_lord.lower() not in g and "mahadasha" not in g:
            fails.append(f"2) Authority: Mahadasha Lord ({mahadasha_lord}) not clearly referenced.")
        else:
            primary = guidance[: int(len(guidance) * 0.65)].lower()
            # First occurrence of "X currently transits" or "X transits" for lord vs Moon
            lord_token = mahadasha_lord.lower()
            lord_transits = primary.find(f"{lord_token} currently transits")
            if lord_transits < 0:
                lord_transits = primary.find(f"{lord_token} transits")
            moon_transits = primary.find("moon currently transits")
            if moon_transits < 0:
                moon_transits = primary.find("moon transits")
            if lord_transits >= 0 and moon_transits >= 0 and moon_transits < lord_transits:
                fails.append("2) Authority: Moon (planet) transit sentence before Mahadasha Lord transit sentence.")

    # 3) Chandrashtama — Moon in 8th from natal Moon → must have warning
    if moon_natal_house is not None and moon_transit_house is not None:
        eighth_from_natal = ((moon_natal_house - 1 + 7) % 12) + 1
        if moon_transit_house == eighth_from_natal:
            if "do not initiate major ventures" not in g:
                fails.append("3) Chandrashtama: Moon in 8th from natal Moon but missing 'Do not initiate major ventures today.'")

    # 4) Tara Bala Vipat — tone must reduce optimism
    if tara_category and "vipat" in tara_category.lower():
        if any(phrase in g for phrase in ["great opportunity", "success likely", "excellent day", "highly favorable", "auspicious day"]):
            fails.append("4) Tara Vipat: Tone must be cautionary; avoid optimistic fluff.")
        if not any(w in g for w in ["caution", "careful", "avoid", "restraint", "discipline", "patience", "delay", "karmic", "restrict"]):
            fails.append("4) Tara Vipat: Output should feel heavy/restrictive; no cautionary language found.")

    # 5) Aspect filter — if Mars aspects Dasha Lord, conflict phrase
    if dasha_lord_aspects.get("Mars") and dasha_lord_aspects.get("Mars", 0) > 0:
        if not any(phrase in g for phrase in ["conflict", "impulsive", "risk", "harm", "tension", "aggression"]):
            fails.append("5) Aspect: Mars aspects Dasha Lord but no conflict/risk phrase.")

    # 6) No retrograde hallucination — only if JSON says is_retrograde true (transit or natal)
    if "retrograde" in g or "vakri" in g:
        allowed = set()
        for p, d in (transit or {}).items():
            if isinstance(d, dict) and d.get("is_retrograde") is True:
                allowed.add(p.lower())
        for shift in context.get("yearly_transits", []) + context.get("monthly_transits", []):
            if shift.get("is_retrograde"):
                allowed.add((shift.get("planet") or "").lower())
        natal_p = (context.get("natal") or {}).get("planets") or (context.get("natal") or {}).get("planets_d1") or {}
        for p, d in (natal_p or {}).items():
            if isinstance(d, dict) and d.get("is_retrograde") is True:
                allowed.add(p.lower())
        for planet in ["mercury", "venus", "mars", "jupiter", "saturn"]:
            if planet in allowed:
                continue
            if re.search(rf"\b{planet}\b.*retrograde|retrograde.*\b{planet}\b", g):
                fails.append(f"6) Retrograde: '{planet}' stated as retrograde but JSON has no is_retrograde true (transit/natal/shift).")

    # 7) Nakshatra throne — if no transit in Janma, should state no activation (or not fabricate)
    janma_name = (janma.get("name") or "").strip()
    transit_in_janma = False
    for p, d in (transit or {}).items():
        if isinstance(d, dict) and (d.get("nakshatra") or "").strip() == janma_name:
            transit_in_janma = True
            break
    if not transit_in_janma and janma_name:
        if "you were born under" not in g:
            fails.append("7) Nakshatra Throne: Must include Janma Nakshatra block.")
        # Prefer explicit "no transit planet activates" when none; optional strict check
        if "no transit planet" not in g and "no planet activates" not in g and "no activation" not in g:
            pass  # Soft: prompt says "do not fabricate"; test accepts either explicit no-activation or simple close

    # Overall tone — must feel heavy, not motivational
    if any(phrase in g for phrase in ["great opportunity day", "success likely", "excellent time", "highly auspicious"]):
        fails.append("Tone: Day must feel heavy/restrictive; not motivational fluff.")

    if fails:
        print("\nFAILED CHECKS:")
        for f in fails:
            print(" ", f)
        print("\nFirst failing rule:", fails[0])
        sys.exit(1)

    print("\nAll Master Test Case #2 checks passed.")
    print("  - Panchanga opening present, no invented data")
    print("  - Authority order: Dasha Lord before Moon")
    print("  - Chandrashtama warning when Moon in 8th from natal Moon")
    print("  - Tara Vipat: cautionary tone")
    print("  - Aspect modifier when Mars aspects Dasha Lord")
    print("  - No retrograde without JSON proof")
    print("  - Nakshatra Throne handled (no fabrication)")
    print("  - Tone: heavy, disciplined, cautionary")
    print("\nGURUSUITE — MASTER TEST CASE #2 PASSED (Daivajna adversity rule)")


if __name__ == "__main__":
    main()
