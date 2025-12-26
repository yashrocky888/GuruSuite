#!/usr/bin/env python3
"""
Test different D24, D30, D40 formula variations to find the correct one.
"""

import math

# D1 data for test birth
D1_DATA = {
    "Ascendant": {"sign_index": 7, "long_in_sign": 2.2799, "full_long": 212.2799},
    "Sun": {"sign_index": 1, "long_in_sign": 1.4138, "full_long": 31.4138},
    "Moon": {"sign_index": 7, "long_in_sign": 25.2501, "full_long": 235.2501},
    "Mars": {"sign_index": 4, "long_in_sign": 2.2504, "full_long": 122.2504},
    "Mercury": {"sign_index": 1, "long_in_sign": 22.1178, "full_long": 52.1178},
    "Jupiter": {"sign_index": 7, "long_in_sign": 18.6872, "full_long": 228.6872},
    "Venus": {"sign_index": 0, "long_in_sign": 5.6886, "full_long": 5.6886},
    "Saturn": {"sign_index": 10, "long_in_sign": 28.8956, "full_long": 328.8956},
    "Rahu": {"sign_index": 6, "long_in_sign": 10.7944, "full_long": 190.7944},
    "Ketu": {"sign_index": 0, "long_in_sign": 10.7944, "full_long": 10.7944},
}

# Prokerala ground truth
PROKERALA = {
    "D24": {"Ascendant": 4, "Sun": 4, "Moon": 0, "Mars": 5, "Mercury": 8, "Jupiter": 5, "Venus": 8, "Saturn": 2, "Rahu": 11, "Ketu": 11},
    "D30": {"Ascendant": 1, "Sun": 1, "Moon": 7, "Mars": 0, "Mercury": 9, "Jupiter": 11, "Venus": 10, "Saturn": 6, "Rahu": 8, "Ketu": 8},
    "D40": {"Ascendant": 9, "Sun": 8, "Moon": 0, "Mars": 9, "Mercury": 11, "Jupiter": 6, "Venus": 8, "Saturn": 2, "Rahu": 1, "Ketu": 1},
}

def test_d24_variations():
    """Test different D24 formula variations"""
    print("=" * 80)
    print("D24 FORMULA VARIATIONS")
    print("=" * 80)
    
    variations = [
        ("Current (odd→Leo, even→Aries)", lambda si, li, fl: d24_current(si, li, fl)),
        ("Reversed (odd→Aries, even→Leo)", lambda si, li, fl: d24_reversed(si, li, fl)),
        ("Always Leo start", lambda si, li, fl: d24_always_leo(si, li, fl)),
        ("Always Aries start", lambda si, li, fl: d24_always_aries(si, li, fl)),
        ("By nature (movable→Aries, fixed→Leo, dual→Sag)", lambda si, li, fl: d24_by_nature(si, li, fl)),
        ("By nature reversed", lambda si, li, fl: d24_by_nature_rev(si, li, fl)),
    ]
    
    for name, func in variations:
        matches = 0
        total = 0
        print(f"\n{name}:")
        for planet, d1 in D1_DATA.items():
            if planet == "Ascendant":
                continue
            result = func(d1["sign_index"], d1["long_in_sign"], d1["full_long"])
            expected = PROKERALA["D24"].get(planet, -1)
            total += 1
            match = "✅" if result == expected else "❌"
            if result == expected:
                matches += 1
            print(f"  {planet:8s}: Got {result:2d}, Expected {expected:2d} {match}")
        print(f"  Match rate: {matches}/{total} ({matches*100/total:.1f}%)")

def d24_current(sign_index, long_in_sign, full_longitude):
    """Current D24 formula"""
    amsa = int(math.floor((full_longitude * 24.0) / 30.0)) % 24
    if sign_index % 2 == 0:  # Odd sign
        start = 4  # Leo
    else:  # Even sign
        start = 0  # Aries
    return (start + amsa) % 12

def d24_reversed(sign_index, long_in_sign, full_longitude):
    """Reversed D24 formula"""
    amsa = int(math.floor((full_longitude * 24.0) / 30.0)) % 24
    if sign_index % 2 == 0:  # Odd sign
        start = 0  # Aries
    else:  # Even sign
        start = 4  # Leo
    return (start + amsa) % 12

def d24_always_leo(sign_index, long_in_sign, full_longitude):
    """Always Leo start"""
    amsa = int(math.floor((full_longitude * 24.0) / 30.0)) % 24
    return (4 + amsa) % 12

def d24_always_aries(sign_index, long_in_sign, full_longitude):
    """Always Aries start"""
    amsa = int(math.floor((full_longitude * 24.0) / 30.0)) % 24
    return (0 + amsa) % 12

def d24_by_nature(sign_index, long_in_sign, full_longitude):
    """D24 by sign nature"""
    amsa = int(math.floor((full_longitude * 24.0) / 30.0)) % 24
    if sign_index in (0, 3, 6, 9):  # Movable
        start = 0  # Aries
    elif sign_index in (1, 4, 7, 10):  # Fixed
        start = 4  # Leo
    else:  # Dual
        start = 8  # Sagittarius
    return (start + amsa) % 12

def d24_by_nature_rev(sign_index, long_in_sign, full_longitude):
    """D24 by sign nature (reversed)"""
    amsa = int(math.floor((full_longitude * 24.0) / 30.0)) % 24
    if sign_index in (0, 3, 6, 9):  # Movable
        start = 4  # Leo
    elif sign_index in (1, 4, 7, 10):  # Fixed
        start = 0  # Aries
    else:  # Dual
        start = 8  # Sagittarius
    return (start + amsa) % 12

if __name__ == "__main__":
    test_d24_variations()

