#!/usr/bin/env python3
"""
Systematic Varga Fixing Script
Fixes one divisional chart at a time based on JHora ground truth.

WORKFLOW:
1. User provides JHora ground truth for ONE varga (e.g., D3) for all three births
2. Script compares engine output with JHora
3. Identifies exact mismatches
4. Helps derive correct math logic
5. Verifies fix against all three births

VERIFIED BIRTH CHARTS:
1. 1995-05-16, 18:38 IST — Bangalore
2. 1996-04-07, 11:59 IST — Bangalore
3. 2001-04-07, 11:00 IST — Bangalore

Ayanamsa: Lahiri
Authority: Jagannatha Hora (JHora)
"""

import sys
import json
import requests
from typing import Dict, List, Optional

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

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def get_sign_name(sign_index: int) -> str:
    """Convert sign index (0-11) to sign name."""
    return SIGN_NAMES[sign_index] if 0 <= sign_index < 12 else "Unknown"


def fetch_varga_chart(birth: Dict, varga_key: str, base_url: str = "http://localhost:8000") -> Optional[Dict]:
    """Fetch varga chart from API."""
    url = f"{base_url}/api/v1/kundli"
    params = {
        "dob": birth["dob"],
        "time": birth["time"],
        "lat": birth["lat"],
        "lon": birth["lon"],
        "timezone": birth["timezone"]
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        varga_data = data.get(varga_key, {})
        if not varga_data:
            varga_data = data.get("data", {}).get("kundli", {}).get(varga_key, {})
        
        return varga_data if varga_data else None
    except Exception as e:
        print(f"❌ Error fetching {varga_key} for {birth['name']}: {e}")
        return None


def extract_planet_signs(varga_data: Dict) -> Dict[str, str]:
    """Extract planet→sign mappings from varga chart data."""
    planet_signs = {}
    
    ascendant = varga_data.get("Ascendant", {})
    if ascendant:
        sign_index = ascendant.get("sign_index")
        if sign_index is not None:
            planet_signs["Ascendant"] = get_sign_name(sign_index)
    
    planets = varga_data.get("Planets", {})
    for planet_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        planet = planets.get(planet_name, {})
        if planet:
            sign_index = planet.get("sign_index")
            if sign_index is not None:
                planet_signs[planet_name] = get_sign_name(sign_index)
    
    return planet_signs


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


def compare_and_report(varga_key: str, engine_data: Dict, jhora_data: Dict):
    """Compare engine output with JHora and generate detailed mismatch report."""
    print("\n" + "=" * 100)
    print(f"{varga_key} VERIFICATION REPORT (Engine vs JHora)")
    print("=" * 100)
    
    all_planets = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    all_verified = True
    
    for birth in VERIFIED_BIRTHS:
        birth_name = birth["name"]
        engine_signs = engine_data.get(birth_name, {})
        jhora_signs = jhora_data.get(birth_name, {})
        
        print(f"\n{birth_name} ({birth['dob']} {birth['time']} IST):")
        print("-" * 100)
        
        mismatches = []
        matches = []
        
        for planet in all_planets:
            engine_sign = normalize_sign_name(engine_signs.get(planet, ""))
            jhora_sign = normalize_sign_name(jhora_signs.get(planet, ""))
            
            if not engine_sign or not jhora_sign or jhora_sign == "???":
                continue
            
            if engine_sign == jhora_sign:
                matches.append(planet)
                print(f"  ✅ {planet:<12} Engine: {engine_sign:<15} JHora: {jhora_sign:<15} MATCH")
            else:
                mismatches.append({
                    "planet": planet,
                    "engine": engine_sign,
                    "jhora": jhora_sign
                })
                print(f"  ❌ {planet:<12} Engine: {engine_sign:<15} JHora: {jhora_sign:<15} MISMATCH")
                all_verified = False
        
        print(f"\n  Summary: {len(matches)}/{len([p for p in all_planets if engine_signs.get(p) or jhora_signs.get(p)])} planets match")
        
        if mismatches:
            print(f"  ❌ {len(mismatches)} mismatches found - {varga_key} is NOT VERIFIED")
        else:
            print(f"  ✅ All planets match for {birth_name}")
    
    print("\n" + "=" * 100)
    if all_verified:
        print(f"✅ {varga_key} is VERIFIED (100% match across all three births)")
        print("   Status: READY FOR PRODUCTION")
    else:
        print(f"❌ {varga_key} is NOT VERIFIED")
        print("   Action Required: Fix math logic in varga_drik.py")
        print("   Rule: Derive universal formula from JHora behavior")
        print("   Prohibited: No planet-specific exceptions, no birth-specific hacks")
    print("=" * 100 + "\n")
    
    return all_verified


def main():
    """Main fixing function."""
    if len(sys.argv) < 2:
        print("Usage: python fix_varga_systematic.py <VARGA_KEY> [jhora_data.json]")
        print("\nExample: python fix_varga_systematic.py D3")
        print("         python fix_varga_systematic.py D3 jhora_d3_data.json")
        print("\nThis script:")
        print("1. Fetches engine data for specified varga")
        print("2. Compares with JHora ground truth")
        print("3. Identifies exact mismatches")
        print("4. Reports verification status")
        sys.exit(1)
    
    varga_key = sys.argv[1].upper()
    
    if varga_key not in ["D3", "D4", "D7", "D10", "D12", "D16", "D20", "D27", "D30", "D40", "D45", "D60"]:
        print(f"❌ Invalid varga key: {varga_key}")
        print("   Valid keys: D3, D4, D7, D10, D12, D16, D20, D27, D30, D40, D45, D60")
        sys.exit(1)
    
    print("=" * 100)
    print(f"SYSTEMATIC VARGA FIXING: {varga_key}")
    print("=" * 100)
    print("\nStep 1: Fetching engine data for all three births...")
    print("-" * 100)
    
    # Fetch engine data
    engine_data = {}
    for birth in VERIFIED_BIRTHS:
        print(f"Fetching {varga_key} for {birth['name']}...")
        varga_data = fetch_varga_chart(birth, varga_key)
        
        if varga_data:
            planet_signs = extract_planet_signs(varga_data)
            engine_data[birth["name"]] = planet_signs
            print(f"✅ {birth['name']} data extracted")
        else:
            print(f"❌ Failed to fetch {varga_key} for {birth['name']}")
            return
    
    # Load JHora data
    jhora_data = {}
    
    if len(sys.argv) >= 3:
        # Load from JSON file
        try:
            with open(sys.argv[2], 'r') as f:
                jhora_file_data = json.load(f)
                # Extract varga data for each birth
                for birth in VERIFIED_BIRTHS:
                    birth_name = birth["name"]
                    if birth_name in jhora_file_data.get("verified_births", {}):
                        jhora_data[birth_name] = jhora_file_data["verified_births"][birth_name].get(varga_key, {})
        except Exception as e:
            print(f"❌ Error loading JHora data from {sys.argv[2]}: {e}")
            print("   Please provide JHora data manually or fix the JSON file.")
            sys.exit(1)
    else:
        # Manual input template
        print("\n" + "=" * 100)
        print("JHORA GROUND TRUTH DATA REQUIRED")
        print("=" * 100)
        print("\nPlease provide JHora planet→sign data for each birth.")
        print("You can:")
        print("1. Fill jhora_ground_truth_template.json and pass it as argument")
        print("2. Or provide data manually when prompted\n")
        
        for birth in VERIFIED_BIRTHS:
            print(f"{birth['name']} ({birth['dob']} {birth['time']} IST):")
            jhora_data[birth["name"]] = {}
            for planet in ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
                engine_sign = engine_data.get(birth["name"], {}).get(planet, "N/A")
                jhora_sign = input(f"  {planet} (Engine: {engine_sign}, JHora: ").strip()
                if jhora_sign:
                    jhora_data[birth["name"]][planet] = jhora_sign
    
    # Compare and report
    print("\n" + "=" * 100)
    print("COMPARING ENGINE OUTPUT WITH JHORA GROUND TRUTH")
    print("=" * 100)
    
    is_verified = compare_and_report(varga_key, engine_data, jhora_data)
    
    if not is_verified:
        print("\n" + "=" * 100)
        print("NEXT STEPS FOR FIXING")
        print("=" * 100)
        print("\n1. Analyze mismatches to identify pattern")
        print("2. Derive universal math rule from JHora behavior")
        print("3. Update calculate_varga_sign() in varga_drik.py")
        print("4. Re-run this script to verify fix")
        print("5. Only mark VERIFIED when 100% match across all three births")
        print("=" * 100 + "\n")


if __name__ == "__main__":
    main()

