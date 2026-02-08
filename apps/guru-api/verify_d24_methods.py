#!/usr/bin/env python3
"""
D24 Verification Script (Method 1 - JHora Verified)

D24 is LOCKED to Method 1 (Traditional Parasara Siddhamsa).
This script verifies D24 output against JHora for Method 1 only.

Test Birth:
- DOB: 1995-05-16
- Time: 18:38 IST
- Place: Bangalore (12.9716°N, 77.5946°E)
- Ayanamsa: Lahiri

STATUS: D24 is VERIFIED against Jagannatha Hora (JHora) using Method 1.
"""

import sys
import json
import requests
from typing import Dict

# Test birth data
TEST_BIRTH = {
    "dob": "1995-05-16",
    "time": "18:38",
    "lat": 12.9716,
    "lon": 77.5946,
    "timezone": "Asia/Kolkata"
}

# JHora ground truth (Method 1 - verified)
# D24 is locked to Method 1 and verified against JHora
JHORA_METHOD1_GROUND_TRUTH = {
    "Ascendant": "Leo",
    "Sun": "Leo",
    "Moon": "Aries",
    "Mars": "Virgo",
    "Mercury": "Sagittarius",
    "Jupiter": "Virgo",
    "Venus": "Sagittarius",
    "Saturn": "Cancer",
    "Rahu": "Pisces",
    "Ketu": "Pisces"
}

# Sign index to name mapping
SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def get_sign_name(sign_index: int) -> str:
    """Convert sign index (0-11) to sign name."""
    return SIGN_NAMES[sign_index] if 0 <= sign_index < 12 else "Unknown"


def fetch_d24_chart(base_url: str = "http://localhost:8000") -> Dict:
    """Fetch D24 chart from API (Method 1 is locked, no parameter needed)."""
    url = f"{base_url}/api/v1/kundli"
    params = {
        **TEST_BIRTH
        # d24_chart_method parameter REMOVED - D24 is locked to Method 1
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("D24", {})
    except Exception as e:
        print(f"❌ Error fetching D24 chart: {e}")
        return {}


def extract_planet_signs(d24_data: Dict) -> Dict[str, str]:
    """Extract planet→sign mappings from D24 chart data."""
    planet_signs = {}
    
    # Extract Ascendant
    ascendant = d24_data.get("Ascendant", {})
    if ascendant:
        sign_index = ascendant.get("sign_index")
        if sign_index is not None:
            planet_signs["Ascendant"] = get_sign_name(sign_index)
    
    # Extract planets
    planets = d24_data.get("Planets", {})
    for planet_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        planet = planets.get(planet_name, {})
        if planet:
            sign_index = planet.get("sign_index")
            if sign_index is not None:
                planet_signs[planet_name] = get_sign_name(sign_index)
    
    return planet_signs


def print_verification_table(planet_signs: Dict[str, str]):
    """Print verification table comparing Method 1 with JHora."""
    print("\n" + "=" * 80)
    print("D24 VERIFICATION TABLE (Method 1 - JHora Verified)")
    print("=" * 80)
    print(f"\nTest Birth: {TEST_BIRTH['dob']} {TEST_BIRTH['time']} IST, Bangalore (Lahiri Ayanamsa)")
    print("\n" + "-" * 80)
    
    # Header
    header = f"{'Planet':<12} {'Our Engine':<15} {'JHora (M1)':<15} {'Match':<10}"
    print(header)
    print("-" * 80)
    
    # Planet rows
    planets = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    matches = 0
    total = 0
    
    for planet in planets:
        our_sign = planet_signs.get(planet, "N/A")
        jhora_sign = JHORA_METHOD1_GROUND_TRUTH.get(planet, "N/A")
        match = "✅" if our_sign == jhora_sign else "❌"
        
        if our_sign != "N/A":
            total += 1
            if our_sign == jhora_sign:
                matches += 1
        
        print(f"{planet:<12} {our_sign:<15} {jhora_sign:<15} {match:<10}")
    
    print("-" * 80)
    
    # Summary
    print(f"\nSUMMARY:")
    print(f"  Matches: {matches}/{total} planets")
    print(f"  Status: {'✅ VERIFIED' if matches == total and total == len(planets) else '❌ NOT VERIFIED'}")
    
    print("\n" + "=" * 80)
    print("VERIFICATION RESULT:")
    print("=" * 80)
    
    if matches == total and total == len(planets):
        print("✅ D24 Method 1 matches JHora 100%")
        print("   → D24 is VERIFIED (JHora Method 1)")
    else:
        print(f"⚠️  D24 Method 1 matches {matches}/{total} planets")
        print("   → D24 NOT VERIFIED - Check implementation or JHora data")
    
    print("=" * 80 + "\n")


def main():
    """Main verification function."""
    print("=" * 80)
    print("D24 VERIFICATION (Method 1 - JHora Verified)")
    print("=" * 80)
    print(f"\nTest Birth: {TEST_BIRTH['dob']} {TEST_BIRTH['time']} IST")
    print(f"Place: Bangalore ({TEST_BIRTH['lat']}°N, {TEST_BIRTH['lon']}°E)")
    print(f"Ayanamsa: Lahiri")
    print("\n⚠️  D24 is LOCKED to Method 1 (Traditional Parasara Siddhamsa)")
    print("   No method switching - Method 1 is the only method used.")
    print("-" * 80)
    
    print(f"\n📊 Fetching D24 chart (Method 1)...")
    d24_data = fetch_d24_chart()
    
    if not d24_data:
        print("❌ Failed to fetch D24 data. Check API server.")
        return
    
    planet_signs = extract_planet_signs(d24_data)
    
    print(f"✅ D24 Method 1 results:")
    for planet, sign in sorted(planet_signs.items()):
        expected = JHORA_METHOD1_GROUND_TRUTH.get(planet)
        match = "✅" if sign == expected else "❌"
        print(f"   {planet:<12} → {sign:<15} {match} (JHora: {expected or 'N/A'})")
    
    # Print verification table
    print_verification_table(planet_signs)


if __name__ == "__main__":
    main()
