#!/usr/bin/env python3
"""
D24 Method Verification Script

Tests all three D24 chart_methods (1, 2, 3) against test birth data.
Outputs planet→sign mappings for comparison with Prokerala/JHora.

Test Birth:
- DOB: 1995-05-16
- Time: 18:38 IST
- Place: Bangalore (12.9716°N, 77.5946°E)
- Ayanamsa: Lahiri
"""

import sys
import json
import requests
from typing import Dict, List

# Test birth data
TEST_BIRTH = {
    "dob": "1995-05-16",
    "time": "18:38",
    "lat": 12.9716,
    "lon": 77.5946,
    "timezone": "Asia/Kolkata"
}

# Prokerala ground truth (for comparison)
PROKERALA_GROUND_TRUTH = {
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


def fetch_d24_chart(chart_method: int, base_url: str = "http://localhost:8000") -> Dict:
    """Fetch D24 chart from API with specified chart_method."""
    url = f"{base_url}/api/v1/kundli"
    params = {
        **TEST_BIRTH,
        "d24_chart_method": chart_method
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("D24", {})
    except Exception as e:
        print(f"❌ Error fetching D24 chart_method={chart_method}: {e}")
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


def compare_with_prokerala(planet_signs: Dict[str, str], method: int) -> Dict[str, bool]:
    """Compare planet signs with Prokerala ground truth."""
    matches = {}
    for planet, sign in planet_signs.items():
        expected = PROKERALA_GROUND_TRUTH.get(planet)
        matches[planet] = (sign == expected) if expected else None
    return matches


def print_verification_table(all_results: Dict[int, Dict[str, str]]):
    """Print verification table comparing all three methods."""
    print("\n" + "=" * 100)
    print("D24 METHOD VERIFICATION TABLE")
    print("=" * 100)
    print(f"\nTest Birth: {TEST_BIRTH['dob']} {TEST_BIRTH['time']} IST, Bangalore (Lahiri Ayanamsa)")
    print("\n" + "-" * 100)
    
    # Header
    header = f"{'Planet':<12} {'Method 1':<15} {'Method 2':<15} {'Method 3':<15} {'Prokerala':<15} {'Match':<10}"
    print(header)
    print("-" * 100)
    
    # Planet rows
    planets = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    for planet in planets:
        m1_sign = all_results.get(1, {}).get(planet, "N/A")
        m2_sign = all_results.get(2, {}).get(planet, "N/A")
        m3_sign = all_results.get(3, {}).get(planet, "N/A")
        prokerala_sign = PROKERALA_GROUND_TRUTH.get(planet, "N/A")
        
        # Determine which method matches
        match_status = ""
        if m1_sign == prokerala_sign:
            match_status = "Method 1 ✅"
        elif m2_sign == prokerala_sign:
            match_status = "Method 2 ✅"
        elif m3_sign == prokerala_sign:
            match_status = "Method 3 ✅"
        else:
            match_status = "None ❌"
        
        print(f"{planet:<12} {m1_sign:<15} {m2_sign:<15} {m3_sign:<15} {prokerala_sign:<15} {match_status:<10}")
    
    print("-" * 100)
    
    # Summary
    print("\nSUMMARY:")
    for method in [1, 2, 3]:
        method_signs = all_results.get(method, {})
        matches = sum(1 for planet in planets 
                     if method_signs.get(planet) == PROKERALA_GROUND_TRUTH.get(planet))
        total = len([p for p in planets if method_signs.get(p)])
        print(f"  Method {method}: {matches}/{total} planets match Prokerala")
    
    # Identify matching method
    print("\n" + "=" * 100)
    print("VERIFICATION RESULT:")
    print("=" * 100)
    
    best_method = None
    best_matches = 0
    for method in [1, 2, 3]:
        method_signs = all_results.get(method, {})
        matches = sum(1 for planet in planets 
                     if method_signs.get(planet) == PROKERALA_GROUND_TRUTH.get(planet))
        if matches > best_matches:
            best_matches = matches
            best_method = method
    
    if best_matches == len(planets):
        print(f"✅ Method {best_method} matches Prokerala 100% ({best_matches}/{len(planets)} planets)")
        print(f"   → D24 verified using chart_method = {best_method}")
    elif best_matches > 0:
        print(f"⚠️  Method {best_method} matches {best_matches}/{len(planets)} planets")
        print(f"   → D24 NOT VERIFIED - No method matches 100%")
    else:
        print("❌ No method matches Prokerala")
        print("   → D24 NOT VERIFIED - Check ayanamsa, birth data, or Prokerala method")
    
    print("=" * 100 + "\n")


def main():
    """Main verification function."""
    print("=" * 100)
    print("D24 CHART METHOD VERIFICATION")
    print("=" * 100)
    print(f"\nTest Birth: {TEST_BIRTH['dob']} {TEST_BIRTH['time']} IST")
    print(f"Place: Bangalore ({TEST_BIRTH['lat']}°N, {TEST_BIRTH['lon']}°E)")
    print(f"Ayanamsa: Lahiri")
    print("\nTesting all three chart_methods (1, 2, 3)...")
    print("-" * 100)
    
    all_results = {}
    
    # Test each method
    for method in [1, 2, 3]:
        print(f"\n📊 Fetching D24 chart_method={method}...")
        d24_data = fetch_d24_chart(method)
        
        if not d24_data:
            print(f"❌ Failed to fetch D24 data for method {method}")
            continue
        
        planet_signs = extract_planet_signs(d24_data)
        all_results[method] = planet_signs
        
        print(f"✅ Method {method} results:")
        for planet, sign in sorted(planet_signs.items()):
            expected = PROKERALA_GROUND_TRUTH.get(planet)
            match = "✅" if sign == expected else "❌"
            print(f"   {planet:<12} → {sign:<15} {match} (Prokerala: {expected or 'N/A'})")
    
    # Print verification table
    if all_results:
        print_verification_table(all_results)
    else:
        print("\n❌ Failed to fetch any D24 data. Check API server.")


if __name__ == "__main__":
    main()

