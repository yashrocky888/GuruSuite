#!/usr/bin/env python3
"""
Maitreya8 Varga Verification Script
Extracts varga calculation formulas from Maitreya8 and compares with JHora, Prokerala, and our engine.

Repository: https://github.com/martin-pe/maitreya8.git
Language: C++
Main File: src/jyotish/Varga.cpp
"""

import sys
import os
import json
import math
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


def get_rasi(longitude: float) -> int:
    """Get sign index (0-11) from longitude."""
    return int(longitude // 30)


def get_rasi_len(longitude: float) -> float:
    """Get longitude within sign (0-30)."""
    return longitude % 30


def is_odd_rasi(longitude: float) -> bool:
    """Check if sign is odd (0-indexed: 0,2,4,6,8,10 = Aries, Gemini, Leo, Libra, Sagittarius, Aquarius)."""
    rasi = get_rasi(longitude)
    return rasi % 2 == 0


def in_movable_sign(longitude: float) -> bool:
    """Check if in movable sign (Aries, Cancer, Libra, Capricorn = 0, 3, 6, 9)."""
    rasi = get_rasi(longitude)
    return rasi in (0, 3, 6, 9)


def in_fixed_sign(longitude: float) -> bool:
    """Check if in fixed sign (Taurus, Leo, Scorpio, Aquarius = 1, 4, 7, 10)."""
    rasi = get_rasi(longitude)
    return rasi in (1, 4, 7, 10)


def red_deg(deg: float) -> float:
    """Reduce degrees to 0-360 range."""
    return deg % 360


def a_red(deg: float, divisor: float) -> float:
    """Alternative reduction (used in D2)."""
    return deg % divisor


def maitreya8_d2(longitude: float, mode: int = 0) -> int:
    """
    D2 (Hora) - Maitreya8 implementation
    Mode 0: Parasara (default)
    Mode 1: Continuous
    """
    if mode == 0:  # Parasara
        ret = a_red(longitude - 15, 60) + 90
    else:  # Continuous
        ret = 2 * longitude
    return get_rasi(ret)


def maitreya8_d3(longitude: float, mode: int = 0) -> int:
    """
    D3 (Drekkana) - Maitreya8 implementation
    Mode 0: Parasara (default)
    Mode 1: Continuous
    """
    if mode == 0:  # Parasara
        ret = (math.floor(get_rasi_len(longitude) / 10) * 120 + 
               get_rasi(longitude) * 30 + 
               get_rasi_len(3 * longitude))
    else:  # Continuous
        ret = 3 * longitude
    return get_rasi(ret)


def maitreya8_d4(longitude: float, mode: int = 0) -> int:
    """
    D4 (Chaturtamsa) - Maitreya8 implementation
    Mode 0: Parasara (default)
    Mode 1: Continuous
    """
    if mode == 0:  # Parasara
        ret = (math.floor(get_rasi_len(longitude) / 7.5) * 90 + 
               get_rasi(longitude) * 30 + 
               get_rasi_len(4 * longitude))
    else:  # Continuous
        ret = 2 * longitude  # Note: This seems wrong, should be 4 * longitude?
    return get_rasi(ret)


def maitreya8_d7(longitude: float) -> int:
    """D7 (Saptamsa) - Maitreya8 implementation."""
    basepos = get_rasi(longitude) * 30 + get_rasi_len(longitude) * 7
    if is_odd_rasi(longitude):
        ret = basepos
    else:
        ret = basepos + 180
    return get_rasi(ret)


def maitreya8_d9(longitude: float) -> int:
    """D9 (Navamsa) - Maitreya8 implementation."""
    ret = 9 * longitude
    return get_rasi(ret)


def maitreya8_d10(longitude: float) -> int:
    """D10 (Dasamsa) - Maitreya8 implementation."""
    basepos = get_rasi(longitude) * 30 + get_rasi_len(longitude) * 10
    if is_odd_rasi(longitude):
        ret = basepos
    else:
        ret = basepos + 240
    return get_rasi(ret)


def maitreya8_d12(longitude: float) -> int:
    """D12 (Dwadasamsa) - Maitreya8 implementation."""
    # Uses getDvadasamsaLongitude: getRasi(len) * 30 + getRasiLen(len) * 12
    ret = get_rasi(longitude) * 30 + get_rasi_len(longitude) * 12
    return get_rasi(ret)


def maitreya8_d16(longitude: float) -> int:
    """D16 (Shodasamsa) - Maitreya8 implementation."""
    ret = 16 * longitude
    return get_rasi(ret)


def maitreya8_d20(longitude: float) -> int:
    """D20 (Vimsamsa) - Maitreya8 implementation."""
    ret = 20 * longitude
    return get_rasi(ret)


def maitreya8_d24(longitude: float) -> int:
    """D24 (Siddhamsa/Chaturvimsamsa) - Maitreya8 implementation."""
    basepos = get_rasi_len(longitude) * 24
    if is_odd_rasi(longitude):
        ret = basepos + 120  # Leo (120°)
    else:
        ret = basepos + 90   # Cancer (90°)
    return get_rasi(ret)


def maitreya8_d27(longitude: float) -> int:
    """D27 (Bhamsa/Saptavimsamsa) - Maitreya8 implementation."""
    ret = 27 * longitude
    return get_rasi(ret)


def maitreya8_d30(longitude: float) -> int:
    """D30 (Trimsamsa) - Maitreya8 implementation."""
    rs = get_rasi_len(longitude)
    rasi_idx = get_rasi(longitude)
    
    if is_odd_rasi(longitude):
        # Odd signs: Aries, Gemini, Leo, Libra, Sagittarius, Aquarius
        if rs < 5:
            ret = 30 * 0 + rs * 6  # Aries
        elif 5 <= rs <= 10:
            ret = 30 * 10 + (rs - 5) * 6  # Aquarius
        elif 10 <= rs <= 18:
            ret = 30 * 8 + (rs - 10) / 4 * 15  # Sagittarius
        elif 18 <= rs <= 25:
            ret = 30 * 2 + (rs - 18) / 7 * 30  # Gemini
        elif rs > 25:
            ret = 30 * 6 + (rs - 25) * 6  # Libra
    else:
        # Even signs: Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces
        if rs < 5:
            ret = 30 * 1 + (5 - rs) * 6  # Taurus
        elif 5 <= rs <= 10:
            ret = 30 * 5 + (10 - rs) * 6  # Virgo
        elif 10 <= rs <= 18:
            ret = 30 * 11 + (18 - rs) / 4 * 15  # Pisces
        elif 18 <= rs <= 25:
            ret = 30 * 9 + (25 - rs) / 7 * 30  # Capricorn
        elif rs > 25:
            ret = 30 * 7 + (30 - rs) * 6  # Scorpio
    
    return get_rasi(ret)


def maitreya8_d40(longitude: float) -> int:
    """D40 (Chatvarimsamsa/Khavedamsa) - Maitreya8 implementation."""
    basepos = get_rasi_len(longitude) * 40
    if is_odd_rasi(longitude):
        ret = basepos
    else:
        ret = basepos + 180
    return get_rasi(ret)


def maitreya8_d45(longitude: float) -> int:
    """D45 (Akshavedamsa) - Maitreya8 implementation."""
    basepos = get_rasi_len(longitude) * 45
    if in_movable_sign(longitude):
        ret = basepos
    elif in_fixed_sign(longitude):
        ret = basepos + 120
    else:  # Dual sign
        ret = basepos + 240
    return get_rasi(ret)


def maitreya8_d60(longitude: float) -> int:
    """D60 (Shashtiamsa) - Maitreya8 implementation."""
    ret = 60 * get_rasi_len(longitude) + get_rasi(longitude) * 30
    return get_rasi(ret)


def extract_varga_formulas():
    """Extract and document all varga formulas from Maitreya8."""
    print("=" * 100)
    print("MAITREYA8 VARGA FORMULAS EXTRACTED")
    print("=" * 100)
    
    formulas = {
        "D1": {
            "formula": "ret = len (same as D1)",
            "source": "Varga.cpp line 86",
            "notes": "Rasi chart"
        },
        "D2": {
            "formula": "Mode 0 (Parasara): ret = a_red(len - 15, 60) + 90\nMode 1 (Continuous): ret = 2 * len",
            "source": "Varga.cpp lines 95-108",
            "notes": "Two modes available, default is Parasara"
        },
        "D3": {
            "formula": "Mode 0 (Parasara): ret = floor(rasiLen/10)*120 + rasi*30 + rasiLen(3*len)\nMode 1 (Continuous): ret = 3 * len",
            "source": "Varga.cpp lines 111-124",
            "notes": "Two modes available, default is Parasara"
        },
        "D4": {
            "formula": "Mode 0 (Parasara): ret = floor(rasiLen/7.5)*90 + rasi*30 + rasiLen(4*len)\nMode 1 (Continuous): ret = 2 * len",
            "source": "Varga.cpp lines 127-140",
            "notes": "Two modes available, default is Parasara. Note: Mode 1 seems incorrect (should be 4*len?)"
        },
        "D7": {
            "formula": "basepos = rasi*30 + rasiLen*7\nOdd: ret = basepos\nEven: ret = basepos + 180",
            "source": "Varga.cpp lines 149-153",
            "notes": "Odd/even sign dependent"
        },
        "D9": {
            "formula": "ret = 9 * len",
            "source": "Varga.cpp line 91",
            "notes": "Simple multiplication"
        },
        "D10": {
            "formula": "basepos = rasi*30 + rasiLen*10\nOdd: ret = basepos\nEven: ret = basepos + 240",
            "source": "Varga.cpp lines 161-165",
            "notes": "Odd/even sign dependent"
        },
        "D12": {
            "formula": "ret = rasi*30 + rasiLen*12",
            "source": "Varga.cpp lines 168-170",
            "notes": "Uses getDvadasamsaLongitude function"
        },
        "D16": {
            "formula": "ret = 16 * len",
            "source": "Varga.cpp line 174",
            "notes": "Simple multiplication"
        },
        "D20": {
            "formula": "ret = 20 * len",
            "source": "Varga.cpp line 179",
            "notes": "Simple multiplication"
        },
        "D24": {
            "formula": "basepos = rasiLen*24\nOdd: ret = basepos + 120 (Leo)\nEven: ret = basepos + 90 (Cancer)",
            "source": "Varga.cpp lines 183-187",
            "notes": "Odd/even sign dependent, uses longitude_in_sign only"
        },
        "D27": {
            "formula": "ret = 27 * len",
            "source": "Varga.cpp line 191",
            "notes": "Simple multiplication"
        },
        "D30": {
            "formula": "Complex degree-based lookup (odd/even sign dependent)",
            "source": "Varga.cpp lines 195-220",
            "notes": "Uses degree ranges with different signs for odd/even"
        },
        "D40": {
            "formula": "basepos = rasiLen*40\nOdd: ret = basepos\nEven: ret = basepos + 180",
            "source": "Varga.cpp lines 223-227",
            "notes": "Odd/even sign dependent"
        },
        "D45": {
            "formula": "basepos = rasiLen*45\nMovable: ret = basepos\nFixed: ret = basepos + 120\nDual: ret = basepos + 240",
            "source": "Varga.cpp lines 230-235",
            "notes": "Modality-based (movable/fixed/dual)"
        },
        "D60": {
            "formula": "ret = 60*rasiLen + rasi*30",
            "source": "Varga.cpp line 239",
            "notes": "Uses longitude_in_sign and sign index"
        }
    }
    
    print("\nVarga charts implemented in Maitreya8:")
    for varga, info in formulas.items():
        print(f"\n{varga}:")
        print(f"  Formula: {info['formula']}")
        print(f"  Source: {info['source']}")
        print(f"  Notes: {info['notes']}")
    
    print("\n" + "=" * 100 + "\n")
    return formulas


def main():
    """Main verification function."""
    print("=" * 100)
    print("MAITREYA8 VARGA VERIFICATION FRAMEWORK")
    print("=" * 100)
    print("\nThis script extracts varga formulas from Maitreya8 source code.")
    print("To run actual comparisons, Maitreya8 binary must be built and executed.")
    print("\n" + "=" * 100 + "\n")
    
    extract_varga_formulas()
    
    print("\n" + "=" * 100)
    print("NEXT STEPS")
    print("=" * 100)
    print("\n1. Build Maitreya8 from source")
    print("2. Execute Maitreya8 for three verified births")
    print("3. Extract planet→sign outputs for each varga")
    print("4. Compare with JHora and Prokerala")
    print("5. Generate verification report")
    print("=" * 100 + "\n")


if __name__ == "__main__":
    main()

