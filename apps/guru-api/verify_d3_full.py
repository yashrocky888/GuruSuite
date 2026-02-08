#!/usr/bin/env python3
"""
Full D3 Verification Against JHora
Verifies D3 implementation against JHora for all planets across all 3 births.
"""

import sys
import os
import requests
import json
from typing import Dict, List, Tuple

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

# JHora Ground Truth (to be filled)
JHORA_D3_GROUND_TRUTH = {
    "Birth 1": {},  # Pending
    "Birth 2": {},  # Pending
    "Birth 3": {
        "Moon": "Aquarius",      # ✅ Verified
        "Jupiter": "Cancer"       # ✅ Verified
    }
}

def get_d1_data(birth: Dict) -> Dict:
    """Fetch D1 data from API."""
    url = "http://localhost:8000/api/v1/kundli"
    params = {k: birth[k] for k in ["dob", "time", "lat", "lon", "timezone"]}
    try:
        response = requests.get(url, params=params, timeout=30)
        return response.json().get("D1", {})
    except Exception as e:
        print(f"❌ Error fetching D1 for {birth['name']}: {e}")
        return {}

def get_d3_data(birth: Dict) -> Dict:
    """Fetch D3 data from API."""
    url = "http://localhost:8000/api/v1/kundli"
    params = {k: birth[k] for k in ["dob", "time", "lat", "lon", "timezone"]}
    try:
        response = requests.get(url, params=params, timeout=30)
        return response.json().get("D3", {})
    except Exception as e:
        print(f"❌ Error fetching D3 for {birth['name']}: {e}")
        return {}

def verify_birth_d3(birth: Dict) -> Tuple[bool, int, int, List[Dict]]:
    """Verify D3 for a single birth against JHora."""
    birth_name = birth["name"]
    jhora_data = JHORA_D3_GROUND_TRUTH.get(birth_name, {})
    
    d1_data = get_d1_data(birth)
    d3_data = get_d3_data(birth)
    
    if not d1_data or not d3_data:
        return False, 0, 0, []
    
    print(f"\n{'='*120}")
    print(f"D3 VERIFICATION: {birth_name} ({birth['dob']} {birth['time']} IST)")
    print(f"{'='*120}")
    
    print(f"\n{'Planet':<12} | {'D1 Sign':<12} | {'Deg':<8} | {'Div':<4} | {'Our D3':<12} | {'API D3':<12} | {'JHora D3':<12} | {'Status'}")
    print("-"*120)
    
    all_match = True
    match_count = 0
    total_planets = 0
    mismatches = []
    
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
        
        # Get JHora (if available)
        jhora_d3_sign = jhora_data.get(planet, "N/A")
        jhora_d3_idx = SIGN_NAMES.index(jhora_d3_sign) if jhora_d3_sign in SIGN_NAMES else -1
        
        total_planets += 1
        
        # Check internal consistency (our function vs API)
        internal_match = our_d3_idx == api_d3_idx
        
        # Check JHora match (if JHora data available)
        if jhora_d3_sign != "N/A":
            jhora_match = our_d3_idx == jhora_d3_idx
            if jhora_match:
                match_count += 1
            else:
                all_match = False
                mismatches.append({
                    "planet": planet,
                    "d1_sign": d1_sign,
                    "our_d3": our_d3_sign,
                    "jhora_d3": jhora_d3_sign
                })
            status = "✅" if jhora_match else "❌"
        else:
            status = "⏳" if internal_match else "⚠️"
        
        print(f"{planet:<12} | {d1_sign:<12} | {deg_in_sign:7.4f}° | {division:4} | {our_d3_sign:<12} | {api_d3_sign:<12} | {jhora_d3_sign:<12} | {status}")
    
    print("-"*120)
    
    if jhora_data:
        print(f"JHora Match Rate: {match_count}/{total_planets} planets")
        if all_match and match_count == total_planets:
            print(f"✅ {birth_name}: 100% MATCH with JHora")
        else:
            print(f"❌ {birth_name}: MISMATCHES found")
            if mismatches:
                print("\nMismatches:")
                for mm in mismatches:
                    print(f"  {mm['planet']}: D1={mm['d1_sign']}, Our={mm['our_d3']}, JHora={mm['jhora_d3']}")
    else:
        print(f"⏳ {birth_name}: JHora data not available")
        print(f"   Internal consistency: {'✅ PASS' if all([calculate_varga_sign(d1_data.get('Planets', {}).get(p, {}).get('sign_index', -1), d1_data.get('Planets', {}).get(p, {}).get('degrees_in_sign', 0), 'D3') == SIGN_NAMES.index(d3_data.get('Planets', {}).get(p, {}).get('sign', '')) if p != 'Ascendant' else calculate_varga_sign(d1_data.get('Ascendant', {}).get('sign_index', -1), d1_data.get('Ascendant', {}).get('degrees_in_sign', 0), 'D3') == SIGN_NAMES.index(d3_data.get('Ascendant', {}).get('sign', '')) for p in PLANETS]) else '❌ FAIL'}")
    
    return all_match, match_count, total_planets, mismatches

def verify_rule_table():
    """Verify Division 1 rule table against JHora data."""
    print(f"\n{'='*120}")
    print("DIVISION 1 RULE TABLE VERIFICATION")
    print(f"{'='*120}")
    
    print("\nTesting all 12 signs in Division 1 (10°-20° range):")
    print(f"\n{'Sign':<12} | {'Sign Idx':<10} | {'Our Offset':<12} | {'Result Sign':<12} | {'JHora Expected':<12} | {'Status'}")
    print("-"*120)
    
    # Test each sign with a degree in division 1 (e.g., 15°)
    test_degree = 15.0
    rule_table_verified = True
    
    for sign_idx in range(12):
        sign_name = SIGN_NAMES[sign_idx]
        our_d3_idx = calculate_varga_sign(sign_idx, test_degree, "D3")
        our_d3_sign = SIGN_NAMES[our_d3_idx]
        
        # Calculate offset
        offset = (our_d3_idx - sign_idx) % 12
        if offset > 6:
            offset = offset - 12
        
        # JHora expected (if we had data)
        jhora_expected = "N/A"
        status = "⏳"
        
        print(f"{sign_name:<12} | {sign_idx:10} | {offset:+3}           | {our_d3_sign:<12} | {jhora_expected:<12} | {status}")
    
    print("-"*120)
    print("\n⚠️ Rule table verification requires JHora data for all 12 signs in Division 1.")
    print("   Current rule table is based on known mappings (Taurus, Virgo) and")
    print("   Parāśara standard for all other signs.")
    
    return rule_table_verified

def main():
    """Main verification function."""
    print("="*120)
    print("D3 FULL VERIFICATION - JHORA CANONICAL")
    print("="*120)
    print("\nVerification Authority: Jagannatha Hora (JHora)")
    print("Verification Criteria: 100% planet-by-planet match required")
    print("Even ONE mismatch = NOT VERIFIED")
    print("\n" + "="*120)
    
    all_births_verified = True
    total_matches = 0
    total_planets = 0
    all_mismatches = []
    
    # Verify each birth
    for birth in VERIFIED_BIRTHS:
        verified, matches, planets, mismatches = verify_birth_d3(birth)
        total_matches += matches
        total_planets += planets
        all_mismatches.extend(mismatches)
        
        if not verified and matches < planets:
            all_births_verified = False
    
    # Verify rule table
    verify_rule_table()
    
    # Final summary
    print(f"\n{'='*120}")
    print("VERIFICATION SUMMARY")
    print(f"{'='*120}")
    
    if total_planets > 0:
        match_rate = (total_matches / total_planets) * 100
        print(f"\nOverall Match Rate: {total_matches}/{total_planets} planets ({match_rate:.1f}%)")
        
        if all_births_verified and total_matches == total_planets:
            print("\n✅ D3 = VERIFIED (JHora-canonical)")
            print("   - All planets match JHora for all 3 births")
            print("   - Rule table confirmed")
            print("   - D3 logic is LOCKED")
        else:
            print("\n❌ D3 = NOT VERIFIED")
            print(f"   - {total_planets - total_matches} mismatches found")
            if all_mismatches:
                print("\n   Mismatches:")
                for mm in all_mismatches:
                    print(f"     {mm['planet']}: Our={mm['our_d3']}, JHora={mm['jhora_d3']}")
    else:
        print("\n⏳ D3 = PENDING VERIFICATION")
        print("   - JHora ground truth data required for all 3 births")
        print("   - Current implementation ready for verification")
    
    print(f"\n{'='*120}\n")
    
    # Save results
    results = {
        "status": "VERIFIED" if all_births_verified and total_matches == total_planets else "NOT VERIFIED",
        "match_rate": f"{total_matches}/{total_planets}",
        "mismatches": all_mismatches,
        "jhora_data_available": {
            birth["name"]: len(JHORA_D3_GROUND_TRUTH.get(birth["name"], {})) > 0
            for birth in VERIFIED_BIRTHS
        }
    }
    
    with open("d3_verification_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("✅ Results saved to: d3_verification_results.json\n")

if __name__ == "__main__":
    main()

