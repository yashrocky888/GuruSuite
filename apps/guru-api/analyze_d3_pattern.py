#!/usr/bin/env python3
"""
Analyze D3 Pattern - Compare Matching vs Non-Matching Planets
Identifies what makes Moon & Jupiter different from planets that match.
"""

import math
import requests

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Birth 3 data
BIRTH3 = {
    "dob": "2001-04-07",
    "time": "11:00",
    "lat": 12.9716,
    "lon": 77.5946,
    "timezone": "Asia/Kolkata"
}

# Known: Moon & Jupiter mismatch, others match
JHORA_D3_BIRTH3 = {
    "Moon": "Aquarius",      # Our: Capricorn ❌
    "Jupiter": "Cancer"      # Our: Virgo ❌
}

def our_engine_d3(sign_idx: int, deg_in_sign: float) -> int:
    l = int(math.floor(deg_in_sign / 10.0))
    if l >= 3: l = 2
    return (sign_idx + l * 4) % 12

def get_d1_data():
    url = "http://localhost:8000/api/v1/kundli"
    params = {k: BIRTH3[k] for k in ["dob", "time", "lat", "lon", "timezone"]}
    response = requests.get(url, params=params, timeout=30)
    return response.json().get("D1", {})

def analyze_pattern():
    """Analyze what makes Moon & Jupiter different."""
    d1_data = get_d1_data()
    
    print("="*120)
    print("D3 PATTERN ANALYSIS - BIRTH 3")
    print("="*120)
    print("\nComparing planets that MATCH vs planets that MISMATCH:")
    print("-"*120)
    print(f"{'Planet':<12} | {'D1 Sign':<12} | {'Idx':<4} | {'Deg':<8} | {'Div':<4} | {'Our D3':<12} | {'JHora D3':<12} | {'Status'}")
    print("-"*120)
    
    planets_analysis = []
    
    for planet in ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        if planet == "Ascendant":
            pdata = d1_data.get("Ascendant", {})
        else:
            pdata = d1_data.get("Planets", {}).get(planet, {})
        
        if not pdata:
            continue
        
        sign_idx = pdata.get("sign_index", -1)
        deg_in_sign = pdata.get("degrees_in_sign", 0)
        d1_sign = pdata.get("sign", "N/A")
        division = int(deg_in_sign / 10.0)
        
        our_d3_idx = our_engine_d3(sign_idx, deg_in_sign)
        our_d3_sign = SIGN_NAMES[our_d3_idx]
        
        jhora_d3_sign = JHORA_D3_BIRTH3.get(planet, our_d3_sign)  # Assume match if not in mismatch list
        jhora_d3_idx = SIGN_NAMES.index(jhora_d3_sign) if jhora_d3_sign in SIGN_NAMES else our_d3_idx
        
        status = "✅ MATCH" if our_d3_idx == jhora_d3_idx else "❌ MISMATCH"
        
        print(f"{planet:<12} | {d1_sign:<12} | {sign_idx:4} | {deg_in_sign:7.4f}° | {division:4} | {our_d3_sign:<12} | {jhora_d3_sign:<12} | {status}")
        
        planets_analysis.append({
            "planet": planet,
            "d1_sign": d1_sign,
            "d1_idx": sign_idx,
            "deg": deg_in_sign,
            "div": division,
            "our_d3": our_d3_sign,
            "jhora_d3": jhora_d3_sign,
            "matches": our_d3_idx == jhora_d3_idx
        })
    
    print("-"*120)
    
    # Analyze pattern
    print("\n" + "="*120)
    print("PATTERN ANALYSIS")
    print("="*120)
    
    mismatch_planets = [p for p in planets_analysis if not p["matches"]]
    match_planets = [p for p in planets_analysis if p["matches"]]
    
    print(f"\nMismatching planets: {len(mismatch_planets)}")
    for p in mismatch_planets:
        print(f"  {p['planet']}: D1={p['d1_sign']} (idx {p['d1_idx']}), Div={p['div']}, "
              f"Our={p['our_d3']}, JHora={p['jhora_d3']}")
    
    print(f"\nMatching planets: {len(match_planets)}")
    
    # Focus on division 1 planets
    div1_planets = [p for p in planets_analysis if p["div"] == 1]
    print(f"\nDivision 1 planets (10-20°):")
    for p in div1_planets:
        status = "❌" if not p["matches"] else "✅"
        print(f"  {status} {p['planet']}: D1={p['d1_sign']} (idx {p['d1_idx']}), "
              f"Our={p['our_d3']}, JHora={p['jhora_d3']}")
    
    # Analyze what's different
    print("\n" + "="*120)
    print("KEY OBSERVATIONS")
    print("="*120)
    
    div1_mismatch = [p for p in div1_planets if not p["matches"]]
    div1_match = [p for p in div1_planets if p["matches"]]
    
    if div1_mismatch and div1_match:
        print("\nDivision 1 planets that MATCH:")
        for p in div1_match:
            print(f"  {p['planet']}: D1={p['d1_sign']} (idx {p['d1_idx']}) → D3={p['jhora_d3']}")
            print(f"    Our formula: ({p['d1_idx']} + 1*4) % 12 = {(p['d1_idx'] + 4) % 12} ({SIGN_NAMES[(p['d1_idx'] + 4) % 12]}) ✅")
        
        print("\nDivision 1 planets that MISMATCH:")
        for p in div1_mismatch:
            our_idx = (p['d1_idx'] + 4) % 12
            jhora_idx = SIGN_NAMES.index(p['jhora_d3'])
            offset = (jhora_idx - our_idx) % 12
            if offset > 6:
                offset = offset - 12
            print(f"  {p['planet']}: D1={p['d1_sign']} (idx {p['d1_idx']}) → D3={p['jhora_d3']}")
            print(f"    Our formula: ({p['d1_idx']} + 1*4) % 12 = {our_idx} ({SIGN_NAMES[our_idx]}) ❌")
            print(f"    JHora wants: {jhora_idx} ({p['jhora_d3']})")
            print(f"    Offset needed: {offset:+d}")
    
    print("\n" + "="*120)
    print("HYPOTHESIS")
    print("="*120)
    print("\nIf some division 1 planets match and others don't,")
    print("JHora might use a lookup table or sign-specific rule.")
    print("\nHowever, this violates the requirement for ONE universal rule.")
    print("\nAlternative: Maybe JHora uses a different division calculation")
    print("or a different offset pattern that we haven't identified yet.")


if __name__ == "__main__":
    analyze_pattern()

