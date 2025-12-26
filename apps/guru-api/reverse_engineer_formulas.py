#!/usr/bin/env python3
"""
Reverse-engineer D24, D30, D40 formulas from Prokerala data.
"""

import math

# D1 data
D1 = {
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

# Prokerala results
PROK = {
    "D24": {"Ascendant": 4, "Sun": 4, "Moon": 0, "Mars": 5, "Mercury": 8, "Jupiter": 5, "Venus": 8, "Saturn": 2, "Rahu": 11, "Ketu": 11},
    "D30": {"Ascendant": 1, "Sun": 1, "Moon": 7, "Mars": 0, "Mercury": 9, "Jupiter": 11, "Venus": 10, "Saturn": 6, "Rahu": 8, "Ketu": 8},
    "D40": {"Ascendant": 9, "Sun": 8, "Moon": 0, "Mars": 9, "Mercury": 11, "Jupiter": 6, "Venus": 8, "Saturn": 2, "Rahu": 1, "Ketu": 1},
}

print("=" * 80)
print("REVERSE ENGINEERING D24 FORMULA")
print("=" * 80)

for planet, d1_data in D1.items():
    if planet == "Ascendant":
        continue
    si = d1_data["sign_index"]
    li = d1_data["long_in_sign"]
    fl = d1_data["full_long"]
    expected = PROK["D24"][planet]
    
    # Calculate amsa
    amsa = int(math.floor((fl * 24.0) / 30.0)) % 24
    
    # Find what start sign would give the expected result
    # expected = (start + amsa) % 12
    # So: start = (expected - amsa) % 12
    start = (expected - amsa) % 12
    
    print(f"{planet:8s}: sign={si:2d}, long={li:6.2f}, amsa={amsa:2d}, expected={expected:2d}, start={start:2d}")

print("\n" + "=" * 80)
print("REVERSE ENGINEERING D30 FORMULA")
print("=" * 80)

for planet, d1_data in D1.items():
    if planet == "Ascendant":
        continue
    si = d1_data["sign_index"]
    li = d1_data["long_in_sign"]
    expected = PROK["D30"][planet]
    
    # Current D30 logic
    is_odd = (si % 2 == 0)
    if is_odd:
        if li < 5.0:
            current = 0
        elif li < 10.0:
            current = 9
        elif li < 18.0:
            current = 8
        elif li < 25.0:
            current = 2
        else:
            current = 6
    else:
        if li < 5.0:
            current = 6
        elif li < 10.0:
            current = 2
        elif li < 18.0:
            current = 8
        elif li < 25.0:
            current = 9
        else:
            current = 0
    
    match = "✅" if current == expected else "❌"
    print(f"{planet:8s}: sign={si:2d} ({'odd' if is_odd else 'even'}), long={li:6.2f}, current={current:2d}, expected={expected:2d} {match}")

print("\n" + "=" * 80)
print("REVERSE ENGINEERING D40 FORMULA")
print("=" * 80)

for planet, d1_data in D1.items():
    if planet == "Ascendant":
        continue
    si = d1_data["sign_index"]
    li = d1_data["long_in_sign"]
    fl = d1_data["full_long"]
    expected = PROK["D40"][planet]
    
    # Calculate amsa
    amsa = int(math.floor((fl * 40.0) / 30.0)) % 40
    
    # Find what start sign would give the expected result
    start = (expected - amsa) % 12
    
    # Determine sign nature
    if si in (0, 3, 6, 9):
        nature = "movable"
    elif si in (1, 4, 7, 10):
        nature = "fixed"
    else:
        nature = "dual"
    
    print(f"{planet:8s}: sign={si:2d} ({nature}), long={li:6.2f}, amsa={amsa:2d}, expected={expected:2d}, start={start:2d}")

