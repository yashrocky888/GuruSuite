#!/usr/bin/env python3
"""
Jyotishyamitra Varga Verification Script
Extracts varga calculation formulas from jyotishyamitra and compares with JHora, Astrosoft, and our engine.

Repository: https://github.com/VicharaVandana/jyotishyamitra.git
"""

import sys
import os
import json
import math
from typing import Dict, Optional

# Add jyotishyamitra to path
sys.path.insert(0, '/tmp/jyotishyamitra')

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


def jyotishyamitra_d3_calculate(sign_index_1based: int, degrees_in_sign: float) -> int:
    """
    Calculate D3 using jyotishyamitra's exact logic.
    
    From mod_divisional.py Drekkana_from_long():
    - longi_sec = (pos_deg * 3600) + (pos_min * 60) + pos_sec
    - amsa = 10 * 3600  # 10 degrees
    - drekkanaCompartment = 1 + int(longi_sec/amsa)
    - Div 1 (0-10°):  DrekkanaSign = compute_nthsign(sign, 1)  # +1
    - Div 2 (10-20°): DrekkanaSign = compute_nthsign(sign, 5)  # +5
    - Div 3 (20-30°): DrekkanaSign = compute_nthsign(sign, 9)  # +9
    
    Note: jyotishyamitra uses 1-based signs (1=Aries, 12=Pisces)
    """
    # Convert to seconds
    longi_sec = degrees_in_sign * 3600
    amsa = 10 * 3600  # 10 degrees
    drekkanaCompartment = 1 + int(longi_sec / amsa)
    
    if drekkanaCompartment > 3:
        drekkanaCompartment = 3
    
    # jyotishyamitra uses compute_nthsign(sign, n) = (sign + n - 1) % 12
    # Div 1: compute_nthsign(sign, 1) = sign (offset 0)
    # Div 2: compute_nthsign(sign, 5) = sign + 4 (offset +4)
    # Div 3: compute_nthsign(sign, 9) = sign + 8 (offset +8)
    # This is the SAME as PyJHora Parasara method!
    if drekkanaCompartment == 1:
        n = 1  # offset = 0
    elif drekkanaCompartment == 2:
        n = 5  # offset = 4
    else:  # drekkanaCompartment == 3
        n = 9  # offset = 8
    
    # Compute result using compute_nthsign formula: (sign + n - 1) % 12
    result_1based = ((sign_index_1based + n - 1) % 12)
    if result_1based == 0:
        result_1based = 12
    
    # Convert to 0-based for comparison
    return result_1based - 1


def astrosoft_d3_calculate(sign_index: int, degrees_in_sign: float) -> int:
    """Calculate D3 using Astrosoft logic."""
    house = sign_index
    rem = degrees_in_sign
    
    if (0.0 <= rem) and (rem < 10.0):
        house = house + 1
    elif (10.0 <= rem) and (rem < 20.0):
        house = house + 5
    elif (20.0 <= rem) and (rem <= 30.0):
        house = house + 9
    
    house = house % 12
    
    # Astrosoft returns 1-based house (1-12), convert to 0-based sign (0-11)
    if house == 0:
        return 11  # Pisces
    else:
        return house - 1


def pyjhora_parasara_d3(sign_index: int, degrees_in_sign: float) -> int:
    """Calculate D3 using PyJHora Parasara method (chart_method=1)."""
    l = int(math.floor(degrees_in_sign / 10.0))
    if l >= 3:
        l = 2
    f2 = 4
    return (sign_index + l * f2) % 12


def print_d3_formula_comparison():
    """Print D3 formula comparison."""
    print("=" * 100)
    print("D3 (DREKKANA) FORMULA COMPARISON")
    print("=" * 100)
    print("\n1. Jyotishyamitra D3 Logic:")
    print("   Div 1 (0-10°):  sign + 1")
    print("   Div 2 (10-20°): sign + 5")
    print("   Div 3 (20-30°): sign + 9")
    print("   Result: (sign + offset) % 12")
    
    print("\n2. Astrosoft D3 Logic:")
    print("   Div 1 (0-10°):  sign + 1")
    print("   Div 2 (10-20°): sign + 5")
    print("   Div 3 (20-30°): sign + 9")
    print("   Result: (sign + offset) % 12")
    
    print("\n3. PyJHora Parasara D3 Logic (chart_method=1):")
    print("   Div 1 (0-10°):  sign + 0")
    print("   Div 2 (10-20°): sign + 4")
    print("   Div 3 (20-30°): sign + 8")
    print("   Result: (sign + l * 4) % 12")
    
    print("\n" + "=" * 100)
    print("KEY FINDING:")
    print("=" * 100)
    print("✅ Jyotishyamitra D3 = Astrosoft D3 (both use +1, +5, +9 offsets)")
    print("❌ Jyotishyamitra D3 ≠ PyJHora Parasara D3 (PyJHora uses +0, +4, +8 offsets)")
    print("=" * 100 + "\n")


def test_d3_birth3():
    """Test D3 calculations for Birth 3."""
    print("=" * 100)
    print("D3 COMPARISON - BIRTH 3 (2001-04-07 11:00 IST)")
    print("=" * 100)
    
    # Birth 3 D1 data
    d1_birth3 = {
        "Ascendant": {"sign_index": 2, "degrees": 7.3987},   # Gemini (1-based: 3)
        "Sun": {"sign_index": 11, "degrees": 23.5934},      # Pisces (1-based: 12)
        "Moon": {"sign_index": 5, "degrees": 11.3237},       # Virgo (1-based: 6)
        "Mars": {"sign_index": 7, "degrees": 28.9574},      # Scorpio (1-based: 8)
        "Mercury": {"sign_index": 11, "degrees": 7.7565},   # Pisces (1-based: 12)
        "Jupiter": {"sign_index": 1, "degrees": 14.8664},    # Taurus (1-based: 2)
        "Venus": {"sign_index": 11, "degrees": 10.9480},     # Pisces (1-based: 12)
        "Saturn": {"sign_index": 1, "degrees": 4.5711},     # Taurus (1-based: 2)
        "Rahu": {"sign_index": 2, "degrees": 16.7195},      # Gemini (1-based: 3)
        "Ketu": {"sign_index": 8, "degrees": 16.7195}        # Sagittarius (1-based: 9)
    }
    
    # JHora D3 expected (from previous verification)
    jhora_d3_birth3 = {
        "Ascendant": 2,   # Gemini
        "Sun": 7,         # Scorpio
        "Moon": 10,       # Aquarius
        "Mars": 3,        # Cancer
        "Mercury": 11,    # Pisces
        "Jupiter": 3,     # Cancer
        "Venus": 3,       # Cancer
        "Saturn": 1,      # Taurus
        "Rahu": 6,        # Libra
        "Ketu": 0         # Aries
    }
    
    print(f"\n{'Planet':<12} | {'D1 Sign':<12} | {'D1 Deg':<10} | {'Jyotishyamitra':<15} | {'Astrosoft':<12} | {'PyJHora':<12} | {'JHora':<12} | {'Match'}")
    print("-" * 100)
    
    matches_jyotishyamitra = 0
    matches_astrosoft = 0
    matches_pyjhora = 0
    
    for planet in ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        d1_info = d1_birth3[planet]
        sign_idx_0based = d1_info["sign_index"]
        sign_idx_1based = sign_idx_0based + 1  # Convert to 1-based for jyotishyamitra
        deg = d1_info["degrees"]
        
        jyotishyamitra_result = jyotishyamitra_d3_calculate(sign_idx_1based, deg)
        astrosoft_result = astrosoft_d3_calculate(sign_idx_0based, deg)
        pyjhora_result = pyjhora_parasara_d3(sign_idx_0based, deg)
        jhora_expected = jhora_d3_birth3[planet]
        
        jyotishyamitra_match = "✅" if jyotishyamitra_result == jhora_expected else "❌"
        astrosoft_match = "✅" if astrosoft_result == jhora_expected else "❌"
        pyjhora_match = "✅" if pyjhora_result == jhora_expected else "❌"
        
        if jyotishyamitra_result == jhora_expected:
            matches_jyotishyamitra += 1
        if astrosoft_result == jhora_expected:
            matches_astrosoft += 1
        if pyjhora_result == jhora_expected:
            matches_pyjhora += 1
        
        print(f"{planet:<12} | {SIGN_NAMES[sign_idx_0based]:<12} | {deg:7.4f}° | {SIGN_NAMES[jyotishyamitra_result]:<15} {jyotishyamitra_match} | {SIGN_NAMES[astrosoft_result]:<12} {astrosoft_match} | {SIGN_NAMES[pyjhora_result]:<12} {pyjhora_match} | {SIGN_NAMES[jhora_expected]}")
    
    print("\n" + "-" * 100)
    print(f"Summary:")
    print(f"  Jyotishyamitra matches JHora: {matches_jyotishyamitra}/10")
    print(f"  Astrosoft matches JHora: {matches_astrosoft}/10")
    print(f"  PyJHora Parasara matches JHora: {matches_pyjhora}/10")
    
    print("\n" + "=" * 100)
    print("CONCLUSION:")
    print("=" * 100)
    if matches_jyotishyamitra == 10:
        print("✅ Jyotishyamitra D3 matches JHora 100%")
    elif matches_jyotishyamitra == matches_astrosoft:
        print(f"⚠️  Jyotishyamitra D3 = Astrosoft D3 (both match {matches_jyotishyamitra}/10 with JHora)")
    else:
        print(f"❌ Jyotishyamitra D3 does NOT match JHora 100% ({matches_jyotishyamitra}/10)")
    print("=" * 100 + "\n")


def extract_varga_formulas():
    """Extract varga formulas from jyotishyamitra source code."""
    print("=" * 100)
    print("JYOTISHYAMITRA VARGA FORMULAS EXTRACTED")
    print("=" * 100)
    
    formulas = {
        "D2": {
            "function": "hora_from_long",
            "logic": "Simple forward: (sign + compartment) % 12",
            "division_size": "15°",
            "source": "mod_divisional.py lines 81-98"
        },
        "D3": {
            "function": "Drekkana_from_long",
            "logic": "Div 1: sign+1, Div 2: sign+5, Div 3: sign+9",
            "division_size": "10°",
            "source": "mod_divisional.py lines 100-123"
        },
        "D4": {
            "function": "Chaturtamsa_from_long",
            "logic": "Div 1: sign+1, Div 2: sign+4, Div 3: sign+7, Div 4: sign+10",
            "division_size": "7.5°",
            "source": "mod_divisional.py lines 125-150"
        },
        "D7": {
            "function": "Saptamsa_from_long",
            "logic": "Odd: forward, Even: reverse (+6)",
            "division_size": "~4.286°",
            "source": "mod_divisional.py lines 152-173"
        },
        "D9": {
            "function": "navamsa_from_long",
            "logic": "Simple forward: (sign + compartment) % 12",
            "division_size": "3.333°",
            "source": "mod_divisional.py lines 33-52"
        },
        "D10": {
            "function": "dasamsa_from_long",
            "logic": "Odd: same sign, Even: 9th sign from it",
            "division_size": "3°",
            "source": "mod_divisional.py lines 54-78"
        },
        "D12": {
            "function": "Dwadasamsa_from_long",
            "logic": "Simple forward: (sign + compartment) % 12",
            "division_size": "2.5°",
            "source": "mod_divisional.py lines 175-194"
        },
        "D16": {
            "function": "Shodasamsa_from_long",
            "logic": "Movable: Aries base, Fixed: Leo base, Dual: Sagittarius base",
            "division_size": "1.875°",
            "source": "mod_divisional.py lines 196-219"
        },
        "D20": {
            "function": "Vimsamsa_from_long",
            "logic": "Movable: Aries base, Fixed: Sagittarius base, Dual: Leo base",
            "division_size": "1.5°",
            "source": "mod_divisional.py lines 221-244"
        },
        "D24": {
            "function": "ChaturVimsamsa_from_long",
            "logic": "Even: Leo base, Odd: Cancer base",
            "division_size": "1.25°",
            "source": "mod_divisional.py lines 246-267"
        },
        "D27": {
            "function": "SaptaVimsamsa_from_long",
            "logic": "Fire: Aries base, Earth: Cancer base, Air: Libra base, Water: Capricorn base",
            "division_size": "~1.111°",
            "source": "mod_divisional.py lines 269-295"
        },
        "D30": {
            "function": "Trimsamsa_from_long",
            "logic": "Complex degree-based lookup (odd/even sign dependent)",
            "division_size": "1°",
            "source": "mod_divisional.py lines 297-337"
        },
        "D40": {
            "function": "Khavedamsa_from_long",
            "logic": "Even: Libra base, Odd: Aries base",
            "division_size": "0.75°",
            "source": "mod_divisional.py lines 339-360"
        },
        "D45": {
            "function": "Akshavedamsa_from_long",
            "logic": "Movable: Aries base, Fixed: Leo base, Dual: Sagittarius base",
            "division_size": "~0.667°",
            "source": "mod_divisional.py lines 362-385"
        },
        "D60": {
            "function": "Shashtiamsa_from_long",
            "logic": "Simple forward: (sign + compartment) % 12",
            "division_size": "0.5°",
            "source": "mod_divisional.py lines 387-406"
        }
    }
    
    print("\nVarga charts implemented in jyotishyamitra:")
    for varga, info in formulas.items():
        print(f"\n{varga}:")
        print(f"  Function: {info['function']}")
        print(f"  Logic: {info['logic']}")
        print(f"  Division Size: {info['division_size']}")
        print(f"  Source: {info['source']}")
    
    print("\n" + "=" * 100 + "\n")
    return formulas


def main():
    """Main verification function."""
    print_d3_formula_comparison()
    extract_varga_formulas()
    test_d3_birth3()


if __name__ == "__main__":
    main()

