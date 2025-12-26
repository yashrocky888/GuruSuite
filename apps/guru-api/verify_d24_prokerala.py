#!/usr/bin/env python3
"""
D24 Prokerala Verification Script
Compares API output vs Prokerala ground truth for D24

Test Birth: 1995-05-16, 18:38 IST, Bangalore (Lahiri Ayanamsa)
"""

import requests
import json

# Prokerala Ground Truth (COMPLETE - ALL PLANETS)
# Birth: 1995-05-16, 18:38 IST, Bangalore (Lahiri Ayanamsa)
PROKERALA_D24 = {
    "Ascendant": "Leo",      # Simha (index 4)
    "Sun": "Leo",            # Simha (index 4)
    "Moon": "Aries",         # Mesha (index 0)
    "Mars": "Virgo",         # Kanya (index 5)
    "Mercury": "Sagittarius", # Dhanu (index 8)
    "Jupiter": "Virgo",      # Kanya (index 5)
    "Venus": "Sagittarius",  # Dhanu (index 8)
    "Saturn": "Cancer",      # Karka (index 3) - CRITICAL MISMATCH: API returns Gemini
    "Rahu": "Pisces",        # Meena (index 11)
    "Ketu": "Pisces",        # Meena (index 11)
}

# Sign index mapping
SIGN_NAMES = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
              "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGN_INDEX = {name: idx for idx, name in enumerate(SIGN_NAMES)}

def get_api_d24():
    """Fetch D24 data from local API"""
    url = "http://localhost:8000/api/v1/kundli"
    params = {
        "dob": "1995-05-16",
        "time": "18:38",
        "lat": 12.9716,
        "lon": 77.5946,
        "timezone": "Asia/Kolkata"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("D24", {})
    except Exception as e:
        print(f"❌ Error fetching API: {e}")
        return None

def compare_d24():
    """Compare API D24 vs Prokerala ground truth"""
    print("=" * 80)
    print("D24 PROKERALA VERIFICATION")
    print("=" * 80)
    print(f"Test Birth: 1995-05-16, 18:38 IST, Bangalore (Lahiri)")
    print()
    
    d24_data = get_api_d24()
    if not d24_data:
        print("❌ Failed to fetch D24 data from API")
        return
    
    print("COMPARISON TABLE:")
    print("-" * 80)
    print(f"{'Planet':<12} {'Prokerala':<15} {'API':<15} {'Match':<10} {'Notes'}")
    print("-" * 80)
    
    mismatches = []
    ascendant_sign = d24_data.get("Ascendant", {}).get("sign", "N/A")
    
    for planet_name in ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        prokerala_sign = PROKERALA_D24.get(planet_name, "?")
        api_planet = d24_data.get("Planets", {}).get(planet_name, {}) if planet_name != "Ascendant" else d24_data.get("Ascendant", {})
        api_sign = api_planet.get("sign", "N/A")
        api_sign_sanskrit = api_planet.get("sign_sanskrit", "")
        
        if prokerala_sign == "?":
            match = "❓ NEEDS VERIFICATION"
            notes = "Prokerala data not available"
        elif api_sign.lower() == prokerala_sign.lower():
            match = "✅ MATCH"
            notes = ""
        else:
            match = "❌ MISMATCH"
            notes = f"CRITICAL: Expected {prokerala_sign}, got {api_sign}"
            mismatches.append((planet_name, prokerala_sign, api_sign))
        
        print(f"{planet_name:<12} {prokerala_sign:<15} {api_sign:<15} {match:<10} {notes}")
    
    print("-" * 80)
    print()
    
    if mismatches:
        print("❌ CRITICAL MISMATCHES FOUND:")
        for planet, expected, actual in mismatches:
            print(f"   {planet}: Expected {expected}, API returned {actual}")
        print()
        print("ACTION REQUIRED:")
        print("1. Verify Prokerala data is correct for this birth")
        print("2. Fix D24 formula in varga_drik.py")
        print("3. Re-test until 100% match")
        print("4. DO NOT mark as verified until ALL planets match")
    else:
        print("✅ ALL 10 PLANETS MATCH PROKERALA EXACTLY")
        print("✅ D24 FORMULA IS CORRECT FOR THIS TEST BIRTH")
        print("✅ VERIFICATION STATUS: PASSED")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    compare_d24()

