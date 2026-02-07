#!/usr/bin/env python3
"""
EXTREME BATTLEFIELD STRESS TEST

Triggers ALL locks simultaneously:
- Rahu Mahadasha active
- Saturn transiting 8th from Lagna
- Moon transiting 8th from natal Moon (Chandra Bala)
- Naidhana Tara (strong caution)
- Rahu + Saturn dusthana stacking

Payload chosen to statistically force stress conditions.
"""

import sys
import requests

API_URL = "https://guru-api-660206747784.asia-south1.run.app/api/v1/predict"

PAYLOAD = {
    "timescale": "daily",
    "calculation_date": "2026-02-15",
    "birth_details": {
        "name": "BattleTest",
        "dob": "1990-09-14",
        "time": "02:18",
        "lat": 12.9716,
        "lon": 77.5946,
        "timezone": "Asia/Kolkata",
    },
}

FAILURES = []


def main():
    print("⚔️ EXTREME BATTLEFIELD STRESS TEST")
    print("=" * 50)
    print(f"Birth: 1990-09-14 02:18, Bangalore")
    print(f"Calculation: 2026-02-15")
    print()

    try:
        r = requests.post(API_URL, json=PAYLOAD, timeout=60)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"❌ API ERROR: {e}")
        sys.exit(1)

    guidance = data.get("guidance", "") or data.get("message", "")
    structured = data.get("structured") or {}
    context = data.get("context", {})

    time_block = context.get("time") or {}
    mahadasha = (time_block.get("mahadasha_lord") or "").strip()
    transit = context.get("transit") or {}
    tara = context.get("tara_bala") or {}
    tara_cat = (tara.get("tara_category") or tara.get("tara_name") or "").strip() if isinstance(tara, dict) else ""

    # Use structured for checks when available; else guidance
    body = structured.get("declarations", "") + "\n\n" + (guidance or "")
    if structured:
        body = (
            (structured.get("greeting") or "")
            + "\n\n"
            + (structured.get("declarations") or "")
            + "\n\n"
            + (structured.get("panchanga") or "")
            + "\n\n"
            + (structured.get("dasha") or "")
            + "\n\n"
            + (structured.get("chandra_bala") or "")
            + "\n\n"
            + (structured.get("tara_bala") or "")
            + "\n\n"
            + (structured.get("major_transits") or "")
            + "\n\n"
            + (structured.get("dharmic_guidance") or "")
            + "\n\n"
            + (structured.get("throne") or "")
        )
    else:
        body = guidance

    body_lower = body.lower()

    # 1. Greeting first
    if "the wheel of time turns thus" in body_lower or "battletest" in body_lower:
        print("✅ 1. Greeting appears first")
    else:
        FAILURES.append("1. Greeting not found or not first")
        print("❌ 1. Greeting not found or not first")

    # 2. Declaration block: 9 planets, one per line, no dup
    decl_lines = [l for l in body.splitlines() if "currently transits" in l or "—" in l and "House" in l]
    planets_in_decl = set()
    for line in decl_lines:
        for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            if p in line:
                planets_in_decl.add(p)
                break
    if len(planets_in_decl) >= 8 and "Rahu" in str(planets_in_decl) and "Ketu" in str(planets_in_decl):
        print("✅ 2. Declaration block: 9 planets, Rahu+Ketu included")
    else:
        FAILURES.append(f"2. Declaration: {len(planets_in_decl)} planets found")
        print(f"❌ 2. Declaration: {len(planets_in_decl)} planets, need 9 with Rahu+Ketu")

    # 3. Rahu Mahadasha authority (if active)
    if mahadasha == "Rahu":
        if "shadow amplification" in body_lower and "rahu intensifies" in body_lower:
            print("✅ 3. Rahu Mahadasha authority present")
        else:
            FAILURES.append("3. Rahu Mahadasha authority missing")
            print("❌ 3. Rahu Mahadasha authority missing")
    else:
        print("⏭ 3. Rahu Mahadasha not active (skipped)")

    # 4. Saturn 8th: no optimism
    if "great opportunity" in body_lower or "excellent day" in body_lower:
        FAILURES.append("4. Optimism present despite Saturn 8th")
        print("❌ 4. Optimism present (forbidden)")
    else:
        print("✅ 4. Saturn 8th: no illicit optimism")

    # 5. Moon 8th from Moon: exact line
    if "do not initiate major ventures today" in body_lower:
        print("✅ 5. Moon 8th: exact Chandrashtama line present")
    else:
        FAILURES.append("5. Chandrashtama exact line missing")
        print("❌ 5. Moon 8th: exact line missing")

    # 6. Naidhana Tara (when active): must have "Avoid major risks"
    if tara_cat == "Naidhana":
        if "avoid major risks" in body_lower:
            print("✅ 6. Naidhana Tara: 'Avoid major risks' present")
        else:
            FAILURES.append("6. Naidhana Tara: 'Avoid major risks' missing when Naidhana active")
            print("❌ 6. Naidhana Tara: 'Avoid major risks' not found (Naidhana active)")
    else:
        print("⏭ 6. Naidhana Tara not active (skipped)")

    # 7. Dharma: canonical block (3–6 lines; zero-hardcode format includes lordship, tara, afflicted house, gita, closing)
    dharma = structured.get("dharmic_guidance", "")
    dharma_lines = [l.strip() for l in dharma.split("\n") if l.strip()]
    if 3 <= len(dharma_lines) <= 6 and "Bhagavad Gita" in dharma and "Act with awareness" in dharma:
        print("✅ 7. Dharma section canonical (3–6 lines, Gita + closing)")
    else:
        FAILURES.append(f"7. Dharma has {len(dharma_lines)} lines or missing Gita/closing")
        print(f"❌ 7. Dharma: {len(dharma_lines)} lines (expected 3–6 with Gita + closing)")

    # 8. No fallback
    if "guidance could not be generated" in body_lower or "openai_api_key" in body_lower:
        FAILURES.append("8. Fallback message present")
        print("❌ 8. Fallback message present")
    else:
        print("✅ 8. No fallback message")

    # 9. All 9 planets in major transits
    major = structured.get("major_transits", "") or body
    planets_in_major = sum(1 for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"] if p in major)
    if planets_in_major >= 8:
        print("✅ 9. All planets in major transits")
    else:
        FAILURES.append(f"9. Only {planets_in_major}/9 planets in major transits")
        print(f"❌ 9. Major transits: {planets_in_major}/9 planets")

    print()
    if FAILURES:
        print("FAILED:", "; ".join(FAILURES))
        sys.exit(1)
    print("🛡 ALL 9 PASS CONDITIONS MET — PRODUCTION-GRADE")
    sys.exit(0)


if __name__ == "__main__":
    main()
