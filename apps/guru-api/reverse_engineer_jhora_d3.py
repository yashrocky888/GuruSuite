#!/usr/bin/env python3
"""
Reverse-Engineer JHora D3 Rule
Derives the exact D3 method JHora uses from observed mismatches.

NO DATA REQUESTS - Work with existing information.
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

# Known JHora D3 outputs (from user confirmation)
# Birth 3: Moon = Aquarius, Jupiter = Cancer (our engine: Moon = Capricorn, Jupiter = Virgo)
JHORA_D3_KNOWN = {
    "Birth 3": {
        "Moon": "Aquarius",      # Our engine: Capricorn
        "Jupiter": "Cancer"      # Our engine: Virgo
    }
}

# Our engine D3 (Parāśara standard)
def our_engine_d3(sign_index: int, degrees_in_sign: float) -> int:
    """Our current D3 implementation (Parāśara standard)."""
    l = int(math.floor(degrees_in_sign / 10.0))
    if l >= 3:
        l = 2
    return (sign_index + l * 4) % 12


def get_d1_data(birth: Dict) -> Dict:
    """Fetch D1 data from API."""
    url = "http://localhost:8000/api/v1/kundli"
    params = {
        "dob": birth["dob"],
        "time": birth["time"],
        "lat": birth["lat"],
        "lon": birth["lon"],
        "timezone": birth["timezone"]
    }
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("D1", {})
    except Exception as e:
        print(f"❌ Error fetching D1 for {birth['name']}: {e}")
        return {}


def analyze_d3_mismatches():
    """Analyze D3 mismatches to derive JHora rule."""
    print("="*120)
    print("REVERSE-ENGINEERING JHORA D3 RULE")
    print("="*120)
    print("\nKnown Facts:")
    print("  - Birth 3: Moon & Jupiter mismatch")
    print("  - JHora Moon = Aquarius (our engine: Capricorn)")
    print("  - JHora Jupiter = Cancer (our engine: Virgo)")
    print("  - JHora = Prokerala (confirmed)")
    print("\n" + "="*120)
    
    # Get D1 data for Birth 3
    birth3 = VERIFIED_BIRTHS[2]
    d1_data = get_d1_data(birth3)
    
    if not d1_data:
        print("❌ Failed to fetch D1 data")
        return
    
    print("\n📊 D1 Data for Birth 3 (2001-04-07 11:00 IST):")
    print("-"*120)
    print(f"{'Planet':<12} | {'D1 Sign':<12} | {'Sign Idx':<10} | {'Deg in Sign':<12} | {'Our D3':<12} | {'JHora D3':<12} | {'Offset'}")
    print("-"*120)
    
    mismatches = []
    
    for planet in ["Moon", "Jupiter"]:
        pdata = d1_data.get("Planets", {}).get(planet, {})
        if not pdata:
            continue
        
        sign_idx = pdata.get("sign_index", -1)
        deg_in_sign = pdata.get("degrees_in_sign", 0)
        d1_sign = pdata.get("sign", "N/A")
        
        # Our engine D3
        our_d3_idx = our_engine_d3(sign_idx, deg_in_sign)
        our_d3_sign = SIGN_NAMES[our_d3_idx]
        
        # JHora D3 (known)
        jhora_d3_sign = JHORA_D3_KNOWN["Birth 3"].get(planet, "N/A")
        jhora_d3_idx = SIGN_NAMES.index(jhora_d3_sign) if jhora_d3_sign != "N/A" else -1
        
        # Calculate offset difference
        if jhora_d3_idx >= 0 and our_d3_idx >= 0:
            offset = (jhora_d3_idx - our_d3_idx) % 12
            if offset > 6:
                offset = offset - 12  # Show negative offset
            
            print(f"{planet:<12} | {d1_sign:<12} | {sign_idx:10} | {deg_in_sign:11.4f}° | {our_d3_sign:<12} | {jhora_d3_sign:<12} | {offset:+3}")
            
            if offset != 0:
                mismatches.append({
                    "planet": planet,
                    "d1_sign_idx": sign_idx,
                    "deg_in_sign": deg_in_sign,
                    "division": int(deg_in_sign / 10),
                    "our_d3_idx": our_d3_idx,
                    "jhora_d3_idx": jhora_d3_idx,
                    "offset": offset
                })
    
    print("-"*120)
    
    # Analyze pattern
    print("\n" + "="*120)
    print("PATTERN ANALYSIS")
    print("="*120)
    
    if mismatches:
        print("\nMismatch Details:")
        for mm in mismatches:
            print(f"\n{mm['planet']}:")
            print(f"  D1 Sign: {SIGN_NAMES[mm['d1_sign_idx']]} (idx {mm['d1_sign_idx']})")
            print(f"  Degrees in Sign: {mm['deg_in_sign']:.4f}°")
            print(f"  Division: {mm['division']} (0-10°={0}, 10-20°={1}, 20-30°={2})")
            print(f"  Our Engine D3: {SIGN_NAMES[mm['our_d3_idx']]} (idx {mm['our_d3_idx']})")
            print(f"  JHora D3: {SIGN_NAMES[mm['jhora_d3_idx']]} (idx {mm['jhora_d3_idx']})")
            print(f"  Offset: {mm['offset']:+d} signs")
        
        print("\n" + "="*120)
        print("RULE DERIVATION")
        print("="*120)
        print("\nAnalyzing to derive JHora's D3 rule...")
        print("(This requires examining the pattern across all three births)")
    
    return mismatches


def main():
    """Main analysis function."""
    mismatches = analyze_d3_mismatches()
    
    print("\n" + "="*120)
    print("NEXT STEPS")
    print("="*120)
    print("\n1. Analyze D1 data for all three births")
    print("2. Compare our engine D3 vs JHora D3 for ALL planets")
    print("3. Identify the universal rule JHora uses")
    print("4. Implement the rule in varga_drik.py")
    print("5. Verify all 3 births (100% match required)")
    print("="*120 + "\n")


if __name__ == "__main__":
    main()

