#!/usr/bin/env python3
"""
D3 (Drekkana) Verification Script
Compares engine output with JHora ground truth for D3.

VERIFIED BIRTH CHARTS (GROUND TRUTH):
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

# JHORA GROUND TRUTH (Fill this with actual JHora data)
# Format: { "Birth Name": { "Planet": "Sign", ... } }
JHORA_GROUND_TRUTH = {
    "Birth 1": {
        "Ascendant": "???",  # Fill from JHora
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


def compare_d3_results():
    """Compare D3 engine output with JHora ground truth."""
    print("=" * 100)
    print("D3 (DREKKANA) VERIFICATION — ENGINE vs JHORA")
    print("=" * 100)
    
    print("\n📊 Step 1: Fetching engine data for all three births...")
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
    
    # Display engine data
    print("\n" + "=" * 100)
    print("CURRENT ENGINE OUTPUT (for reference)")
    print("=" * 100)
    all_planets = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    for birth in VERIFIED_BIRTHS:
        birth_name = birth["name"]
        engine_signs = engine_data.get(birth_name, {})
        print(f"\n{birth_name} ({birth['dob']} {birth['time']} IST):")
        for planet in all_planets:
            sign = engine_signs.get(planet, "MISSING")
            print(f"  {planet:<12} → {sign}")
    
    # Check if JHora data is filled
    has_placeholders = any(
        "???" in str(v) 
        for birth_data in JHORA_GROUND_TRUTH.values() 
        for v in birth_data.values()
    )
    
    if has_placeholders:
        print("\n" + "=" * 100)
        print("⚠️  JHORA GROUND TRUTH DATA REQUIRED")
        print("=" * 100)
        print("\n   Please provide JHora planet→sign data for comparison.")
        print("   You can:")
        print("   1. Fill JHORA_GROUND_TRUTH in this script, OR")
        print("   2. Provide the data in any format and I'll structure it")
        print("\n   Required for each birth:")
        print("   • Birth 1: 1995-05-16 18:38 IST Bangalore")
        print("   • Birth 2: 1996-04-07 11:59 IST Bangalore")
        print("   • Birth 3: 2001-04-07 11:00 IST Bangalore")
        print("\n   Format: { 'Birth 1': { 'Ascendant': 'Leo', 'Sun': 'Aries', ... } }")
        print("\n   Once provided, I'll update the script and run comparison.")
        return False
    
    print("\n" + "=" * 100)
    print("COMPARISON RESULTS")
    print("=" * 100)
    
    all_planets = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    all_verified = True
    
    for birth in VERIFIED_BIRTHS:
        birth_name = birth["name"]
        engine_signs = engine_data.get(birth_name, {})
        jhora_signs = JHORA_GROUND_TRUTH.get(birth_name, {})
        
        print(f"\n{birth_name} ({birth['dob']} {birth['time']} IST):")
        print("-" * 100)
        
        matches = []
        mismatches = []
        
        for planet in all_planets:
            engine_sign = engine_signs.get(planet, "MISSING")
            jhora_sign = jhora_signs.get(planet, "MISSING")
            
            if engine_sign == jhora_sign and engine_sign != "MISSING":
                matches.append(planet)
                print(f"  {planet:<12} → {engine_sign:<15} ✅")
            else:
                mismatches.append({
                    "planet": planet,
                    "engine": engine_sign,
                    "jhora": jhora_sign
                })
                status = "❌ MISMATCH" if engine_sign != "MISSING" and jhora_sign != "MISSING" else "⚠️ MISSING"
                print(f"  {planet:<12} → Engine: {engine_sign:<15} JHora: {jhora_sign:<15} {status}")
        
        match_count = len(matches)
        total_count = len([p for p in all_planets if engine_signs.get(p) or jhora_signs.get(p)])
        
        print(f"\n  Summary: {match_count}/{total_count} planets match")
        
        if mismatches:
            all_verified = False
            print(f"  ❌ {len(mismatches)} MISMATCHES FOUND")
        else:
            print(f"  ✅ ALL PLANETS MATCH")
    
    print("\n" + "=" * 100)
    if all_verified:
        print("✅ D3 VERIFICATION STATUS: VERIFIED")
        print("   All planets match JHora across all three births.")
        print("   D3 math logic is CORRECT.")
    else:
        print("❌ D3 VERIFICATION STATUS: NOT VERIFIED")
        print("   Mismatches found. Math logic must be fixed in varga_drik.py")
        print("   Fix requirements:")
        print("   • Universal rule only (no birth-specific logic)")
        print("   • No exceptions, no hardcoding")
        print("   • Must match JHora 100% for all three births")
    print("=" * 100 + "\n")
    
    return all_verified


def main():
    """Main function."""
    success = compare_d3_results()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

