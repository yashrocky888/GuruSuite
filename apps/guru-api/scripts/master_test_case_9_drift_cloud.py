#!/usr/bin/env python3
"""
MASTER TEST CASE #9 — PROBABILISTIC DRIFT DETECTION (Cloud-only)

Run same daily prediction 10 times; validate structural integrity across calls.
Detects: model drift, retrograde leakage, authority order instability,
declaration corruption, structural randomness, fluff creep.
Cloud only. No GURU_API_URL override. Do not modify backend, prompt, validators, or API.
"""

import re
import socket
import sys
import time
from typing import Dict, Any, List, Tuple

import requests

# Cloud only — DO NOT use GURU_API_URL
API_URL = "https://guru-api-660206747784.asia-south1.run.app/api/v1/predict"

PAYLOAD = {
    "timescale": "daily",
    "calculation_date": "2026-02-04T12:00:00",
    "birth_details": {
        "name": "Drift Stability Native",
        "dob": "1991-07-12",
        "time": "11:26",
        "lat": 12.9716,
        "lon": 77.5946,
        "timezone": "Asia/Kolkata",
    },
}

# New canonical format: "Planet — Sign — Nth House" (e.g. "Mercury — Aquarius (Kumbha) — 6th House")
# Includes Rahu, Ketu per MAHABHARATA DAIVA-JÑA full planet lock
PLANETS = r"(Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn|Rahu|Ketu)"
DECL_LINE_RE = re.compile(
    rf"{PLANETS}\s+[—\-]\s+(.+?)\s+[—\-]\s+(\d+(?:st|nd|rd|th))\s+House",
    re.IGNORECASE,
)

# Strict: backend declaration lines only (full line match)
STRICT_DECL_RE = re.compile(
    rf"^\s*{PLANETS}\s+[—\-]\s+.+?\s+[—\-]\s+\d+(?:st|nd|rd|th)\s+House\s*$",
    re.IGNORECASE,
)

# Split sentences for retrograde check
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")

# Declaration line (for retrograde skip) — new format
DECL_SENTENCE_RE = re.compile(
    rf"^\s*{PLANETS}\s+[—\-]\s+.+?\s+[—\-]\s+\d+(?:st|nd|rd|th)\s+House\s*$",
    re.IGNORECASE,
)

FLUFF_PHRASES = [
    "amazing",
    "fantastic",
    "incredible",
    "positive vibes",
    "life changing",
    "great opportunity",
]


def _extract_declaration_block(guidance: str) -> str:
    """Extract declaration lines from CURRENT SKY POSITION section. Format: Planet — Sign — Nth House."""
    if not guidance:
        return ""
    # Find CURRENT SKY POSITION section (with or without emoji)
    sky_marker = "CURRENT SKY POSITION"
    idx = guidance.find(sky_marker)
    if idx < 0:
        return ""
    # Start after the heading line; take content until next section or end
    rest = guidance[idx + len(sky_marker) :].lstrip()
    lines = []
    for line in rest.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # Stop at next section heading (starts with emoji or all-caps short label)
        if re.match(r"^[🕉👑🌙⭐⚖🪔🔄]", stripped) or re.match(r"^[A-Z][A-Z\s]{2,20}$", stripped):
            break
        if STRICT_DECL_RE.match(stripped):
            lines.append(stripped)
    return "\n".join(lines)


def _extract_sign_and_house_per_planet(guidance: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Return (planet -> sign_phrase, planet -> house_ordinal) from strict declaration lines only."""
    decl_block = _extract_declaration_block(guidance)
    sign_per = {}
    house_per = {}
    for line in decl_block.splitlines():
        m = DECL_LINE_RE.search(line)
        if m:
            planet = m.group(1)
            sign_phrase = m.group(2).strip()
            house_ord = m.group(3)
            sign_per[planet] = sign_phrase
            house_per[planet] = house_ord
    return sign_per, house_per


def _build_allowed_retro(context: Dict[str, Any]) -> set:
    allowed = set()
    transit = context.get("transit") or {}
    for p, pdata in transit.items():
        if isinstance(pdata, dict) and pdata.get("is_retrograde") is True:
            allowed.add((p or "").lower())
    natal = context.get("natal") or {}
    natal_planets = natal.get("planets") or natal.get("planets_d1") or {}
    for p, pdata in natal_planets.items():
        if isinstance(pdata, dict) and pdata.get("is_retrograde") is True:
            allowed.add((p or "").lower())
    for shift in context.get("yearly_transits", []) + context.get("monthly_transits", []):
        if shift.get("is_retrograde"):
            allowed.add((shift.get("planet") or "").lower())
    return allowed


def _retrograde_violation(guidance: str, allowed_retro: set, transit_planets: List[str]) -> bool:
    """True if any non-declaration sentence mentions retrograde/vakri for a planet not in allowed_retro."""
    for sent in SENTENCE_SPLIT_RE.split(guidance):
        sent = sent.strip()
        if not sent or len(sent) < 5:
            continue
        if DECL_SENTENCE_RE.match(sent):
            continue
        lower = sent.lower()
        if "retrograde" not in lower and "vakri" not in lower:
            continue
        for p in transit_planets:
            if p.lower() in lower and p.lower() not in allowed_retro:
                return True
    return False


def main() -> None:
    failures: List[str] = []
    runs: List[Tuple[str, Dict[str, Any]]] = []

    print("Checking DNS resolution...")
    try:
        socket.gethostbyname("guru-api-660206747784.asia-south1.run.app")
        print("DNS OK")
    except Exception as e:
        print("DNS FAILED:", e)
        sys.exit(1)

    print("Calling Cloud API 10 times...")
    for i in range(10):
        response = None
        for attempt in range(3):
            try:
                response = requests.post(API_URL, json=PAYLOAD, timeout=60)
                response.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                print(f"Retry {attempt+1}/3 after network error:", e)
                time.sleep(1)

        if response is None:
            print("API ERROR (run %d) after retries" % (i + 1))
            sys.exit(1)

        data = response.json()
        guidance = data.get("guidance", "")
        context = data.get("context", {})
        runs.append((guidance, context))

    # Reference from run 1
    g1, ctx1 = runs[0]
    ref_decl_block = _extract_declaration_block(g1)
    ref_sign_per, ref_house_per = _extract_sign_and_house_per_planet(g1)
    allowed_retro = _build_allowed_retro(ctx1)
    time_block = ctx1.get("time") or {}
    mahadasha = (time_block.get("mahadasha_lord") or "").strip().lower()
    transit_planets = list((ctx1.get("transit") or {}).keys())

    # -------------------------------------------------------------------------
    # RULE 0 — Declaration block has 9 planets (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu)
    # -------------------------------------------------------------------------
    expected_planets = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}
    ref_planets = set(ref_sign_per.keys())
    if ref_planets != expected_planets:
        failures.append("FAIL_DECLARATION_DRIFT")  # wrong planet count

    # -------------------------------------------------------------------------
    # RULE 1 — Declaration block identical to run 1 in runs 2–10
    # -------------------------------------------------------------------------
    if "FAIL_DECLARATION_DRIFT" not in failures:
        for i in range(1, 10):
            decl_block = _extract_declaration_block(runs[i][0])
            if decl_block != ref_decl_block:
                failures.append("FAIL_DECLARATION_DRIFT")
                break

    # -------------------------------------------------------------------------
    # RULE 2 — Authority order: first planet in declaration block = Mahadasha Lord
    # -------------------------------------------------------------------------
    for i in range(10):
        decl_block = _extract_declaration_block(runs[i][0])
        first_planet = None
        for line in decl_block.splitlines():
            m = DECL_LINE_RE.search(line.strip())
            if m:
                first_planet = m.group(1).strip().lower()
                break
        if mahadasha and first_planet and first_planet != mahadasha:
            failures.append("FAIL_AUTHORITY_DRIFT")
            break
        if not decl_block.strip():
            failures.append("FAIL_AUTHORITY_DRIFT")
            break

    # -------------------------------------------------------------------------
    # RULE 3 — Retrograde consistency (no planet outside allowed_retro described as retrograde)
    # -------------------------------------------------------------------------
    for i in range(10):
        if _retrograde_violation(runs[i][0], allowed_retro, transit_planets):
            failures.append("FAIL_RETROGRADE_DRIFT")
            break

    # -------------------------------------------------------------------------
    # RULE 4 — Sign phrase per planet identical across runs
    # -------------------------------------------------------------------------
    for i in range(1, 10):
        sign_per, _ = _extract_sign_and_house_per_planet(runs[i][0])
        for planet, sign_phrase in ref_sign_per.items():
            if sign_per.get(planet) != sign_phrase:
                failures.append("FAIL_SIGN_DRIFT")
                break
        else:
            continue
        break

    # -------------------------------------------------------------------------
    # RULE 5 — House ordinal per planet identical across runs
    # -------------------------------------------------------------------------
    for i in range(1, 10):
        _, house_per = _extract_sign_and_house_per_planet(runs[i][0])
        for planet, house_ord in ref_house_per.items():
            if house_per.get(planet) != house_ord:
                failures.append("FAIL_HOUSE_DRIFT")
                break
        else:
            continue
        break

    # -------------------------------------------------------------------------
    # RULE 6 — Each run contains "You were born under"
    # -------------------------------------------------------------------------
    for i in range(10):
        if "you were born under" not in runs[i][0].lower():
            failures.append("FAIL_THRONE_DRIFT")
            break

    # -------------------------------------------------------------------------
    # RULE 7 — No fluff in any run
    # -------------------------------------------------------------------------
    for i in range(10):
        g_lower = runs[i][0].lower()
        for phrase in FLUFF_PHRASES:
            if phrase in g_lower:
                failures.append("FAIL_FLUFF_DRIFT")
                break
        else:
            continue
        break

    # -------------------------------------------------------------------------
    # Output
    # -------------------------------------------------------------------------
    if failures:
        print("FAILED RULES:")
        for f in failures:
            print("-", f)

        print("\n--- DRIFT DEBUG OUTPUT ---")
        if len(runs) >= 2:

            # Handle both tuple and dict storage formats safely
            def extract_guidance(item):
                if isinstance(item, dict):
                    return item.get("guidance", "")
                if isinstance(item, (list, tuple)) and len(item) > 0:
                    return item[0]
                return ""

            run1 = extract_guidance(runs[0])
            run2 = extract_guidance(runs[1])

            print("\nRUN 1 DECLARATION BLOCK:")
            print(_extract_declaration_block(run1))

            print("\nRUN 2 DECLARATION BLOCK:")
            print(_extract_declaration_block(run2))

            print("\nRUN 1 LENGTH:", len(run1))
            print("RUN 2 LENGTH:", len(run2))

            print("\nRUN 1 FIRST 800 CHARS:\n")
            print(run1[:800])

            print("\nRUN 2 FIRST 800 CHARS:\n")
            print(run2[:800])

        else:
            print("Not enough runs captured for comparison.")

        sys.exit(1)

    print("GURUSUITE — MASTER TEST CASE #9 PASSED (Drift Stability Integrity)")
    sys.exit(0)


if __name__ == "__main__":
    main()
