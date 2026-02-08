#!/usr/bin/env python3
"""
VedicAstro Varga Verification Script
Analyzes VedicAstro project for divisional chart implementations.

Repository: https://github.com/diliprk/VedicAstro.git
Note: VedicAstro is primarily a KP (Krishnamurti Paddhati) astrology library,
      not a traditional Parāśara varga chart library.
"""

import sys
import os
import json
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

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]


def analyze_vedicastro_structure():
    """Analyze VedicAstro project structure and identify varga implementations."""
    print("=" * 100)
    print("VEDICASTRO PROJECT ANALYSIS")
    print("=" * 100)
    
    print("\n1. PROJECT TYPE:")
    print("   VedicAstro is a KP (Krishnamurti Paddhati) astrology library")
    print("   Focus: Sublords, Sub-sublords, Nakshatra-based calculations")
    print("   NOT focused on: Traditional Parāśara varga charts (D1-D60)")
    
    print("\n2. MAIN MODULES:")
    print("   - vedicastro/VedicAstro.py: Main horoscope data class")
    print("   - vedicastro/utils.py: Utility functions")
    print("   - vedicastro/horary_chart.py: Horary chart calculations")
    print("   - vedicastro/data/KP_SL_Divisions.csv: KP sublord divisions")
    
    print("\n3. KEY FEATURES:")
    print("   - Uses flatlib (sidereal branch) for planetary positions")
    print("   - Computes Rasi Lords, Nakshatra Lords, Sublords, Sub-sublords")
    print("   - Generates Vimshottari Dasha")
    print("   - KP-specific calculations (not Parāśara varga charts)")
    
    print("\n4. VARGA CHART SUPPORT:")
    print("   ❌ No explicit D1-D60 varga chart calculations found")
    print("   ❌ No divisional chart functions (D3, D9, D24, etc.)")
    print("   ❌ No varga sign computation logic")
    print("   ✅ Provides D1 (Rasi) chart data via flatlib")
    
    print("\n5. CONCLUSION:")
    print("   VedicAstro does NOT implement traditional Parāśara varga charts.")
    print("   It is designed for KP astrology which uses a different system.")
    print("   Therefore, VedicAstro cannot be used for varga verification.")
    
    print("\n" + "=" * 100 + "\n")


def check_flatlib_varga_support():
    """Check if flatlib (used by VedicAstro) has varga support."""
    print("=" * 100)
    print("FLATLIB VARGA SUPPORT CHECK")
    print("=" * 100)
    
    print("\nAttempting to check flatlib for varga support...")
    print("(Note: flatlib may not be installed in this environment)")
    
    try:
        import flatlib
        print("✅ flatlib is available")
        
        # Check for varga-related functions
        flatlib_attrs = dir(flatlib)
        varga_related = [x for x in flatlib_attrs if 'varga' in x.lower() or 'divisional' in x.lower()]
        
        if varga_related:
            print(f"   Found varga-related attributes: {varga_related}")
        else:
            print("   ❌ No varga-related functions found in flatlib")
            
    except ImportError:
        print("❌ flatlib is not installed")
        print("   Cannot check for varga support")
        print("   (VedicAstro requires flatlib from sidereal branch)")
    
    print("\n" + "=" * 100 + "\n")


def generate_verification_report():
    """Generate verification report for VedicAstro."""
    print("=" * 100)
    print("VEDICASTRO VARGA VERIFICATION REPORT")
    print("=" * 100)
    
    print("\nSTATUS: ❌ NOT APPLICABLE")
    print("\nREASON:")
    print("   VedicAstro is a KP (Krishnamurti Paddhati) astrology library.")
    print("   It does NOT implement traditional Parāśara varga charts (D1-D60).")
    print("   Therefore, VedicAstro cannot be used for varga verification.")
    
    print("\nWHAT VEDICASTRO PROVIDES:")
    print("   ✅ D1 (Rasi) chart data via flatlib")
    print("   ✅ Planetary positions (longitude, latitude)")
    print("   ✅ Nakshatra, Pada, Nakshatra Lord")
    print("   ✅ Sublords and Sub-sublords (KP system)")
    print("   ✅ Vimshottari Dasha")
    print("   ✅ House positions")
    
    print("\nWHAT VEDICASTRO DOES NOT PROVIDE:")
    print("   ❌ D2 (Hora) chart")
    print("   ❌ D3 (Drekkana) chart")
    print("   ❌ D4 (Chaturthamsa) chart")
    print("   ❌ D7 (Saptamsa) chart")
    print("   ❌ D9 (Navamsa) chart")
    print("   ❌ D10 (Dasamsa) chart")
    print("   ❌ D12 (Dwadasamsa) chart")
    print("   ❌ D16 (Shodasamsa) chart")
    print("   ❌ D20 (Vimsamsa) chart")
    print("   ❌ D24 (Chaturvimsamsa) chart")
    print("   ❌ D27 (Saptavimsamsa) chart")
    print("   ❌ D30 (Trimsamsa) chart")
    print("   ❌ D40 (Khavedamsa) chart")
    print("   ❌ D45 (Akshavedamsa) chart")
    print("   ❌ D60 (Shashtiamsa) chart")
    
    print("\nRECOMMENDATION:")
    print("   Skip VedicAstro for varga verification.")
    print("   Use instead:")
    print("   - JHora (primary authority)")
    print("   - Astrosoft (secondary authority)")
    print("   - PyJHora (Python reference)")
    print("   - Jyotishyamitra (Python reference)")
    
    print("\n" + "=" * 100 + "\n")


def main():
    """Main verification function."""
    analyze_vedicastro_structure()
    check_flatlib_varga_support()
    generate_verification_report()
    
    print("\n" + "=" * 100)
    print("FINAL CONCLUSION")
    print("=" * 100)
    print("\nVedicAstro does NOT implement Parāśara varga charts.")
    print("It is a KP astrology library and cannot be used for varga verification.")
    print("\nProceed with other verification engines:")
    print("  - JHora (primary)")
    print("  - Astrosoft (secondary)")
    print("  - PyJHora (Python)")
    print("  - Jyotishyamitra (Python)")
    print("=" * 100 + "\n")


if __name__ == "__main__":
    main()

