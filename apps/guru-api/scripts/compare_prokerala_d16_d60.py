#!/usr/bin/env python3
"""
Compare D16-D60 outputs with Prokerala reference data
and generate fix instructions.

Usage:
    python scripts/compare_prokerala_d16_d60.py > current_outputs.txt
    # Then manually compare with Prokerala and update PROKERALA_REFERENCE below
    python scripts/compare_prokerala_d16_d60.py --verify
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.jyotish.varga_engine import build_varga_chart
from src.jyotish.kundli_engine import generate_kundli
from src.utils.timezone import local_to_utc
from src.utils.converters import get_sign_name
import swisseph as swe
from datetime import datetime
import json

# Test birth data (same as D10/D12 verification)
TEST_DOB = datetime(1995, 5, 16, 18, 38, 0)
TEST_LAT = 12.9716
TEST_LON = 77.5946
TEST_TIMEZONE = 'Asia/Kolkata'

# PROKERALA REFERENCE DATA (to be populated from Prokerala website)
# Format: {varga: {planet: {"sign": str, "sign_index": int, "house": int}}}
PROKERALA_REFERENCE = {
    16: {},  # D16 - TO BE POPULATED
    20: {},  # D20 - TO BE POPULATED
    24: {},  # D24 - TO BE POPULATED
    27: {},  # D27 - TO BE POPULATED
    30: {},  # D30 - TO BE POPULATED
    40: {},  # D40 - TO BE POPULATED
    45: {},  # D45 - TO BE POPULATED
    60: {},  # D60 - TO BE POPULATED
}


def get_d1_data():
    """Generate D1 kundli for test birth data"""
    birth_dt_utc = local_to_utc(TEST_DOB, TEST_TIMEZONE)
    jd = swe.julday(
        birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day,
        birth_dt_utc.hour + birth_dt_utc.minute / 60.0,
        swe.GREG_CAL
    )
    kundli = generate_kundli(jd, TEST_LAT, TEST_LON)
    d1_ascendant = kundli["Ascendant"]["degree"]
    d1_planets = {
        planet_name: planet_info["degree"]
        for planet_name, planet_info in kundli["Planets"].items()
    }
    return d1_ascendant, d1_planets


def print_current_outputs():
    """Print current D16-D60 outputs for manual comparison with Prokerala"""
    d1_ascendant, d1_planets = get_d1_data()
    
    print("=" * 80)
    print("CURRENT D16-D60 OUTPUTS (for Prokerala comparison)")
    print("=" * 80)
    print(f"Test Birth Data: {TEST_DOB.strftime('%Y-%m-%d %H:%M')} IST, Bangalore")
    print(f"D1 Ascendant: {get_sign_name(int(d1_ascendant / 30))} ({d1_ascendant:.4f}°)")
    print()
    
    planets_to_check = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
    
    for varga_type in [16, 20, 24, 27, 30, 40, 45, 60]:
        varga_chart = build_varga_chart(d1_planets, d1_ascendant, varga_type)
        asc = varga_chart['ascendant']
        
        print(f"D{varga_type} Ascendant: {asc['sign']} (index {asc['sign_index']}, house {asc['house']})")
        
        for planet_name in planets_to_check:
            if planet_name in varga_chart['planets']:
                p = varga_chart['planets'][planet_name]
                print(f"  {planet_name:8s}: {p['sign']:12s} (index {p['sign_index']:2d}, house {p['house']:2d})")
        print()


def verify_against_prokerala():
    """Verify current outputs against Prokerala reference data"""
    d1_ascendant, d1_planets = get_d1_data()
    
    print("=" * 80)
    print("VERIFICATION AGAINST PROKERALA REFERENCE")
    print("=" * 80)
    
    all_match = True
    
    for varga_type in [16, 20, 24, 27, 30, 40, 45, 60]:
        if varga_type not in PROKERALA_REFERENCE or not PROKERALA_REFERENCE[varga_type]:
            print(f"D{varga_type}: ⚠️  No Prokerala reference data available")
            continue
        
        varga_chart = build_varga_chart(d1_planets, d1_ascendant, varga_type)
        reference = PROKERALA_REFERENCE[varga_type]
        
        print(f"\nD{varga_type}:")
        
        # Check Ascendant
        if "Ascendant" in reference:
            asc_ref = reference["Ascendant"]
            asc_actual = varga_chart["ascendant"]
            
            if asc_actual["sign_index"] == asc_ref["sign_index"]:
                print(f"  ✅ Ascendant: {asc_actual['sign']} (index {asc_actual['sign_index']})")
            else:
                print(f"  ❌ Ascendant: Expected {asc_ref['sign']} (index {asc_ref['sign_index']}), got {asc_actual['sign']} (index {asc_actual['sign_index']})")
                all_match = False
        
        # Check planets
        for planet_name, planet_ref in reference.items():
            if planet_name == "Ascendant":
                continue
            
            if planet_name not in varga_chart["planets"]:
                print(f"  ⚠️  {planet_name}: Not found in chart")
                continue
            
            planet_actual = varga_chart["planets"][planet_name]
            
            if planet_actual["sign_index"] == planet_ref["sign_index"]:
                print(f"  ✅ {planet_name}: {planet_actual['sign']} (index {planet_actual['sign_index']}, house {planet_actual['house']})")
            else:
                print(f"  ❌ {planet_name}: Expected {planet_ref['sign']} (index {planet_ref['sign_index']}), got {planet_actual['sign']} (index {planet_actual['sign_index']})")
                all_match = False
    
    print()
    if all_match:
        print("✅ All varga charts match Prokerala reference!")
    else:
        print("❌ Some varga charts do not match Prokerala reference. Fixes needed.")
    
    return all_match


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        verify_against_prokerala()
    else:
        print_current_outputs()
        print()
        print("=" * 80)
        print("NEXT STEPS:")
        print("=" * 80)
        print("1. Visit: https://www.prokerala.com/astrology/divisional-charts.php")
        print("2. Enter test birth data: 1995-05-16 18:38 IST, Bangalore")
        print("3. Copy Prokerala outputs for D16-D60")
        print("4. Update PROKERALA_REFERENCE in this script")
        print("5. Run: python scripts/compare_prokerala_d16_d60.py --verify")
        print("6. Fix formulas in varga_drik.py to match Prokerala")

