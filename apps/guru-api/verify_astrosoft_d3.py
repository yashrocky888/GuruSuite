#!/usr/bin/env python3
"""
Astrosoft D3 (Drekkana) Verification Script
Extracts Astrosoft's D3 calculation logic and compares with JHora and our engine.

Astrosoft D3 Logic (from VargaCharts.java, case 3):
- house = (int)(deg / 30)  [sign index, 0-based]
- rem = deg % 30
- Div 0 (0-10°):  house = house + 1
- Div 1 (10-20°): house = house + 5
- Div 2 (20-30°): house = house + 9
- house = house % 12
- Result is 1-based house (1-12), convert to 0-based sign (0-11)
"""

import math
from typing import Dict

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

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def astrosoft_d3_calculate(sign_index: int, degrees_in_sign: float) -> int:
    """
    Calculate D3 using Astrosoft's exact logic.
    
    From VargaCharts.java case 3:
    - house = (int)(deg / 30)  [sign index]
    - rem = deg % 30
    - Div 0 (0-10°):  house = house + 1
    - Div 1 (10-20°): house = house + 5
    - Div 2 (20-30°): house = house + 9
    - house = house % 12
    - Returns 1-based house (1-12), convert to 0-based sign (0-11)
    """
    house = sign_index  # Astrosoft uses (int)(deg / 30) which is sign_index
    rem = degrees_in_sign
    
    if (0.0 <= rem) and (rem < 10.0):
        house = house + 1
    elif (10.0 <= rem) and (rem < 20.0):
        house = house + 5
    elif (20.0 <= rem) and (rem <= 30.0):
        house = house + 9
    
    house = house % 12
    
    # Astrosoft returns 1-based house (1-12), convert to 0-based sign (0-11)
    # If house == 0, it means house 12, which is sign index 11
    if house == 0:
        return 11  # Pisces (12th sign, 0-based index 11)
    else:
        return house - 1  # Convert 1-based house to 0-based sign


def pyjhora_parasara_d3(sign_index: int, degrees_in_sign: float) -> int:
    """
    Calculate D3 using PyJHora Parasara method (chart_method=1).
    Formula: (sign_index + l * 4) % 12 where l = int(degrees_in_sign / 10.0)
    """
    l = int(math.floor(degrees_in_sign / 10.0))
    if l >= 3:
        l = 2
    f2 = 4
    return (sign_index + l * f2) % 12


def print_comparison_table(birth_name: str, d1_data: Dict, jhora_d3: Dict = None):
    """Print comparison table for one birth."""
    print(f"\n{'=' * 100}")
    print(f"D3 COMPARISON: {birth_name}")
    print(f"{'=' * 100}")
    
    print(f"\n{'Planet':<12} | {'D1 Sign':<12} | {'D1 Deg':<10} | {'Astrosoft':<12} | {'PyJHora':<12} | {'JHora':<12} | {'Engine':<12} | {'Match'}")
    print("-" * 100)
    
    # We'll need to fetch engine data and JHora data separately
    # For now, show Astrosoft vs PyJHora comparison
    
    all_planets = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    
    for planet in all_planets:
        if planet not in d1_data:
            continue
            
        d1_info = d1_data[planet]
        sign_idx = d1_info["sign_index"]
        deg = d1_info["degrees"]
        
        astrosoft_result = astrosoft_d3_calculate(sign_idx, deg)
        pyjhora_result = pyjhora_parasara_d3(sign_idx, deg)
        
        jhora_sign = jhora_d3.get(planet, "N/A") if jhora_d3 else "N/A"
        engine_sign = "N/A"  # Will be filled from API
        
        match_status = "?"
        if jhora_d3:
            jhora_idx = sign_name_to_index(jhora_sign) if jhora_sign != "N/A" else -1
            if astrosoft_result == jhora_idx:
                match_status = "✅ ASTRO"
            elif pyjhora_result == jhora_idx:
                match_status = "✅ PYJHORA"
            else:
                match_status = "❌"
        
        print(f"{planet:<12} | {SIGN_NAMES[sign_idx]:<12} | {deg:7.4f}° | {SIGN_NAMES[astrosoft_result]:<12} | {SIGN_NAMES[pyjhora_result]:<12} | {jhora_sign:<12} | {engine_sign:<12} | {match_status}")


def sign_name_to_index(sign_name: str) -> int:
    """Convert sign name to index (0-11)."""
    sign_lower = sign_name.lower().strip()
    sign_map = {
        "aries": 0, "mesha": 0,
        "taurus": 1, "vrishabha": 1,
        "gemini": 2, "mithuna": 2,
        "cancer": 3, "karka": 3, "karkata": 3,
        "leo": 4, "simha": 4,
        "virgo": 5, "kanya": 5,
        "libra": 6, "tula": 6,
        "scorpio": 7, "vrishchika": 7,
        "sagittarius": 8, "dhanu": 8,
        "capricorn": 9, "makara": 9,
        "aquarius": 10, "kumbha": 10,
        "pisces": 11, "meena": 11
    }
    return sign_map.get(sign_lower, -1)


def main():
    """Main function."""
    print("=" * 100)
    print("ASTROSOFT D3 (DREKKANA) VERIFICATION")
    print("=" * 100)
    print("\nAstrosoft D3 Logic:")
    print("  Div 0 (0-10°):  sign + 1")
    print("  Div 1 (10-20°): sign + 5")
    print("  Div 2 (20-30°): sign + 9")
    print("  Result: (sign + offset) % 12")
    print("\nPyJHora Parasara Logic:")
    print("  Div 0 (0-10°):  sign + 0")
    print("  Div 1 (10-20°): sign + 4")
    print("  Div 2 (20-30°): sign + 8")
    print("  Result: (sign + l * 4) % 12")
    
    # Birth 3 JHora data (from previous verification)
    jhora_d3_birth3 = {
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
    
    # Birth 3 D1 data (from previous analysis)
    d1_birth3 = {
        "Ascendant": {"sign_index": 2, "degrees": 7.3987},   # Gemini
        "Sun": {"sign_index": 11, "degrees": 23.5934},      # Pisces
        "Moon": {"sign_index": 5, "degrees": 11.3237},     # Virgo
        "Mars": {"sign_index": 7, "degrees": 28.9574},     # Scorpio
        "Mercury": {"sign_index": 11, "degrees": 7.7565},  # Pisces
        "Jupiter": {"sign_index": 1, "degrees": 14.8664},  # Taurus
        "Venus": {"sign_index": 11, "degrees": 10.9480},    # Pisces
        "Saturn": {"sign_index": 1, "degrees": 4.5711},    # Taurus
        "Rahu": {"sign_index": 2, "degrees": 16.7195},     # Gemini
        "Ketu": {"sign_index": 8, "degrees": 16.7195}      # Sagittarius
    }
    
    print_comparison_table("Birth 3", d1_birth3, jhora_d3_birth3)
    
    print("\n" + "=" * 100)
    print("ANALYSIS:")
    print("=" * 100)
    print("\nComparing Astrosoft vs JHora for Birth 3:")
    
    matches_astrosoft = 0
    matches_pyjhora = 0
    
    for planet in ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        d1_info = d1_birth3[planet]
        sign_idx = d1_info["sign_index"]
        deg = d1_info["degrees"]
        
        astrosoft_result = astrosoft_d3_calculate(sign_idx, deg)
        pyjhora_result = pyjhora_parasara_d3(sign_idx, deg)
        jhora_sign = jhora_d3_birth3[planet]
        jhora_idx = sign_name_to_index(jhora_sign)
        
        astro_match = "✅" if astrosoft_result == jhora_idx else "❌"
        pyjhora_match = "✅" if pyjhora_result == jhora_idx else "❌"
        
        if astrosoft_result == jhora_idx:
            matches_astrosoft += 1
        if pyjhora_result == jhora_idx:
            matches_pyjhora += 1
        
        print(f"{planet:<12}: Astrosoft={SIGN_NAMES[astrosoft_result]:<12} {astro_match} | PyJHora={SIGN_NAMES[pyjhora_result]:<12} {pyjhora_match} | JHora={jhora_sign}")
    
    print(f"\nSummary:")
    print(f"  Astrosoft matches JHora: {matches_astrosoft}/10")
    print(f"  PyJHora matches JHora: {matches_pyjhora}/10")
    
    if matches_astrosoft == 10:
        print(f"\n✅ Astrosoft D3 logic matches JHora 100%")
    elif matches_astrosoft > matches_pyjhora:
        print(f"\n⚠️  Astrosoft D3 logic matches JHora better than PyJHora Parasara method")
    else:
        print(f"\n⚠️  Neither Astrosoft nor PyJHora Parasara matches JHora 100%")
    
    print("=" * 100 + "\n")


if __name__ == "__main__":
    main()

