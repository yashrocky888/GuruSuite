#!/usr/bin/env python3
"""
D3 JHora Pattern Analysis
Analyzes D1 input vs JHora D3 output to reverse-engineer the correct D3 formula.
"""

import requests
import json

# Birth 3 data
BIRTH_3 = {
    "dob": "2001-04-07",
    "time": "11:00",
    "lat": 12.9716,
    "lon": 77.5946,
    "timezone": "Asia/Kolkata"
}

# JHora D3 output for Birth 3
JHORA_D3_BIRTH3 = {
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

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def sign_name_to_index(sign_name: str) -> int:
    """Convert sign name to index (0-11)."""
    sign_lower = sign_name.lower()
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

def get_sign_modality(sign_index: int) -> str:
    """Get sign modality: Movable, Fixed, or Dual."""
    if sign_index in (0, 3, 6, 9):  # Aries, Cancer, Libra, Capricorn
        return "Movable"
    elif sign_index in (1, 4, 7, 10):  # Taurus, Leo, Scorpio, Aquarius
        return "Fixed"
    else:  # Gemini, Virgo, Sagittarius, Pisces
        return "Dual"

def analyze_d3_pattern():
    """Analyze D1 input vs JHora D3 output to derive the correct formula."""
    print("=" * 100)
    print("D3 JHORA PATTERN ANALYSIS - BIRTH 3")
    print("=" * 100)
    
    # Fetch D1 data
    url = "http://localhost:8000/api/v1/kundli"
    params = {
        "dob": BIRTH_3["dob"],
        "time": BIRTH_3["time"],
        "lat": BIRTH_3["lat"],
        "lon": BIRTH_3["lon"],
        "timezone": BIRTH_3["timezone"]
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        d1 = data.get("D1", {})
    except Exception as e:
        print(f"❌ Error fetching D1 data: {e}")
        return
    
    print("\nD1 INPUT DATA:")
    print("-" * 100)
    
    d1_data = {}
    
    # Ascendant
    asc = d1.get("Ascendant", {})
    asc_sign = asc.get("sign", "")
    asc_deg = asc.get("degrees_in_sign", 0.0)
    asc_idx = sign_name_to_index(asc_sign)
    d1_data["Ascendant"] = {"sign": asc_sign, "sign_index": asc_idx, "degrees": asc_deg}
    print(f"Ascendant: {asc_sign} (index {asc_idx}, {asc_deg:.4f}°)")
    
    # Planets
    planets = d1.get("Planets", {})
    for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        p_data = planets.get(planet, {})
        p_sign = p_data.get("sign", "")
        p_deg = p_data.get("degrees_in_sign", 0.0)
        p_idx = sign_name_to_index(p_sign)
        d1_data[planet] = {"sign": p_sign, "sign_index": p_idx, "degrees": p_deg}
        print(f"{planet:<10}: {p_sign:<12} (index {p_idx:2d}, {p_deg:7.4f}°)")
    
    print("\n" + "=" * 100)
    print("JHORA D3 OUTPUT:")
    print("-" * 100)
    
    jhora_d3_data = {}
    for planet, jhora_sign in JHORA_D3_BIRTH3.items():
        jhora_idx = sign_name_to_index(jhora_sign)
        jhora_d3_data[planet] = {"sign": jhora_sign, "sign_index": jhora_idx}
        print(f"{planet:<10}: {jhora_sign:<12} (index {jhora_idx:2d})")
    
    print("\n" + "=" * 100)
    print("PATTERN ANALYSIS:")
    print("-" * 100)
    
    print(f"\n{'Planet':<12} | {'D1 Sign':<12} | {'D1 Deg':<10} | {'Div':<5} | {'JHora D3':<12} | {'Offset':<8} | {'Modality':<10}")
    print("-" * 100)
    
    for planet in ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        d1_info = d1_data[planet]
        jhora_d3_info = jhora_d3_data[planet]
        
        d1_idx = d1_info["sign_index"]
        d1_deg = d1_info["degrees"]
        jhora_d3_idx = jhora_d3_info["sign_index"]
        
        # Calculate division (0, 1, or 2)
        div = int(d1_deg / 10.0)
        if div >= 3:
            div = 2
        
        # Calculate offset
        offset = (jhora_d3_idx - d1_idx) % 12
        if offset > 6:
            offset = offset - 12  # Show negative offset if more intuitive
        
        modality = get_sign_modality(d1_idx)
        
        print(f"{planet:<12} | {d1_info['sign']:<12} | {d1_deg:7.4f}° | {div:5d} | {jhora_d3_info['sign']:<12} | {offset:8d} | {modality:<10}")
    
    print("\n" + "=" * 100)
    print("DERIVED OFFSET PATTERN BY MODALITY AND DIVISION:")
    print("-" * 100)
    
    # Group by modality and division
    pattern = {}
    for planet in ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        d1_info = d1_data[planet]
        jhora_d3_info = jhora_d3_data[planet]
        
        d1_idx = d1_info["sign_index"]
        d1_deg = d1_info["degrees"]
        jhora_d3_idx = jhora_d3_info["sign_index"]
        
        div = int(d1_deg / 10.0)
        if div >= 3:
            div = 2
        
        modality = get_sign_modality(d1_idx)
        
        # Calculate offset (0-11)
        offset = (jhora_d3_idx - d1_idx) % 12
        
        key = (modality, div)
        if key not in pattern:
            pattern[key] = []
        pattern[key].append(offset)
    
    print("\nOffset pattern (modality, division) → offsets observed:")
    for (modality, div), offsets in sorted(pattern.items()):
        unique_offsets = sorted(set(offsets))
        print(f"  ({modality}, div {div}): {unique_offsets} (from {len(offsets)} planets)")
    
    print("\n" + "=" * 100)

if __name__ == "__main__":
    analyze_d3_pattern()

