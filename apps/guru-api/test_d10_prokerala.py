#!/usr/bin/env python3
"""
Test D10 (Dasamsa) chart against Prokerala reference
DOB: 1995-05-16 18:38 IST, Bangalore
"""

import requests
import json
from typing import Dict, Any

# Prokerala Reference Data (Expected)
PROKERALA_D10_REFERENCE = {
    "Lagna": {"sign": "Karka", "sign_num": 4, "house": 4},
    "Sun": {"sign": "Vrischika", "sign_num": 8, "house": 8},
    "Moon": {"sign": "Dhanu", "sign_num": 9, "house": 9},
    "Mercury": {"sign": "Meena", "sign_num": 12, "house": 12},
    "Venus": {"sign": "Kumbha", "sign_num": 11, "house": 11},
    "Mars": {"sign": "Meena", "sign_num": 12, "house": 12},
    "Jupiter": {"sign": "Vrischika", "sign_num": 8, "house": 8},
    "Saturn": {"sign": "Vrischika", "sign_num": 8, "house": 8},
    "Rahu": {"sign": "Vrischika", "sign_num": 8, "house": 8},
    "Ketu": {"sign": "Karka", "sign_num": 4, "house": 4},
}

# Sign name mapping (Sanskrit to English)
SIGN_MAP = {
    "Mesha": "Aries", "Vrishabha": "Taurus", "Mithuna": "Gemini",
    "Karka": "Cancer", "Simha": "Leo", "Kanya": "Virgo",
    "Tula": "Libra", "Vrishchika": "Scorpio", "Vrischika": "Scorpio",
    "Dhanu": "Sagittarius", "Makara": "Capricorn", "Kumbha": "Aquarius",
    "Meena": "Pisces"
}

def normalize_sign_name(sign: str) -> str:
    """Normalize sign name to match reference"""
    # Check if already in reference format
    if sign in ["Karka", "Vrischika", "Dhanu", "Meena", "Kumbha"]:
        return sign
    
    # Convert English to Sanskrit if needed
    reverse_map = {v: k for k, v in SIGN_MAP.items()}
    return reverse_map.get(sign, sign)

def test_d10_prokerala_match(api_url: str = None):
    """
    Test D10 chart against Prokerala reference
    
    Args:
        api_url: API base URL (if None, uses localhost)
    """
    if api_url is None:
        api_url = "http://localhost:8080"
    
    # Test birth data
    birth_data = {
        "name": "Test User",
        "birth_date": "1995-05-16",
        "birth_time": "18:38:00",
        "birth_latitude": 12.9716,  # Bangalore
        "birth_longitude": 77.5946,
        "birth_place": "Bangalore",
        "timezone": "Asia/Kolkata"
    }
    
    print("=" * 80)
    print("🧪 D10 PROKERALA VERIFICATION TEST")
    print("=" * 80)
    print(f"\n📅 Birth Data:")
    print(f"   Date: {birth_data['birth_date']}")
    print(f"   Time: {birth_data['birth_time']} IST")
    print(f"   Place: {birth_data['birth_place']} ({birth_data['birth_latitude']}, {birth_data['birth_longitude']})")
    print(f"\n🌐 API URL: {api_url}")
    
    # Make API request
    try:
        # The endpoint is GET /kundli with query parameters
        print(f"\n📡 Calling API: {api_url}/kundli")
        response = requests.get(
            f"{api_url}/kundli",
            params={
                "dob": birth_data["birth_date"],
                "time": birth_data["birth_time"],
                "lat": birth_data["birth_latitude"],
                "lon": birth_data["birth_longitude"],
                "timezone": birth_data["timezone"]
            },
            timeout=30
        )
        response.raise_for_status()
        response.raise_for_status()
        data = response.json()
        
        # Extract D10 chart
        if "D10" not in data:
            print("\n❌ ERROR: D10 chart not found in API response")
            print(f"Available keys: {list(data.keys())}")
            return False
        
        d10_data = data["D10"]
        print("\n✅ API Response Received")
        
        # Extract planets
        planets = d10_data.get("planets", {})
        ascendant_sign = d10_data.get("ascendant_sign_sanskrit") or d10_data.get("ascendant_sign")
        ascendant_house = d10_data.get("ascendant_house")
        
        print(f"\n📊 D10 Chart Data:")
        print(f"   Ascendant Sign: {ascendant_sign}")
        print(f"   Ascendant House: {ascendant_house}")
        
        # Verify results
        all_match = True
        errors = []
        
        print("\n" + "=" * 80)
        print("🔍 VERIFICATION RESULTS")
        print("=" * 80)
        
        # Check Ascendant
        expected_lagna = PROKERALA_D10_REFERENCE["Lagna"]
        normalized_asc_sign = normalize_sign_name(ascendant_sign)
        
        if normalized_asc_sign != expected_lagna["sign"]:
            print(f"\n❌ LAGNA MISMATCH:")
            print(f"   Expected: {expected_lagna['sign']} (House {expected_lagna['house']})")
            print(f"   Got:      {normalized_asc_sign} (House {ascendant_house})")
            all_match = False
            errors.append(f"Lagna: Expected {expected_lagna['sign']}, got {normalized_asc_sign}")
        else:
            print(f"\n✅ LAGNA: {normalized_asc_sign} → House {ascendant_house} (Expected: {expected_lagna['sign']} → House {expected_lagna['house']})")
        
        # Check each planet
        for planet_name, expected in PROKERALA_D10_REFERENCE.items():
            if planet_name == "Lagna":
                continue  # Already checked
            
            planet_data = planets.get(planet_name)
            if not planet_data:
                print(f"\n❌ {planet_name}: NOT FOUND in API response")
                all_match = False
                errors.append(f"{planet_name}: Not found in API")
                continue
            
            api_sign = planet_data.get("sign_sanskrit") or planet_data.get("sign")
            api_house = planet_data.get("house")
            api_sign_index = planet_data.get("sign_index")
            
            # Normalize sign name
            normalized_sign = normalize_sign_name(api_sign)
            
            # Check sign match
            sign_match = normalized_sign == expected["sign"]
            
            # Check house match (house should equal sign number)
            house_match = api_house == expected["house"]
            
            # CRITICAL ASSERTION: house must equal sign (Whole Sign system)
            # sign_index is 0-11, house should be sign_index + 1
            expected_house_from_sign = api_sign_index + 1 if api_sign_index is not None else None
            house_equals_sign = api_house == expected_house_from_sign if expected_house_from_sign else False
            
            if not house_equals_sign:
                print(f"❌ {planet_name:8s}: HOUSE ≠ SIGN VIOLATION")
                print(f"      Sign Index: {api_sign_index}, Expected House: {expected_house_from_sign}, Got House: {api_house}")
                all_match = False
                errors.append(f"{planet_name}: house ({api_house}) != sign ({api_sign_index + 1 if api_sign_index is not None else 'N/A'})")
            
            if sign_match and house_match and house_equals_sign:
                print(f"✅ {planet_name:8s}: {normalized_sign:12s} → House {api_house:2d} (Expected: {expected['sign']:12s} → House {expected['house']:2d}) [house == sign ✓]")
            elif sign_match and house_match:
                print(f"⚠️  {planet_name:8s}: {normalized_sign:12s} → House {api_house:2d} (Expected: {expected['sign']:12s} → House {expected['house']:2d}) [house != sign ✗]")
            else:
                print(f"❌ {planet_name:8s}: MISMATCH")
                print(f"      Expected: {expected['sign']:12s} → House {expected['house']:2d}")
                print(f"      Got:      {normalized_sign:12s} → House {api_house:2d}")
                all_match = False
                errors.append(f"{planet_name}: Expected {expected['sign']} H{expected['house']}, got {normalized_sign} H{api_house}")
        
        # Final summary
        print("\n" + "=" * 80)
        if all_match:
            print("✅ ALL CHECKS PASSED - D10 MATCHES PROKERALA 100%")
            print("✅ WHOLE SIGN SYSTEM VERIFIED: house == sign for all planets")
            print("=" * 80)
            return True
        else:
            print("❌ VERIFICATION FAILED - MISMATCHES FOUND")
            print("=" * 80)
            print("\n📋 Errors Summary:")
            for error in errors:
                print(f"   • {error}")
            return False
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ API REQUEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    
    # Check if API URL provided
    api_url = None
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
    
    # Run test
    success = test_d10_prokerala_match(api_url)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

