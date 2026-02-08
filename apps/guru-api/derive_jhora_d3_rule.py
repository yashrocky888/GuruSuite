#!/usr/bin/env python3
"""
Derive JHora D3 Rule from All Three Births
Systematically analyzes D1→D3 mapping to identify JHora's exact method.
"""

import sys
import os
import json
import math
import requests
from typing import Dict, List, Tuple, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.dirname(__file__))

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

VERIFIED_BIRTHS = [
    {"name": "Birth 1", "dob": "1995-05-16", "time": "18:38", "lat": 12.9716, "lon": 77.5946, "timezone": "Asia/Kolkata"},
    {"name": "Birth 2", "dob": "1996-04-07", "time": "11:59", "lat": 12.9716, "lon": 77.5946, "timezone": "Asia/Kolkata"},
    {"name": "Birth 3", "dob": "2001-04-07", "time": "11:00", "lat": 12.9716, "lon": 77.5946, "timezone": "Asia/Kolkata"}
]

# Known JHora D3 outputs (from user - Birth 3 confirmed)
JHORA_D3_GROUND_TRUTH = {
    "Birth 3": {
        "Moon": "Aquarius",      # Our: Capricorn (offset +1)
        "Jupiter": "Cancer"       # Our: Virgo (offset -2)
    }
}

# Load our engine and Maitreya8 outputs
def load_comparison_data():
    """Load existing D3 comparison data."""
    try:
        with open("maitreya8_comparison_results.json", "r") as f:
            return json.load(f)
    except:
        return {}


def get_d1_data(birth: Dict) -> Dict:
    """Fetch D1 data from API."""
    url = "http://localhost:8000/api/v1/kundli"
    params = {k: birth[k] for k in ["dob", "time", "lat", "lon", "timezone"]}
    try:
        response = requests.get(url, params=params, timeout=30)
        return response.json().get("D1", {})
    except:
        return {}


def our_engine_d3(sign_idx: int, deg_in_sign: float) -> int:
    """Our current D3 (Parāśara standard)."""
    l = int(math.floor(deg_in_sign / 10.0))
    if l >= 3: l = 2
    return (sign_idx + l * 4) % 12


def analyze_all_births():
    """Analyze all three births to derive JHora D3 rule."""
    print("="*120)
    print("DERIVING JHORA D3 RULE - SYSTEMATIC ANALYSIS")
    print("="*120)
    
    comparison_data = load_comparison_data()
    
    # Collect all D1→D3 mappings
    all_mappings = []
    
    for birth in VERIFIED_BIRTHS:
        birth_name = birth["name"]
        print(f"\n{'='*120}")
        print(f"ANALYZING: {birth_name} ({birth['dob']} {birth['time']} IST)")
        print(f"{'='*120}")
        
        d1_data = get_d1_data(birth)
        if not d1_data:
            continue
        
        our_d3_data = comparison_data.get(birth_name, {}).get("D3", {}).get("our_engine", {})
        maitreya8_d3_data = comparison_data.get(birth_name, {}).get("D3", {}).get("maitreya8", {})
        jhora_d3_data = JHORA_D3_GROUND_TRUTH.get(birth_name, {})
        
        print(f"\n{'Planet':<12} | {'D1 Sign':<12} | {'D1 Idx':<8} | {'Deg':<8} | {'Div':<4} | {'Our D3':<12} | {'Maitreya8':<12} | {'JHora D3':<12}")
        print("-"*120)
        
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
            
            our_d3_sign = our_d3_data.get(planet, "N/A")
            maitreya8_d3_sign = maitreya8_d3_data.get(planet, "N/A")
            jhora_d3_sign = jhora_d3_data.get(planet, "N/A")
            
            print(f"{planet:<12} | {d1_sign:<12} | {sign_idx:8} | {deg_in_sign:7.4f}° | {division:4} | {our_d3_sign:<12} | {maitreya8_d3_sign:<12} | {jhora_d3_sign:<12}")
            
            if jhora_d3_sign != "N/A":
                our_d3_idx = SIGN_NAMES.index(our_d3_sign) if our_d3_sign != "N/A" else -1
                jhora_d3_idx = SIGN_NAMES.index(jhora_d3_sign)
                
                all_mappings.append({
                    "birth": birth_name,
                    "planet": planet,
                    "d1_sign_idx": sign_idx,
                    "deg_in_sign": deg_in_sign,
                    "division": division,
                    "our_d3_idx": our_d3_idx,
                    "jhora_d3_idx": jhora_d3_idx,
                    "offset": (jhora_d3_idx - our_d3_idx) % 12
                })
    
    # Analyze pattern
    print("\n" + "="*120)
    print("PATTERN ANALYSIS - JHORA D3 RULE DERIVATION")
    print("="*120)
    
    if all_mappings:
        print("\nKnown JHora Mappings:")
        for m in all_mappings:
            print(f"\n{m['planet']} ({m['birth']}):")
            print(f"  D1: {SIGN_NAMES[m['d1_sign_idx']]} (idx {m['d1_sign_idx']}), {m['deg_in_sign']:.4f}°, Div {m['division']}")
            print(f"  Our D3: {SIGN_NAMES[m['our_d3_idx']]} (idx {m['our_d3_idx']})")
            print(f"  JHora D3: {SIGN_NAMES[m['jhora_d3_idx']]} (idx {m['jhora_d3_idx']})")
            print(f"  Offset: {m['offset']:+d}")
        
        print("\n" + "="*120)
        print("RULE HYPOTHESIS")
        print("="*120)
        print("\nAnalyzing offsets to derive universal rule...")
        print("(Need more JHora data points to confirm pattern)")
    
    return all_mappings


if __name__ == "__main__":
    analyze_all_births()

