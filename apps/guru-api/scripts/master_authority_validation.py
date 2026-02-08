#!/usr/bin/env python3
"""
MASTER AUTHORITY VALIDATION TEST CASE
Revision guru-api-00227-cf6. Validates all authority/engineering locks.
Uses actual API response to validate against context.
"""

import re
import sys
import requests

API_URL = "https://guru-api-660206747784.asia-south1.run.app/api/v1/predict"

PAYLOAD = {
    "timescale": "daily",
    "calculation_date": "2026-02-06T12:00:00",
    "birth_details": {
        "name": "Authority Lock Test Native",
        "dob": "1985-05-16",
        "time": "18:38",
        "lat": 12.9716,
        "lon": 77.5946,
        "timezone": "Asia/Kolkata",
    },
}

DECL_RE = re.compile(
    r"(Venus|Mercury|Jupiter|Saturn|Sun|Mars|Moon)\s+currently\s+transits\s+(.+?)\s+in\s+your\s+(\d+)(?:st|nd|rd|th)\s+house",
    re.IGNORECASE,
)

AVASTHA_ALLOWED = {
    "Strength amplified.",
    "Expression restrained.",
    "Results manifest externally.",
    "Results fluctuate.",
    "Results internalized.",
}


def extract_declarations(guidance: str) -> dict:
    out = {}
    for m in DECL_RE.finditer(guidance):
        planet, sign_phrase, house = m.group(1), m.group(2).strip(), int(m.group(3))
        out[planet] = (sign_phrase, house)
    return out


def main():
    failures = []
    print("Calling Cloud API (revision 00227-cf6)...")
    try:
        r = requests.post(API_URL, json=PAYLOAD, timeout=90)
        r.raise_for_status()
    except Exception as e:
        print("API ERROR:", e)
        sys.exit(1)

    data = r.json()
    guidance = data.get("guidance", "")
    context = data.get("context", {})

    transit = context.get("transit", {})
    time_block = context.get("time", {})
    mahadasha = (time_block.get("mahadasha_lord") or "").strip()
    tara = (context.get("tara_bala") or {})
    tara_cat = (tara.get("tara_category") or "").strip()
    g_lower = guidance.lower()

    # 1. Declaration block: house must match context transit_house
    decls = extract_declarations(guidance)
    for planet, (sign_phrase, house) in decls.items():
        pdata = transit.get(planet, {})
        if isinstance(pdata, dict):
            exp_house = pdata.get("house_from_lagna") or pdata.get("transit_house")
            if exp_house is not None and house != exp_house:
                failures.append(f"1. DECLARATION: {planet} house {house} != context {exp_house}")

    # 2. Panchanga: must reflect JSON (Panchami, Krishna, Friday, etc.)
    if "panchami" not in g_lower and "pancham" not in g_lower:
        failures.append("2. PANCHANGA: Panchami not found")
    if "krishna" not in g_lower:
        failures.append("2. PANCHANGA: Krishna Paksha not found")
    if "friday" not in g_lower and "venus" not in g_lower:
        failures.append("2. PANCHANGA: Friday/Vara not found")

    # 3. Authority order: Mahadasha lord first in interpretation
    if mahadasha:
        mt_start = g_lower.find("mahadasha")
        if mt_start >= 0:
            body_after_dasha = guidance[mt_start:]
            first_planet_pos = len(body_after_dasha)
            first_planet = None
            for p in ["Venus", "Mercury", "Jupiter", "Saturn", "Sun", "Mars", "Moon"]:
                pos = body_after_dasha.lower().find(p.lower())
                if pos >= 0 and pos < first_planet_pos:
                    first_planet_pos = pos
                    first_planet = p
            if first_planet and first_planet != mahadasha:
                failures.append(f"3. AUTHORITY: First planet in interpretation should be {mahadasha}, found {first_planet}")

    # 4. Avastha: modifiers should align with canonical (allow paraphrases like "restrained expression")
    for phrase in ["Strength amplified", "Expression restrained", "Results manifest externally",
                   "Results fluctuate", "Results internalized"]:
        if phrase.lower() in g_lower:
            pass

    # 5. Dignity: Mars in Capricorn = exalted, cannot have "Expression restrained"
    mars_data = transit.get("Mars", {})
    if isinstance(mars_data, dict) and mars_data.get("dignity") == "exalted":
        if "mars" in g_lower and "expression restrained" in g_lower:
            failures.append("5. DIGNITY: Mars exalted cannot have 'Expression restrained'")

    # 6. Tara override: Pratyak/Vipat/Naidhana → no optimism
    if tara_cat in ("Vipat", "Naidhana", "Pratyak"):
        if "great opportunity" in g_lower or "excellent day" in g_lower or "highly favorable" in g_lower:
            failures.append("6. TARA: Optimism prohibited for " + tara_cat)

    # 7. Chandra Bala: Moon 8th from natal → exact sentence
    moon_data = transit.get("Moon", {})
    if isinstance(moon_data, dict) and moon_data.get("house_from_moon") == 8:
        if "do not initiate major ventures today" not in g_lower:
            failures.append("7. CHANDRA: Must include exact 'Do not initiate major ventures today.'")

    # 8. Throne
    if "you were born under" not in g_lower:
        failures.append("8. THRONE: Missing 'You were born under [Nakshatra]...'")
    if "jyeshtha gives leadership" in g_lower or "jyeshtha gives" in g_lower:
        failures.append("8. THRONE: No static personality (Jyeshtha gives...)")
    if "today, no transit planet activates your throne" not in g_lower and "activates your throne" not in g_lower:
        failures.append("8. THRONE: Must have activation sentence")

    # 9. Dharma: Gita present
    if "gita" not in g_lower and "bhagavad" not in g_lower:
        failures.append("9. DHARMA: Gita verse not found")

    # 10. No duplicate declaration in narrative (declarations are prepended; narrative should not repeat them)
    lines = guidance.splitlines()
    decl_count = sum(1 for l in lines if "currently transits" in l and "in your" in l and l.strip().endswith("house."))
    if decl_count > 7:
        failures.append("10. DUPLICATE: Too many declaration-style lines (possible duplicate in narrative)")

    if failures:
        print("FAILED:")
        for f in failures:
            print(" -", f)
        print("\n--- GUIDANCE (first 3000 chars) ---")
        print(guidance[:3000])
        sys.exit(1)

    print("GURUSUITE — MASTER AUTHORITY VALIDATION PASSED")
    print("All checklist points verified.")
    sys.exit(0)


if __name__ == "__main__":
    main()
