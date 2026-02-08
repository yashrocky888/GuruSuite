#!/usr/bin/env python3
"""
D3 (Drekkana) Focused Verification Script
ONLY D3 - All other vargas BLOCKED until D3 is 100% verified.

JHora is FINAL AUTHORITY.
Prokerala must also match.
Even ONE planet mismatch = FAIL.
"""

import json
import sys
import os
from typing import Dict, Optional

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.dirname(__file__))

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

# PLANETS TO VERIFY
PLANETS = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# JHora Ground Truth (to be filled)
JHORA_D3_GROUND_TRUTH = {
    "Birth 1": {},
    "Birth 2": {},
    "Birth 3": {}  # Note: Birth 3 confirmed - Moon & Jupiter mismatch
}

# Prokerala Ground Truth (to be filled)
PROKERALA_D3_GROUND_TRUTH = {
    "Birth 1": {},
    "Birth 2": {},
    "Birth 3": {}  # Note: Birth 3 confirmed - matches JHora
}


def load_our_engine_d3_data() -> Dict:
    """Load our engine D3 data from comparison results."""
    try:
        with open("maitreya8_comparison_results.json", "r") as f:
            data = json.load(f)
        result = {}
        for birth_name in ["Birth 1", "Birth 2", "Birth 3"]:
            if birth_name in data and "D3" in data[birth_name]:
                result[birth_name] = data[birth_name]["D3"].get("our_engine", {})
        return result
    except FileNotFoundError:
        print("❌ maitreya8_comparison_results.json not found")
        return {}


def load_maitreya8_d3_data() -> Dict:
    """Load Maitreya8 D3 data from comparison results."""
    try:
        with open("maitreya8_comparison_results.json", "r") as f:
            data = json.load(f)
        result = {}
        for birth_name in ["Birth 1", "Birth 2", "Birth 3"]:
            if birth_name in data and "D3" in data[birth_name]:
                result[birth_name] = data[birth_name]["D3"].get("maitreya8", {})
        return result
    except FileNotFoundError:
        print("❌ maitreya8_comparison_results.json not found")
        return {}


def generate_d3_comparison_table(birth: Dict, jhora_data: Dict, prokerala_data: Dict,
                                 maitreya8_data: Dict, our_engine_data: Dict) -> str:
    """Generate D3 comparison table."""
    birth_name = birth["name"]
    
    table = f"\n{'='*120}\n"
    table += f"D3 (DREKKANA) VERIFICATION | BIRTH: {birth_name} ({birth['dob']} {birth['time']} IST)\n"
    table += f"{'='*120}\n"
    table += f"{'Planet':<12} | {'JHora':<12} | {'Prokerala':<12} | {'Maitreya8':<12} | {'Our Engine':<12} | {'Status'}\n"
    table += f"{'-'*120}\n"
    
    all_match = True
    match_count = 0
    mismatches = []
    
    for planet in PLANETS:
        jhora_sign = jhora_data.get(planet, "N/A")
        prokerala_sign = prokerala_data.get(planet, "N/A")
        maitreya8_sign = maitreya8_data.get(planet, "N/A")
        our_sign = our_engine_data.get(planet, "N/A")
        
        # Check if all match
        if (jhora_sign != "N/A" and prokerala_sign != "N/A" and
            maitreya8_sign != "N/A" and our_sign != "N/A"):
            if jhora_sign == prokerala_sign == maitreya8_sign == our_sign:
                status = "✅ PASS"
                match_count += 1
            else:
                status = "❌ FAIL"
                all_match = False
                mismatches.append({
                    "planet": planet,
                    "jhora": jhora_sign,
                    "prokerala": prokerala_sign,
                    "maitreya8": maitreya8_sign,
                    "our_engine": our_sign
                })
        elif jhora_sign != "N/A" and prokerala_sign != "N/A":
            # JHora and Prokerala available
            if jhora_sign == prokerala_sign:
                if jhora_sign == our_sign:
                    status = "✅ PASS (JHora+Prokerala)"
                    match_count += 1
                else:
                    status = "❌ FAIL (Our Engine mismatch)"
                    all_match = False
                    mismatches.append({
                        "planet": planet,
                        "jhora": jhora_sign,
                        "prokerala": prokerala_sign,
                        "our_engine": our_sign
                    })
            else:
                status = "⚠️  JHora≠Prokerala"
                all_match = False
        elif jhora_sign != "N/A":
            # Only JHora available
            if jhora_sign == our_sign:
                status = "✅ PASS (JHora)"
                match_count += 1
            else:
                status = "❌ FAIL (Our Engine mismatch)"
                all_match = False
                mismatches.append({
                    "planet": planet,
                    "jhora": jhora_sign,
                    "our_engine": our_sign
                })
        else:
            status = "⏳ PENDING"
        
        table += f"{planet:<12} | {jhora_sign:<12} | {prokerala_sign:<12} | {maitreya8_sign:<12} | {our_sign:<12} | {status}\n"
    
    table += f"{'-'*120}\n"
    table += f"Match Rate: {match_count}/10 planets\n"
    
    if jhora_data and any(v != "N/A" for v in jhora_data.values()):
        if all_match and match_count == 10:
            table += f"STATUS: ✅ VERIFIED (100% match with JHora and Prokerala)\n"
        else:
            table += f"STATUS: ❌ NOT VERIFIED (mismatches found)\n"
            if mismatches:
                table += f"\nMismatches:\n"
                for mm in mismatches:
                    table += f"  {mm['planet']}: JHora={mm['jhora']}, Our Engine={mm.get('our_engine', 'N/A')}\n"
    else:
        table += f"STATUS: ⏳ PENDING (JHora data not available)\n"
    
    table += f"{'='*120}\n"
    
    return table, all_match, match_count, mismatches


def analyze_d3_method(jhora_data: Dict, maitreya8_data: Dict, our_engine_data: Dict) -> str:
    """Analyze which D3 method JHora uses."""
    analysis = f"\n{'='*120}\n"
    analysis += f"D3 METHOD IDENTIFICATION\n"
    analysis += f"{'='*120}\n"
    
    if not jhora_data or all(v == "N/A" for v in jhora_data.values()):
        analysis += "⏳ JHora data not available yet.\n"
        return analysis
    
    jhora_match_maitreya8 = jhora_data == maitreya8_data
    jhora_match_our_engine = jhora_data == our_engine_data
    
    analysis += f"\nJHora vs Maitreya8: {'✅ MATCH' if jhora_match_maitreya8 else '❌ DIFFER'}\n"
    analysis += f"JHora vs Our Engine: {'✅ MATCH' if jhora_match_our_engine else '❌ DIFFER'}\n"
    
    if jhora_match_maitreya8:
        analysis += f"\n✅ CONCLUSION: JHora uses Maitreya8 D3 method\n"
        analysis += f"   → Adopt Maitreya8 D3 formula\n"
    elif jhora_match_our_engine:
        analysis += f"\n✅ CONCLUSION: JHora uses Our Engine D3 method\n"
        analysis += f"   → Keep Our Engine D3 formula\n"
    else:
        analysis += f"\n❌ CONCLUSION: JHora uses DIFFERENT D3 method\n"
        analysis += f"   → JHora D3 method must be reverse-engineered\n"
        analysis += f"   → Derive ONE UNIVERSAL RULE\n"
        analysis += f"   → NO planet-specific logic\n"
        analysis += f"   → NO birth-specific logic\n"
    
    analysis += f"{'='*120}\n"
    
    return analysis


def main():
    """Main D3 verification function."""
    print("="*120)
    print("D3 (DREKKANA) FOCUSED VERIFICATION")
    print("="*120)
    print("\n🔒 FOCUS: ONLY D3")
    print("🔒 BLOCKED: All other vargas until D3 is 100% verified")
    print("\nVerification Authority:")
    print("  1. JHora (PRIMARY and FINAL)")
    print("  2. Prokerala (SECONDARY - must also match)")
    print("\nRules:")
    print("  ✅ 100% match required (all 10 planets)")
    print("  ✅ All 3 births must pass")
    print("  ❌ Even ONE mismatch = FAIL")
    print("  ❌ NO planet-specific logic")
    print("  ❌ NO birth-specific logic")
    print("  ✅ ONE universal rule only")
    print("\n" + "="*120)
    
    # Load data
    our_engine_d3 = load_our_engine_d3_data()
    maitreya8_d3 = load_maitreya8_d3_data()
    
    print("\n📊 COMPARISON TABLES")
    print("="*120)
    
    all_births_verified = True
    total_mismatches = []
    
    for birth in VERIFIED_BIRTHS:
        birth_name = birth["name"]
        
        jhora_data = JHORA_D3_GROUND_TRUTH.get(birth_name, {})
        prokerala_data = PROKERALA_D3_GROUND_TRUTH.get(birth_name, {})
        maitreya8_data = maitreya8_d3.get(birth_name, {})
        our_engine_data = our_engine_d3.get(birth_name, {})
        
        table, all_match, match_count, mismatches = generate_d3_comparison_table(
            birth, jhora_data, prokerala_data, maitreya8_data, our_engine_data
        )
        print(table)
        
        if not all_match or match_count < 10:
            all_births_verified = False
            total_mismatches.extend(mismatches)
        
        # Method identification
        if jhora_data and any(v != "N/A" for v in jhora_data.values()):
            analysis = analyze_d3_method(jhora_data, maitreya8_data, our_engine_data)
            print(analysis)
    
    # Final Summary
    print("\n" + "="*120)
    print("D3 VERIFICATION SUMMARY")
    print("="*120)
    
    if all_births_verified and len(total_mismatches) == 0:
        print("✅ D3 = VERIFIED (100% match with JHora and Prokerala for all 3 births)")
        print("✅ Can proceed to next varga (D4)")
    else:
        print("❌ D3 = NOT VERIFIED")
        print(f"❌ Total mismatches: {len(total_mismatches)}")
        print("❌ All other vargas BLOCKED until D3 is resolved")
        print("\nRequired Actions:")
        print("  1. Get JHora D3 data for ALL THREE births")
        print("  2. Identify exact JHora D3 method")
        print("  3. Derive ONE UNIVERSAL RULE")
        print("  4. Fix D3 formula (no exceptions)")
        print("  5. Re-verify all 3 births")
    
    print("="*120 + "\n")
    
    # Save results
    results = {
        "status": "VERIFIED" if all_births_verified else "NOT VERIFIED",
        "mismatches": total_mismatches,
        "jhora_data": JHORA_D3_GROUND_TRUTH,
        "prokerala_data": PROKERALA_D3_GROUND_TRUTH
    }
    
    with open("d3_verification_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("✅ Results saved to: d3_verification_results.json\n")


if __name__ == "__main__":
    main()

