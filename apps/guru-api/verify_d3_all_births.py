#!/usr/bin/env python3
"""
Verify D3 against all three births
Tests the JHora D3 implementation across all verified births.
"""

import sys
import os
import requests
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.dirname(__file__))

from jyotish.varga_drik import calculate_varga_sign

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

VERIFIED_BIRTHS = [
    {"name": "Birth 1", "dob": "1995-05-16", "time": "18:38", "lat": 12.9716, "lon": 77.5946, "timezone": "Asia/Kolkata"},
    {"name": "Birth 2", "dob": "1996-04-07", "time": "11:59", "lat": 12.9716, "lon": 77.5946, "timezone": "Asia/Kolkata"},
    {"name": "Birth 3", "dob": "2001-04-07", "time": "11:00", "lat": 12.9716, "lon": 77.5946, "timezone": "Asia/Kolkata"}
]

PLANETS = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

def get_d1_data(birth):
    """Fetch D1 data from API."""
    url = "http://localhost:8000/api/v1/kundli"
    params = {k: birth[k] for k in ["dob", "time", "lat", "lon", "timezone"]}
    try:
        response = requests.get(url, params=params, timeout=30)
        return response.json().get("D1", {})
    except:
        return {}

def get_d3_data(birth):
    """Fetch D3 data from API."""
    url = "http://localhost:8000/api/v1/kundli"
    params = {k: birth[k] for k in ["dob", "time", "lat", "lon", "timezone"]}
    try:
        response = requests.get(url, params=params, timeout=30)
        return response.json().get("D3", {})
    except:
        return {}

def verify_d3_birth(birth):
    """Verify D3 for a single birth."""
    print(f"\n{'='*120}")
    print(f"VERIFYING D3 FOR: {birth['name']} ({birth['dob']} {birth['time']} IST)")
    print(f"{'='*120}")
    
    d1_data = get_d1_data(birth)
    d3_data = get_d3_data(birth)
    
    if not d1_data or not d3_data:
        print("❌ Failed to fetch data")
        return False
    
    print(f"\n{'Planet':<12} | {'D1 Sign':<12} | {'Deg':<8} | {'Div':<4} | {'Our D3':<12} | {'API D3':<12} | {'Match'}")
    print("-"*120)
    
    all_match = True
    match_count = 0
    
    for planet in PLANETS:
        if planet == "Ascendant":
            d1_pdata = d1_data.get("Ascendant", {})
            d3_pdata = d3_data.get("Ascendant", {})
        else:
            d1_pdata = d1_data.get("Planets", {}).get(planet, {})
            d3_pdata = d3_data.get("Planets", {}).get(planet, {})
        
        if not d1_pdata or not d3_pdata:
            continue
        
        sign_idx = d1_pdata.get("sign_index", -1)
        deg_in_sign = d1_pdata.get("degrees_in_sign", 0)
        d1_sign = d1_pdata.get("sign", "N/A")
        division = int(deg_in_sign / 10.0)
        
        # Calculate using our function
        our_d3_idx = calculate_varga_sign(sign_idx, deg_in_sign, "D3")
        our_d3_sign = SIGN_NAMES[our_d3_idx]
        
        # Get from API
        api_d3_sign = d3_pdata.get("sign", "N/A")
        api_d3_idx = SIGN_NAMES.index(api_d3_sign) if api_d3_sign in SIGN_NAMES else -1
        
        match = our_d3_idx == api_d3_idx
        status = "✅" if match else "❌"
        
        if match:
            match_count += 1
        else:
            all_match = False
        
        print(f"{planet:<12} | {d1_sign:<12} | {deg_in_sign:7.4f}° | {division:4} | {our_d3_sign:<12} | {api_d3_sign:<12} | {status}")
    
    print("-"*120)
    print(f"Match Rate: {match_count}/10 planets")
    
    if all_match:
        print(f"✅ {birth['name']}: ALL PLANETS MATCH")
    else:
        print(f"❌ {birth['name']}: SOME MISMATCHES")
    
    return all_match

def main():
    """Verify D3 for all three births."""
    print("="*120)
    print("D3 VERIFICATION - ALL THREE BIRTHS")
    print("="*120)
    print("\nTesting JHora D3 implementation against API output...")
    print("(This verifies internal consistency, not JHora match)")
    
    all_births_pass = True
    for birth in VERIFIED_BIRTHS:
        if not verify_d3_birth(birth):
            all_births_pass = False
    
    print("\n" + "="*120)
    print("VERIFICATION SUMMARY")
    print("="*120)
    
    if all_births_pass:
        print("✅ Internal consistency: PASS (all planets match API)")
        print("⏳ JHora verification: PENDING (need JHora ground truth for all 3 births)")
    else:
        print("❌ Internal consistency: FAIL (some mismatches found)")
    
    print("\n⚠️ NOTE: This verifies internal consistency only.")
    print("Full verification requires JHora ground truth for all 3 births.")
    print("="*120 + "\n")

if __name__ == "__main__":
    main()

