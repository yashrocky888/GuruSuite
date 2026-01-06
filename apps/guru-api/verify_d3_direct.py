#!/usr/bin/env python3
"""
Direct D3 Verification - Calculates D3 from D1 data and compares with JHora
Uses direct calculation instead of API calls.
"""

import sys
import os
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

# JHora D3 Ground Truth from D3_VERIFICATION_INSTRUCTIONS.md
# IMPORTANT:
#   - Only confirmed JHora values (not placeholders) should be included
#   - Any missing / placeholder values MUST be treated as PENDING, not mismatches
JHORA_D3_GROUND_TRUTH = {
    "Birth 1": {
        # All values confirmed from JHora
        "Ascendant": "Scorpio",
        "Sun": "Taurus",
        "Moon": "Cancer",
        "Mars": "Leo",
        "Mercury": "Capricorn",
        "Jupiter": "Pisces",
        "Venus": "Aries",
        "Saturn": "Libra",
        "Rahu": "Aquarius",
        "Ketu": "Leo",
    },
    "Birth 2": {
        # Authoritative JHora D3 (Traditional) signs for Birth 2
        "Ascendant": "Aquarius",
        "Sun": "Scorpio",
        "Moon": "Scorpio",
        "Mars": "Cancer",
        "Mercury": "Aries",
        "Jupiter": "Leo",
        "Venus": "Taurus",
        "Saturn": "Pisces",
        "Rahu": "Taurus",
        "Ketu": "Scorpio",
    },
    "Birth 3": {
        # Authoritative JHora D3 (Traditional) signs for Birth 3
        "Ascendant": "Gemini",
        "Sun": "Scorpio",
        "Moon": "Capricorn",
        "Mars": "Cancer",
        "Mercury": "Pisces",
        "Jupiter": "Virgo",
        "Venus": "Cancer",
        "Saturn": "Taurus",
        "Rahu": "Libra",
        "Ketu": "Aries",
    }
}

# D1 Data - Using known values from previous calculations
# These are the D1 signs and degrees needed to calculate D3
D1_DATA = {
    "Birth 1": {
        "Ascendant": {"sign_index": 7, "degrees_in_sign": 2.2799, "sign": "Scorpio"},
        "Sun": {"sign_index": 1, "degrees_in_sign": 1.4138, "sign": "Taurus"},
        "Moon": {"sign_index": 7, "degrees_in_sign": 25.2501, "sign": "Scorpio"},
        "Mars": {"sign_index": 4, "degrees_in_sign": 2.2504, "sign": "Leo"},
        "Mercury": {"sign_index": 1, "degrees_in_sign": 22.1178, "sign": "Taurus"},
        "Jupiter": {"sign_index": 7, "degrees_in_sign": 18.6872, "sign": "Scorpio"},
        "Venus": {"sign_index": 0, "degrees_in_sign": 5.6886, "sign": "Aries"},
        "Saturn": {"sign_index": 10, "degrees_in_sign": 28.8956, "sign": "Aquarius"},
        "Rahu": {"sign_index": 6, "degrees_in_sign": 10.7944, "sign": "Libra"},
        "Ketu": {"sign_index": 0, "degrees_in_sign": 10.7944, "sign": "Aries"},
    },
    "Birth 2": {
        "Ascendant": {"sign_index": 2, "degrees_in_sign": 21.0828, "sign": "Gemini"},
        "Sun": {"sign_index": 11, "degrees_in_sign": 23.9174, "sign": "Pisces"},
        "Moon": {"sign_index": 7, "degrees_in_sign": 5.1063, "sign": "Scorpio"},
        "Mars": {"sign_index": 11, "degrees_in_sign": 16.7663, "sign": "Pisces"},
        "Mercury": {"sign_index": 0, "degrees_in_sign": 4.4681, "sign": "Aries"},
        "Jupiter": {"sign_index": 8, "degrees_in_sign": 22.6990, "sign": "Sagittarius"},
        "Venus": {"sign_index": 1, "degrees_in_sign": 9.6279, "sign": "Taurus"},
        "Saturn": {"sign_index": 11, "degrees_in_sign": 6.1822, "sign": "Pisces"},
        "Rahu": {"sign_index": 5, "degrees_in_sign": 23.4807, "sign": "Virgo"},
        "Ketu": {"sign_index": 11, "degrees_in_sign": 23.4807, "sign": "Pisces"},
    },
    "Birth 3": {
        "Ascendant": {"sign_index": 2, "degrees_in_sign": 7.3987, "sign": "Gemini"},
        "Sun": {"sign_index": 11, "degrees_in_sign": 23.5934, "sign": "Pisces"},
        "Moon": {"sign_index": 5, "degrees_in_sign": 11.3237, "sign": "Virgo"},
        "Mars": {"sign_index": 7, "degrees_in_sign": 28.9574, "sign": "Scorpio"},
        "Mercury": {"sign_index": 11, "degrees_in_sign": 7.7565, "sign": "Pisces"},
        "Jupiter": {"sign_index": 1, "degrees_in_sign": 14.8664, "sign": "Taurus"},
        "Venus": {"sign_index": 11, "degrees_in_sign": 10.9480, "sign": "Pisces"},
        "Saturn": {"sign_index": 1, "degrees_in_sign": 4.5711, "sign": "Taurus"},
        "Rahu": {"sign_index": 2, "degrees_in_sign": 16.7195, "sign": "Gemini"},
        "Ketu": {"sign_index": 8, "degrees_in_sign": 16.7195, "sign": "Sagittarius"},
    }
}

def verify_birth_d3(birth: Dict) -> Tuple[bool, int, int, List[Dict]]:
    """Verify D3 for a single birth against JHora."""
    birth_name = birth["name"]
    jhora_data = JHORA_D3_GROUND_TRUTH.get(birth_name, {})
    d1_data = D1_DATA.get(birth_name, {})
    
    if not d1_data:
        print(f"❌ No D1 data for {birth_name}")
        return False, 0, 0, []
    
    print(f"\n{'='*120}")
    print(f"D3 VERIFICATION: {birth_name} ({birth['dob']} {birth['time']} IST)")
    print(f"{'='*120}")
    
    print(f"\n{'Planet':<12} | {'D1 Sign':<12} | {'Deg':<8} | {'Div':<4} | {'Our D3':<12} | {'JHora D3':<12} | {'Status'}")
    print("-"*120)
    
    all_match = True
    match_count = 0
    total_planets = 0
    available_count = 0  # Count only planets with confirmed JHora data
    mismatches = []
    
    for planet in PLANETS:
        d1_pdata = d1_data.get(planet, {})
        if not d1_pdata:
            continue
        
        sign_idx = d1_pdata.get("sign_index", -1)
        deg_in_sign = d1_pdata.get("degrees_in_sign", 0)
        d1_sign = d1_pdata.get("sign", "N/A")
        division = int(deg_in_sign / 10.0)
        
        # Calculate using our function
        our_d3_idx = calculate_varga_sign(sign_idx, deg_in_sign, "D3")
        our_d3_sign = SIGN_NAMES[our_d3_idx]
        
        # Get JHora (if available)
        # IMPORTANT: None or missing = PENDING (not mismatch)
        jhora_d3_sign = jhora_data.get(planet)
        jhora_available = False
        jhora_d3_idx = -1
        
        if jhora_d3_sign is not None and jhora_d3_sign in SIGN_NAMES:
            jhora_d3_idx = SIGN_NAMES.index(jhora_d3_sign)
            jhora_available = True
            jhora_d3_sign_display = jhora_d3_sign
            available_count += 1  # Count confirmed JHora data
        else:
            jhora_d3_sign_display = "N/A (Pending)"
            jhora_available = False
        
        total_planets += 1
        
        # Check JHora match (ONLY if confirmed JHora data available)
        if jhora_available:
            jhora_match = our_d3_idx == jhora_d3_idx
            if jhora_match:
                match_count += 1
            else:
                all_match = False
                mismatches.append({
                    "planet": planet,
                    "birth": birth_name,
                    "d1_sign": d1_sign,
                    "d1_idx": sign_idx,
                    "deg": deg_in_sign,
                    "division": division,
                    "our_d3": our_d3_sign,
                    "our_d3_idx": our_d3_idx,
                    "jhora_d3": jhora_d3_sign,
                    "jhora_d3_idx": jhora_d3_idx
                })
            status = "✅" if jhora_match else "❌"
        else:
            # Missing/placeholder data = PENDING (not mismatch)
            status = "⏳"
        
        print(f"{planet:<12} | {d1_sign:<12} | {deg_in_sign:7.4f}° | {division:4} | {our_d3_sign:<12} | {jhora_d3_sign_display:<12} | {status}")
    
    print("-"*120)
    
    # available_count already calculated above
    pending_count = total_planets - available_count
    
    if available_count > 0:
        print(f"JHora Match Rate: {match_count}/{available_count} planets (confirmed data)")
        if pending_count > 0:
            print(f"Pending: {pending_count} planets (JHora data not provided)")
        
        if all_match and match_count == available_count:
            if pending_count == 0:
                print(f"✅ {birth_name}: 100% VERIFIED ({match_count}/{available_count})")
            else:
                print(f"✅ {birth_name}: 100% MATCH for available data ({match_count}/{available_count}), {pending_count} pending")
        else:
            print(f"❌ {birth_name}: MISMATCHES found ({match_count}/{available_count} confirmed)")
    else:
        print(f"⏳ {birth_name}: JHora data not available ({pending_count} planets pending)")
    
    return all_match, match_count, available_count, mismatches

def main():
    """Main verification function."""
    print("="*120)
    print("D3 COMPLETE VERIFICATION - JHORA CANONICAL (DIRECT CALCULATION)")
    print("="*120)
    print("\nVerification Scope:")
    print("  - All 10 planets (Ascendant + 9 planets)")
    print("  - All 3 birth charts")
    print("  - Total: 30 planet-by-planet comparisons")
    print("\nVerification Authority: Jagannatha Hora (JHora)")
    print("Verification Criteria: 100% match required")
    print("Even ONE mismatch = NOT VERIFIED")
    print("\n" + "="*120)
    
    all_births_verified = True
    total_matches = 0
    total_available = 0
    total_pending = 0
    all_mismatches = []
    
    # Verify each birth
    for birth in VERIFIED_BIRTHS:
        verified, matches, available, mismatches = verify_birth_d3(birth)
        total_matches += matches
        total_available += available
        total_pending += (10 - available)  # 10 planets per birth
        all_mismatches.extend(mismatches)
        
        if not verified and matches < available:
            all_births_verified = False
    
    # Document mismatches
    if all_mismatches:
        print(f"\n{'='*120}")
        print("MISMATCH DOCUMENTATION")
        print(f"{'='*120}")
        
        print(f"\nTotal Mismatches: {len(all_mismatches)}")
        print(f"\n{'Birth':<12} | {'Planet':<12} | {'D1 Sign':<12} | {'Div':<4} | {'Our D3':<12} | {'JHora D3':<12} | {'Offset'}")
        print("-"*120)
        
        for mm in all_mismatches:
            offset = (mm['jhora_d3_idx'] - mm['our_d3_idx']) % 12
            if offset > 6:
                offset = offset - 12
            print(f"{mm['birth']:<12} | {mm['planet']:<12} | {mm['d1_sign']:<12} | {mm['division']:4} | {mm['our_d3']:<12} | {mm['jhora_d3']:<12} | {offset:+3}")
    
    # Final summary
    print(f"\n{'='*120}")
    print("VERIFICATION SUMMARY")
    print(f"{'='*120}")
    
    if total_available > 0:
        match_rate = (total_matches / total_available) * 100
        pending_total = 30 - total_available
        
        print(f"\nOverall Match Rate: {total_matches}/{total_available} planets ({match_rate:.1f}%)")
        if pending_total > 0:
            print(f"Pending: {pending_total} planets (JHora data not provided - NOT mismatches)")
        
        if all_births_verified and total_matches == total_available and total_available == 30:
            print("\n" + "="*120)
            print("✅ D3 = VERIFIED (JHora-canonical)")
            print("="*120)
            print("\nVerification Complete:")
            print("  ✅ All 30 planets match JHora (100%)")
            print("  ✅ All 3 births verified")
            print("  ✅ Rule table confirmed")
            print("\n🔒 D3 Logic Status: FROZEN")
            print("  - No further changes allowed")
            print("  - Implementation is canonical")
            print("  - Ready for production")
        elif total_available < 30:
            if total_matches == total_available:
                print(f"\n⏳ D3 = PARTIALLY VERIFIED ({total_available}/30 planets)")
                print(f"   - {pending_total} planets pending JHora data (NOT mismatches)")
                print("   - All available confirmed data matches (100%)")
                print("   - Current implementation ready for full verification")
                print("   - Awaiting JHora data for Birth 2 (10 planets) and Birth 3 (2 planets)")
            else:
                print(f"\n❌ D3 = NOT VERIFIED")
                print(f"   - {total_available - total_matches} mismatches in confirmed data")
                print(f"   - {pending_total} planets pending JHora data (NOT mismatches)")
                print("   - Rule table may need adjustment")
        else:
            print("\n❌ D3 = NOT VERIFIED")
            print(f"   - {total_available - total_matches} mismatches found")
            print("   - Rule table may need adjustment")
    else:
        print("\n⏳ D3 = PENDING VERIFICATION")
        print("   - JHora ground truth data required")
        print("   - Current implementation ready for verification")
    
    print(f"\n{'='*120}\n")
    
    # Save results
    results = {
        "status": "VERIFIED" if all_births_verified and total_matches == total_available == 30 else "NOT VERIFIED",
        "match_rate": f"{total_matches}/{total_available}",
        "total_expected": 30,
        "total_available": total_available,
        "mismatches": all_mismatches,
    }
    
    with open("d3_complete_verification_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("✅ Results saved to: d3_complete_verification_results.json\n")

if __name__ == "__main__":
    main()

