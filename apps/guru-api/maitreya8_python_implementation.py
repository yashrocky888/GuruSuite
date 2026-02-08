#!/usr/bin/env python3
"""
Maitreya8 Varga Formulas - Python Implementation
Implements Maitreya8 varga calculation formulas extracted from C++ source code.

This is a direct translation of formulas from src/jyotish/Varga.cpp
Used for verification when Maitreya8 binary is not available.
"""

import math
from typing import Dict, Optional

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
    """Check if sign is odd (0-indexed: 0,2,4,6,8,10)."""
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
    return get_rasi(red_deg(ret))


def maitreya8_d3(longitude: float, mode: int = 0) -> int:
    """
    D3 (Drekkana) - Maitreya8 implementation
    Mode 0: Parasara (default)
    Mode 1: Continuous
    
    Formula: floor(rasiLen/10)*120 + rasi*30 + rasiLen(3*len)
    """
    if mode == 0:  # Parasara
        rasi = get_rasi(longitude)
        rasi_len = get_rasi_len(longitude)
        ret = (math.floor(rasi_len / 10) * 120 + 
               rasi * 30 + 
               get_rasi_len(3 * longitude))
    else:  # Continuous
        ret = 3 * longitude
    return get_rasi(red_deg(ret))


def maitreya8_d4(longitude: float, mode: int = 0) -> int:
    """
    D4 (Chaturtamsa) - Maitreya8 implementation
    Mode 0: Parasara (default)
    Mode 1: Continuous
    """
    if mode == 0:  # Parasara
        rasi = get_rasi(longitude)
        rasi_len = get_rasi_len(longitude)
        ret = (math.floor(rasi_len / 7.5) * 90 + 
               rasi * 30 + 
               get_rasi_len(4 * longitude))
    else:  # Continuous
        ret = 2 * longitude  # NOTE: This seems incorrect in source
    return get_rasi(red_deg(ret))


def maitreya8_d7(longitude: float) -> int:
    """D7 (Saptamsa) - Maitreya8 implementation."""
    rasi = get_rasi(longitude)
    rasi_len = get_rasi_len(longitude)
    basepos = rasi * 30 + rasi_len * 7
    if is_odd_rasi(longitude):
        ret = basepos
    else:
        ret = basepos + 180
    return get_rasi(red_deg(ret))


def maitreya8_d9(longitude: float) -> int:
    """D9 (Navamsa) - Maitreya8 implementation."""
    ret = 9 * longitude
    return get_rasi(red_deg(ret))


def maitreya8_d10(longitude: float) -> int:
    """D10 (Dasamsa) - Maitreya8 implementation."""
    rasi = get_rasi(longitude)
    rasi_len = get_rasi_len(longitude)
    basepos = rasi * 30 + rasi_len * 10
    if is_odd_rasi(longitude):
        ret = basepos
    else:
        ret = basepos + 240
    return get_rasi(red_deg(ret))


def maitreya8_d12(longitude: float) -> int:
    """D12 (Dwadasamsa) - Maitreya8 implementation."""
    rasi = get_rasi(longitude)
    rasi_len = get_rasi_len(longitude)
    ret = rasi * 30 + rasi_len * 12
    return get_rasi(red_deg(ret))


def maitreya8_d16(longitude: float) -> int:
    """D16 (Shodasamsa) - Maitreya8 implementation."""
    ret = 16 * longitude
    return get_rasi(red_deg(ret))


def maitreya8_d20(longitude: float) -> int:
    """D20 (Vimsamsa) - Maitreya8 implementation."""
    ret = 20 * longitude
    return get_rasi(red_deg(ret))


def maitreya8_d24(longitude: float) -> int:
    """
    D24 (Siddhamsa/Chaturvimsamsa) - Maitreya8 implementation
    Uses Method 1 (Traditional Parasara Siddhamsa)
    """
    rasi_len = get_rasi_len(longitude)
    basepos = rasi_len * 24
    if is_odd_rasi(longitude):
        ret = basepos + 120  # Leo (120°)
    else:
        ret = basepos + 90   # Cancer (90°)
    return get_rasi(red_deg(ret))


def maitreya8_d27(longitude: float) -> int:
    """D27 (Bhamsa/Saptavimsamsa) - Maitreya8 implementation."""
    ret = 27 * longitude
    return get_rasi(red_deg(ret))


def maitreya8_d30(longitude: float) -> int:
    """D30 (Trimsamsa) - Maitreya8 implementation."""
    rs = get_rasi_len(longitude)
    
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
    
    return get_rasi(red_deg(ret))


def maitreya8_d40(longitude: float) -> int:
    """D40 (Chatvarimsamsa/Khavedamsa) - Maitreya8 implementation."""
    rasi_len = get_rasi_len(longitude)
    basepos = rasi_len * 40
    if is_odd_rasi(longitude):
        ret = basepos
    else:
        ret = basepos + 180
    return get_rasi(red_deg(ret))


def maitreya8_d45(longitude: float) -> int:
    """D45 (Akshavedamsa) - Maitreya8 implementation."""
    rasi_len = get_rasi_len(longitude)
    basepos = rasi_len * 45
    if in_movable_sign(longitude):
        ret = basepos
    elif in_fixed_sign(longitude):
        ret = basepos + 120
    else:  # Dual sign
        ret = basepos + 240
    return get_rasi(red_deg(ret))


def maitreya8_d60(longitude: float) -> int:
    """D60 (Shashtiamsa) - Maitreya8 implementation."""
    rasi = get_rasi(longitude)
    rasi_len = get_rasi_len(longitude)
    ret = 60 * rasi_len + rasi * 30
    return get_rasi(red_deg(ret))


# Varga function mapping
VARGA_FUNCTIONS = {
    2: maitreya8_d2,
    3: maitreya8_d3,
    4: maitreya8_d4,
    7: maitreya8_d7,
    9: maitreya8_d9,
    10: maitreya8_d10,
    12: maitreya8_d12,
    16: maitreya8_d16,
    20: maitreya8_d20,
    24: maitreya8_d24,
    27: maitreya8_d27,
    30: maitreya8_d30,
    40: maitreya8_d40,
    45: maitreya8_d45,
    60: maitreya8_d60,
}


def calculate_maitreya8_varga(longitude: float, varga_type: int, mode: int = 0) -> int:
    """
    Calculate varga sign using Maitreya8 formulas.
    
    Args:
        longitude: Full longitude in degrees (0-360)
        varga_type: Varga type (2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60)
        mode: Calculation mode (0=Parasara default, 1=Continuous for D2/D3/D4)
    
    Returns:
        Sign index (0-11)
    """
    if varga_type not in VARGA_FUNCTIONS:
        raise ValueError(f"Unsupported varga type: {varga_type}")
    
    func = VARGA_FUNCTIONS[varga_type]
    
    # D2, D3, D4 support mode parameter
    if varga_type in (2, 3, 4):
        return func(longitude, mode)
    else:
        return func(longitude)


if __name__ == "__main__":
    # Test with a sample longitude
    test_long = 45.5  # Example: 15°30' in Taurus
    print(f"Test longitude: {test_long}°")
    print(f"Sign: {SIGN_NAMES[get_rasi(test_long)]}")
    print(f"\nMaitreya8 Varga Results:")
    for varga in [3, 9, 24]:
        sign_idx = calculate_maitreya8_varga(test_long, varga)
        print(f"  D{varga}: {SIGN_NAMES[sign_idx]}")

