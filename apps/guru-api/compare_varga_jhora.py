#!/usr/bin/env python3
"""
Varga Comparison Script
Compares engine output with JHora ground truth and identifies exact mismatches.

Usage:
1. Run verify_all_vargas.py to get engine data
2. Fill JHora ground truth data
3. Run this script to compare and identify mismatches
"""

import json
import sys
from typing import Dict, List

# JHORA GROUND TRUTH DATA (Fill this with actual JHora data)
# Format: { "Birth Name": { "Planet": "Sign", ... } }
JHORA_GROUND_TRUTH = {
    # Example structure - REPLACE with actual JHora data
    "Birth 1": {
        "Ascendant": "???",  # Fill from JHora
        "Sun": "???",
        "Moon": "???",
        "Mars": "???",
        "Mercury": "???",
        "Jupiter": "???",
        "Venus": "???",
        "Saturn": "???",
        "Rahu": "???",
        "Ketu": "???"
    },
    "Birth 2": {
        "Ascendant": "???",
        "Sun": "???",
        "Moon": "???",
        "Mars": "???",
        "Mercury": "???",
        "Jupiter": "???",
        "Venus": "???",
        "Saturn": "???",
        "Rahu": "???",
        "Ketu": "???"
    },
    "Birth 3": {
        "Ascendant": "???",
        "Sun": "???",
        "Moon": "???",
        "Mars": "???",
        "Mercury": "???",
        "Jupiter": "???",
        "Venus": "???",
        "Saturn": "???",
        "Rahu": "???",
        "Ketu": "???"
    }
}

# ENGINE DATA (From verify_all_vargas.py output or API)
ENGINE_DATA = {
    # This will be populated from API or previous script
    "Birth 1": {},
    "Birth 2": {},
    "Birth 3": {}
}


def normalize_sign_name(sign: str) -> str:
    """Normalize sign name for comparison."""
    sign_lower = sign.lower().strip()
    sign_map = {
        "aries": "Aries", "mesha": "Aries",
        "taurus": "Taurus", "vrishabha": "Taurus",
        "gemini": "Gemini", "mithuna": "Gemini",
        "cancer": "Cancer", "karka": "Cancer", "karkata": "Cancer",
        "leo": "Leo", "simha": "Leo",
        "virgo": "Virgo", "kanya": "Virgo",
        "libra": "Libra", "tula": "Libra",
        "scorpio": "Scorpio", "vrishchika": "Scorpio",
        "sagittarius": "Sagittarius", "dhanu": "Sagittarius",
        "capricorn": "Capricorn", "makara": "Capricorn",
        "aquarius": "Aquarius", "kumbha": "Aquarius",
        "pisces": "Pisces", "meena": "Pisces"
    }
    return sign_map.get(sign_lower, sign)


def compare_varga(varga_key: str, engine_data: Dict, jhora_data: Dict) -> Dict:
    """Compare engine output with JHora for a specific varga."""
    all_planets = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    
    results = {
        "varga": varga_key,
        "births": {}
    }
    
    for birth_name in ["Birth 1", "Birth 2", "Birth 3"]:
        engine_signs = engine_data.get(birth_name, {})
        jhora_signs = jhora_data.get(birth_name, {})
        
        mismatches = []
        matches = []
        
        for planet in all_planets:
            engine_sign = normalize_sign_name(engine_signs.get(planet, ""))
            jhora_sign = normalize_sign_name(jhora_signs.get(planet, ""))
            
            if not engine_sign or not jhora_sign:
                if jhora_sign and jhora_sign != "???":
                    mismatches.append({
                        "planet": planet,
                        "engine": engine_sign or "MISSING",
                        "jhora": jhora_sign,
                        "status": "MISSING"
                    })
                continue
            
            if engine_sign == jhora_sign:
                matches.append(planet)
            else:
                mismatches.append({
                    "planet": planet,
                    "engine": engine_sign,
                    "jhora": jhora_sign,
                    "status": "MISMATCH"
                })
        
        results["births"][birth_name] = {
            "matches": matches,
            "mismatches": mismatches,
            "match_count": len(matches),
            "total_planets": len([p for p in all_planets if engine_signs.get(p) or jhora_signs.get(p)]),
            "is_verified": len(mismatches) == 0
        }
    
    # Overall status
    all_verified = all(r["is_verified"] for r in results["births"].values())
    results["overall_status"] = "VERIFIED" if all_verified else "NOT VERIFIED"
    
    return results


def print_comparison_report(results: Dict):
    """Print detailed comparison report."""
    varga_key = results["varga"]
    print("\n" + "=" * 100)
    print(f"{varga_key} COMPARISON REPORT (Engine vs JHora)")
    print("=" * 100)
    
    for birth_name in ["Birth 1", "Birth 2", "Birth 3"]:
        birth_result = results["births"][birth_name]
        print(f"\n{birth_name}:")
        print(f"  Matches: {birth_result['match_count']}/{birth_result['total_planets']} planets")
        
        if birth_result["mismatches"]:
            print(f"  ❌ MISMATCHES ({len(birth_result['mismatches'])}):")
            for mismatch in birth_result["mismatches"]:
                print(f"    {mismatch['planet']:<12} Engine: {mismatch['engine']:<15} JHora: {mismatch['jhora']:<15} [{mismatch['status']}]")
        else:
            print(f"  ✅ ALL PLANETS MATCH")
    
    print("\n" + "-" * 100)
    print(f"Overall Status: {results['overall_status']}")
    
    if results["overall_status"] == "VERIFIED":
        print(f"✅ {varga_key} is VERIFIED (100% match across all three births)")
    else:
        print(f"❌ {varga_key} is NOT VERIFIED")
        print(f"   Fix required: Math logic must be corrected to match JHora")
    print("=" * 100 + "\n")


def main():
    """Main comparison function."""
    if len(sys.argv) < 2:
        print("Usage: python compare_varga_jhora.py <VARGA_KEY>")
        print("Example: python compare_varga_jhora.py D3")
        print("\nThis script compares engine output with JHora ground truth.")
        print("You must:")
        print("1. Fill JHORA_GROUND_TRUTH in this script with actual JHora data")
        print("2. Fill ENGINE_DATA with engine output (or fetch from API)")
        print("3. Run: python compare_varga_jhora.py <VARGA_KEY>")
        sys.exit(1)
    
    varga_key = sys.argv[1].upper()
    
    if varga_key not in ["D3", "D4", "D7", "D10", "D12", "D16", "D20", "D27", "D30", "D40", "D45", "D60"]:
        print(f"❌ Invalid varga key: {varga_key}")
        print("   Valid keys: D3, D4, D7, D10, D12, D16, D20, D27, D30, D40, D45, D60")
        sys.exit(1)
    
    # Check if JHora data is filled
    if any("???" in str(v) for birth_data in JHORA_GROUND_TRUTH.values() for v in birth_data.values()):
        print("⚠️  WARNING: JHORA_GROUND_TRUTH contains placeholder values (???)")
        print("   Please fill with actual JHora data before running comparison.")
        print("\n   Open JHora and record planet→sign for:")
        print("   • Birth 1: 1995-05-16 18:38 IST Bangalore")
        print("   • Birth 2: 1996-04-07 11:59 IST Bangalore")
        print("   • Birth 3: 2001-04-07 11:00 IST Bangalore")
        sys.exit(1)
    
    # Compare
    results = compare_varga(varga_key, ENGINE_DATA, JHORA_GROUND_TRUTH)
    print_comparison_report(results)


if __name__ == "__main__":
    main()

