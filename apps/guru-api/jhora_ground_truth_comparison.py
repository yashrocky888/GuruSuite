#!/usr/bin/env python3
"""
JHora Ground Truth Comparison Framework
Compares Maitreya8, Our Engine, Prokerala against JHora for D4, D7, D30.

NO CODE CHANGES - Only data collection and reporting.
"""

import json
from typing import Dict, Optional, List

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

# FOCUS VARGAS
FOCUS_VARGAS = [4, 7, 30]

# PLANETS TO EXTRACT
PLANETS = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# Load existing Maitreya8 and Our Engine data
def load_comparison_data() -> Dict:
    """Load existing comparison data from JSON."""
    try:
        with open("maitreya8_comparison_results.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ maitreya8_comparison_results.json not found. Run execute_maitreya8_comparison.py first.")
        return {}


# JHora ground truth data structure (to be filled)
JHORA_GROUND_TRUTH = {
    "D4": {
        "Birth 1": {},
        "Birth 2": {},
        "Birth 3": {}
    },
    "D7": {
        "Birth 1": {},
        "Birth 2": {},
        "Birth 3": {}
    },
    "D30": {
        "Birth 1": {},
        "Birth 2": {},
        "Birth 3": {}
    }
}

# Prokerala ground truth data structure (to be filled)
PROKERALA_GROUND_TRUTH = {
    "D4": {
        "Birth 1": {},
        "Birth 2": {},
        "Birth 3": {}
    },
    "D7": {
        "Birth 1": {},
        "Birth 2": {},
        "Birth 3": {}
    },
    "D30": {
        "Birth 1": {},
        "Birth 2": {},
        "Birth 3": {}
    }
}


def generate_comparison_table(varga_type: int, birth: Dict,
                              jhora_data: Dict, prokerala_data: Dict,
                              maitreya8_data: Dict, our_engine_data: Dict) -> str:
    """Generate comparison table for a varga."""
    varga_name = f"D{varga_type}"
    birth_name = birth["name"]
    
    table = f"\n{'='*120}\n"
    table += f"VARGA: {varga_name} | BIRTH: {birth_name} ({birth['dob']} {birth['time']} IST)\n"
    table += f"{'='*120}\n"
    table += f"{'Planet':<12} | {'JHora':<12} | {'Prokerala':<12} | {'Maitreya8':<12} | {'Our Engine':<12} | {'Status'}\n"
    table += f"{'-'*120}\n"
    
    all_match = True
    match_count = 0
    
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
        elif jhora_sign != "N/A":
            # Only JHora data available
            if jhora_sign == maitreya8_sign == our_sign:
                status = "✅ PASS (JHora)"
                match_count += 1
            else:
                status = "❌ FAIL"
                all_match = False
        else:
            status = "⏳ PENDING"
        
        table += f"{planet:<12} | {jhora_sign:<12} | {prokerala_sign:<12} | {maitreya8_sign:<12} | {our_sign:<12} | {status}\n"
    
    table += f"{'-'*120}\n"
    table += f"Match Rate: {match_count}/10 planets\n"
    
    if jhora_data and any(v != "N/A" for v in jhora_data.values()):
        if all_match and match_count == 10:
            table += f"STATUS: ✅ VERIFIED (100% match with JHora, Prokerala, Maitreya8, Our Engine)\n"
        elif jhora_data == maitreya8_data:
            table += f"STATUS: ⚠️  JHora == Maitreya8 (but Prokerala/Our Engine differ)\n"
        elif jhora_data == our_engine_data:
            table += f"STATUS: ⚠️  JHora == Our Engine (but Maitreya8/Prokerala differ)\n"
        else:
            table += f"STATUS: ❌ NOT VERIFIED (mismatches found)\n"
    else:
        table += f"STATUS: ⏳ PENDING (JHora data not available)\n"
    
    table += f"{'='*120}\n"
    
    return table, all_match, match_count


def analyze_method_alignment(varga_type: int, birth_name: str,
                             jhora_data: Dict, maitreya8_data: Dict, our_engine_data: Dict) -> str:
    """Analyze which method JHora uses."""
    varga_name = f"D{varga_type}"
    
    analysis = f"\n{'='*120}\n"
    analysis += f"METHOD IDENTIFICATION: {varga_name} - {birth_name}\n"
    analysis += f"{'='*120}\n"
    
    if not jhora_data or all(v == "N/A" for v in jhora_data.values()):
        analysis += "⏳ JHora data not available yet.\n"
        return analysis
    
    jhora_match_maitreya8 = jhora_data == maitreya8_data
    jhora_match_our_engine = jhora_data == our_engine_data
    
    analysis += f"\nJHora vs Maitreya8: {'✅ MATCH' if jhora_match_maitreya8 else '❌ DIFFER'}\n"
    analysis += f"JHora vs Our Engine: {'✅ MATCH' if jhora_match_our_engine else '❌ DIFFER'}\n"
    
    if jhora_match_maitreya8:
        analysis += f"\n✅ CONCLUSION: JHora uses Maitreya8 method for {varga_name}\n"
        analysis += f"   → Adopt Maitreya8 formula\n"
    elif jhora_match_our_engine:
        analysis += f"\n✅ CONCLUSION: JHora uses Our Engine method for {varga_name}\n"
        analysis += f"   → Keep Our Engine formula\n"
    else:
        analysis += f"\n❌ CONCLUSION: JHora uses DIFFERENT method for {varga_name}\n"
        analysis += f"   → JHora method must be reverse-engineered\n"
        analysis += f"   → Document exact differences\n"
    
    analysis += f"{'='*120}\n"
    
    return analysis


def main():
    """Main comparison function."""
    print("="*120)
    print("JHORA GROUND TRUTH COMPARISON FRAMEWORK")
    print("="*120)
    print("\nThis framework compares D4, D7, D30 against JHora ground truth.")
    print("JHora data must be provided manually (visual confirmation from JHora software).\n")
    
    # Load existing data
    comparison_data = load_comparison_data()
    if not comparison_data:
        return
    
    print("\n" + "="*120)
    print("COMPARISON TABLES")
    print("="*120)
    
    verification_status = {}
    
    for varga_type in FOCUS_VARGAS:
        varga_name = f"D{varga_type}"
        print(f"\n{'='*120}")
        print(f"VARGA: {varga_name}")
        print(f"{'='*120}")
        
        varga_verified = True
        
        for birth in VERIFIED_BIRTHS:
            birth_name = birth["name"]
            
            # Get data
            jhora_data = JHORA_GROUND_TRUTH.get(varga_name, {}).get(birth_name, {})
            prokerala_data = PROKERALA_GROUND_TRUTH.get(varga_name, {}).get(birth_name, {})
            
            birth_data = comparison_data.get(birth_name, {})
            varga_data = birth_data.get(varga_name, {})
            maitreya8_data = varga_data.get("maitreya8", {})
            our_engine_data = varga_data.get("our_engine", {})
            
            # Generate table
            table, all_match, match_count = generate_comparison_table(
                varga_type, birth, jhora_data, prokerala_data,
                maitreya8_data, our_engine_data
            )
            print(table)
            
            if not all_match or match_count < 10:
                varga_verified = False
            
            # Method identification
            if jhora_data and any(v != "N/A" for v in jhora_data.values()):
                analysis = analyze_method_alignment(
                    varga_type, birth_name, jhora_data,
                    maitreya8_data, our_engine_data
                )
                print(analysis)
        
        verification_status[varga_name] = "✅ VERIFIED" if varga_verified else "❌ NOT VERIFIED"
    
    # Summary
    print("\n" + "="*120)
    print("VERIFICATION SUMMARY")
    print("="*120)
    for varga_name, status in verification_status.items():
        print(f"{varga_name}: {status}")
    print("="*120)
    
    print("\n" + "="*120)
    print("INSTRUCTIONS FOR ADDING JHORA DATA")
    print("="*120)
    print("\nTo add JHora ground truth data, edit this file and update:")
    print("  JHORA_GROUND_TRUTH['D4']['Birth 1'] = {")
    print("    'Ascendant': 'Sign',")
    print("    'Sun': 'Sign',")
    print("    ...")
    print("  }")
    print("\nThen re-run this script to generate comparison tables.")
    print("="*120 + "\n")


if __name__ == "__main__":
    main()

