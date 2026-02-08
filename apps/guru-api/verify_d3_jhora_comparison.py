#!/usr/bin/env python3
"""
D3 (Drekkana) JHora Verification Comparison Script
Compares engine output with JHora ground truth for all three verified births.

VERIFIED BIRTH CHARTS:
1. 16-May-1995, 18:38 IST — Bangalore
2. 07-Apr-1996, 11:59 IST — Bangalore
3. 07-Apr-2001, 11:00 IST — Bangalore

Ayanamsa: Lahiri
Authority: Jagannatha Hora (JHora)
Tolerance: ZERO (even one planet mismatch = FAIL)
"""

import sys
import json
import requests
from typing import Dict, Optional

# VERIFIED BIRTH CHARTS
VERIFIED_BIRTHS = [
    {
        "name": "Birth 1",
        "dob": "1995-05-16",
        "time": "18:38",
        "lat": 12.9716,
        "lon": 77.5946,
        "timezone": "Asia/Kolkata"
    },
    {
        "name": "Birth 2",
        "dob": "1996-04-07",
        "time": "11:59",
        "lat": 12.9716,
        "lon": 77.5946,
        "timezone": "Asia/Kolkata"
    },
    {
        "name": "Birth 3",
        "dob": "2001-04-07",
        "time": "11:00",
        "lat": 12.9716,
        "lon": 77.5946,
        "timezone": "Asia/Kolkata"
    }
]

# JHORA GROUND TRUTH (Fill this with actual JHora visual verification data)
JHORA_GROUND_TRUTH = {
    "Birth 1": {
        "Ascendant": "???",  # Fill from JHora visual verification
        "Sun": "???",
        "Moon": "???",
        "Mars": "???",
        "Mercury": "???",
        "Jupiter": "???",
        "Venus": "???",
        "Saturn": "???",
        "Rahu": "???",
        "Ketu": "???"
    },
    "Birth 2": {
        "Ascendant": "???",
        "Sun": "???",
        "Moon": "???",
        "Mars": "???",
        "Mercury": "???",
        "Jupiter": "???",
        "Venus": "???",
        "Saturn": "???",
        "Rahu": "???",
        "Ketu": "???"
    },
    "Birth 3": {
        "Ascendant": "Gemini",
        "Sun": "Scorpio",
        "Moon": "Aquarius",
        "Mars": "Cancer",
        "Mercury": "Pisces",
        "Jupiter": "Cancer",
        "Venus": "Cancer",
        "Saturn": "Taurus",
        "Rahu": "Libra",
        "Ketu": "Aries"
    }
}

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def normalize_sign_name(sign: str) -> str:
    """Normalize sign name for comparison."""
    sign_lower = sign.lower().strip()
    sign_map = {
        "aries": "Aries", "mesha": "Aries",
        "taurus": "Taurus", "vrishabha": "Taurus",
        "gemini": "Gemini", "mithuna": "Gemini",
        "cancer": "Cancer", "karka": "Cancer", "karkata": "Cancer",
        "leo": "Leo", "simha": "Leo",
        "virgo": "Virgo", "kanya": "Virgo",
        "libra": "Libra", "tula": "Libra",
        "scorpio": "Scorpio", "vrishchika": "Scorpio",
        "sagittarius": "Sagittarius", "dhanu": "Sagittarius",
        "capricorn": "Capricorn", "makara": "Capricorn",
        "aquarius": "Aquarius", "kumbha": "Aquarius",
        "pisces": "Pisces", "meena": "Pisces"
    }
    return sign_map.get(sign_lower, sign)


def fetch_d3_chart(birth: Dict, base_url: str = "http://localhost:8000") -> Optional[Dict]:
    """Fetch D3 chart from API."""
    url = f"{base_url}/api/v1/kundli"
    params = {
        "dob": birth["dob"],
        "time": birth["time"],
        "lat": birth["lat"],
        "lon": birth["lon"],
        "timezone": birth["timezone"]
    }
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("D3", {})
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching D3 for {birth['name']}: {e}")
        return None


def extract_planet_signs(chart_data: Dict) -> Dict[str, str]:
    """Extract planet signs from chart data."""
    planet_signs = {}
    
    # Extract Ascendant
    ascendant = chart_data.get("Ascendant", {})
    if ascendant:
        sign_name = ascendant.get("sign") or ascendant.get("sign_name") or ascendant.get("sign_sanskrit")
        if sign_name:
            planet_signs["Ascendant"] = normalize_sign_name(sign_name)
    
    # Extract planets
    planets = chart_data.get("Planets", {})
    for planet_name, planet_data in planets.items():
        if planet_data:
            sign_name = planet_data.get("sign") or planet_data.get("sign_name") or planet_data.get("sign_sanskrit")
            if sign_name:
                planet_signs[planet_name] = normalize_sign_name(sign_name)
    
    return planet_signs


def print_verification_table(birth_name: str, birth_details: Dict, engine_signs: Dict, jhora_signs: Dict):
    """Print verification table for one birth."""
    all_planets = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    
    print(f"\n{'=' * 100}")
    print(f"VERIFICATION TABLE: {birth_name}")
    print(f"Birth Details: {birth_details['dob']} {birth_details['time']} IST, Bangalore (Lahiri)")
    print(f"{'=' * 100}")
    print(f"{'Planet':<12} | {'JHora Sign':<15} | {'Engine Sign':<15} | {'Status'}")
    print(f"{'-' * 12} | {'-' * 15} | {'-' * 15} | {'-' * 10}")
    
    matches = 0
    mismatches = []
    
    for planet in all_planets:
        engine_sign = engine_signs.get(planet, "MISSING")
        jhora_sign = jhora_signs.get(planet, "MISSING")
        
        if engine_sign == jhora_sign and engine_sign != "MISSING" and jhora_sign != "MISSING":
            status = "✅ MATCH"
            matches += 1
        elif jhora_sign == "???" or jhora_sign == "MISSING":
            status = "⏳ PENDING"
        else:
            status = "❌ FAIL"
            mismatches.append({
                "planet": planet,
                "engine": engine_sign,
                "jhora": jhora_sign
            })
        
        print(f"{planet:<12} | {jhora_sign:<15} | {engine_sign:<15} | {status}")
    
    print(f"{'-' * 100}")
    print(f"Summary: {matches}/{len(all_planets)} planets match")
    
    if mismatches:
        print(f"\n❌ MISMATCHES FOUND ({len(mismatches)}):")
        for mismatch in mismatches:
            print(f"   {mismatch['planet']}: Engine={mismatch['engine']}, JHora={mismatch['jhora']}")
        return False
    elif any(jhora_signs.get(p) == "???" for p in all_planets):
        print(f"\n⏳ VERIFICATION PENDING: JHora data not yet provided")
        return None
    else:
        print(f"\n✅ ALL PLANETS MATCH")
        return True


def main():
    """Main verification function."""
    print("=" * 100)
    print("D3 (DREKKANA) JHORA VERIFICATION REPORT")
    print("=" * 100)
    print("\nAuthority: Jagannatha Hora (JHora)")
    print("Tolerance: ZERO (even one planet mismatch = FAIL)")
    print("\n" + "=" * 100)
    
    # Step 1: Fetch engine data
    print("\n📊 Step 1: Fetching engine D3 data for all three births...")
    engine_data = {}
    
    for birth in VERIFIED_BIRTHS:
        print(f"   Fetching D3 for {birth['name']}...")
        d3_chart = fetch_d3_chart(birth)
        if not d3_chart:
            print(f"   ❌ Failed to fetch D3 for {birth['name']}")
            return False
        
        planet_signs = extract_planet_signs(d3_chart)
        engine_data[birth["name"]] = planet_signs
        print(f"   ✅ Fetched {len(planet_signs)} planets")
    
    # Step 2: Compare with JHora
    print("\n" + "=" * 100)
    print("VERIFICATION COMPARISON (Engine vs JHora)")
    print("=" * 100)
    
    results = {}
    all_verified = True
    has_pending = False
    
    for birth in VERIFIED_BIRTHS:
        birth_name = birth["name"]
        engine_signs = engine_data.get(birth_name, {})
        jhora_signs = JHORA_GROUND_TRUTH.get(birth_name, {})
        
        result = print_verification_table(birth_name, birth, engine_signs, jhora_signs)
        results[birth_name] = result
        
        if result is False:
            all_verified = False
        elif result is None:
            has_pending = True
    
    # Final summary
    print("\n" + "=" * 100)
    print("FINAL VERIFICATION STATUS")
    print("=" * 100)
    
    for birth_name, result in results.items():
        if result is True:
            print(f"✅ {birth_name}: PASS (100% match)")
        elif result is False:
            print(f"❌ {birth_name}: FAIL (mismatches found)")
        else:
            print(f"⏳ {birth_name}: PENDING (JHora data not provided)")
    
    print("\n" + "-" * 100)
    
    if has_pending:
        print("⏳ VERIFICATION INCOMPLETE")
        print("   Please provide JHora ground truth data for all three births.")
        print("   Update JHORA_GROUND_TRUTH in this script and re-run.")
    elif all_verified:
        print("✅ D3 VERIFICATION STATUS: VERIFIED (JHora)")
        print("   All planets match JHora across all three births.")
        print("   D3 math logic is CORRECT and can be marked as VERIFIED.")
    else:
        print("❌ D3 VERIFICATION STATUS: NOT VERIFIED")
        print("   Mismatches found. Math logic must be fixed in varga_drik.py")
        print("   Fix requirements:")
        print("   • Universal rule only (no birth-specific logic)")
        print("   • No exceptions, no hardcoding")
        print("   • Must match JHora 100% for all three births")
    
    print("=" * 100 + "\n")
    
    return all_verified and not has_pending


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

