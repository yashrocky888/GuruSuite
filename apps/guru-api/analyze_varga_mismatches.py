#!/usr/bin/env python3
"""
Analyze varga mismatches to understand formula errors.
"""

import requests
import json

# Prokerala Ground Truth
PROKERALA = {
    "D24": {"Ascendant": 4, "Sun": 4, "Moon": 0, "Mars": 5, "Mercury": 8, "Jupiter": 5, "Venus": 8, "Saturn": 2, "Rahu": 11, "Ketu": 11},
    "D30": {"Ascendant": 1, "Sun": 1, "Moon": 7, "Mars": 0, "Mercury": 9, "Jupiter": 11, "Venus": 10, "Saturn": 6, "Rahu": 8, "Ketu": 8},
    "D40": {"Ascendant": 9, "Sun": 8, "Moon": 0, "Mars": 9, "Mercury": 11, "Jupiter": 6, "Venus": 8, "Saturn": 2, "Rahu": 1, "Ketu": 1},
}

# Sign names
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

def get_d1_data():
    """Get D1 data from API"""
    api_url = "https://guru-api-660206747784.asia-south1.run.app/api/v1/kundli"
    params = {"dob": "1995-05-16", "time": "18:38", "lat": 12.9716, "lon": 77.5946, "timezone": "Asia/Kolkata"}
    response = requests.get(api_url, params=params, timeout=30)
    data = response.json()
    kundli = data.get("data", {}).get("kundli", {}) or data
    d1 = kundli.get("D1", {})
    return d1

def analyze():
    api_url = "https://guru-api-660206747784.asia-south1.run.app/api/v1/kundli"
    params = {"dob": "1995-05-16", "time": "18:38", "lat": 12.9716, "lon": 77.5946, "timezone": "Asia/Kolkata"}
    response = requests.get(api_url, params=params, timeout=30)
    data = response.json()
    kundli = data.get("data", {}).get("kundli", {}) or data
    
    d1 = kundli.get("D1", {})
    
    print("=" * 80)
    print("D1 DATA (Base for varga calculations)")
    print("=" * 80)
    asc = d1.get("Ascendant", {})
    print(f"Ascendant: {asc.get('sign_sanskrit')} (sign_index={asc.get('sign_index')}, degree={asc.get('degree')}, long_in_sign={asc.get('degrees_in_sign')})")
    
    planets = d1.get("Planets", {})
    for name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        p = planets.get(name, {})
        print(f"{name:8s}: {p.get('sign_sanskrit'):12s} (sign_index={p.get('sign_index'):2d}, degree={p.get('degree'):8.4f}, long_in_sign={p.get('degrees_in_sign'):6.4f})")
    
    print("\n" + "=" * 80)
    print("VARGA MISMATCH ANALYSIS")
    print("=" * 80)
    
    for varga in ["D24", "D30", "D40"]:
        print(f"\n{varga} MISMATCHES:")
        chart = kundli.get(varga, {})
        if not chart:
            print(f"  {varga} not found in response")
            continue
        
        prokerala = PROKERALA[varga]
        
        # Ascendant
        asc_api = chart.get("Ascendant", {})
        asc_api_idx = asc_api.get("sign_index", -1)
        asc_prok_idx = prokerala["Ascendant"]
        if asc_api_idx != asc_prok_idx:
            print(f"  Ascendant: API={SIGNS[asc_api_idx]} ({asc_api_idx}), Prokerala={SIGNS[asc_prok_idx]} ({asc_prok_idx}), diff={asc_prok_idx - asc_api_idx}")
        
        # Planets
        planets = chart.get("Planets", {})
        for name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            p = planets.get(name, {})
            api_idx = p.get("sign_index", -1)
            prok_idx = prokerala.get(name, -1)
            if api_idx != prok_idx:
                print(f"  {name:8s}: API={SIGNS[api_idx]} ({api_idx}), Prokerala={SIGNS[prok_idx]} ({prok_idx}), diff={prok_idx - api_idx}")

if __name__ == "__main__":
    analyze()

