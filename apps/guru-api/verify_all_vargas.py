#!/usr/bin/env python3
"""
Comprehensive Varga Verification Script
Compares all divisional charts against JHora for three verified birth charts.

VERIFIED BIRTH CHARTS (GROUND TRUTH):
1. 16-May-1995, 18:38 IST — Bangalore
2. 07-Apr-1996, 11:59 IST — Bangalore
3. 07-Apr-2001, 11:00 IST — Bangalore

Ayanamsa: Lahiri
Authority: Jagannatha Hora (JHora)
Tolerance: ZERO (even one planet mismatch = FAIL)
"""

import sys
import json
import requests
from typing import Dict, List, Optional

# VERIFIED BIRTH CHARTS (GROUND TRUTH)
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

# DIVISIONAL CHARTS TO VERIFY
VARGA_CHARTS = {
    "D1": {"name": "Rasi Chart", "status": "VERIFIED"},
    "D2": {"name": "Hora Chart", "status": "VERIFIED"},
    "D3": {"name": "Drekkana Chart", "status": "NOT VERIFIED"},
    "D4": {"name": "Chaturthamsa Chart", "status": "NOT VERIFIED"},
    "D7": {"name": "Saptamsa Chart", "status": "NOT VERIFIED"},
    "D9": {"name": "Navamsa Chart", "status": "VERIFIED"},
    "D10": {"name": "Dashamsa Chart", "status": "NOT VERIFIED"},
    "D12": {"name": "Dwadashamsa Chart", "status": "NOT VERIFIED"},
    "D16": {"name": "Shodasamsa Chart", "status": "NOT VERIFIED"},
    "D20": {"name": "Vimsamsa Chart", "status": "NOT VERIFIED"},
    "D24": {"name": "Chaturvimsamsa Chart", "status": "VERIFIED (Method 1)"},
    "D27": {"name": "Saptavimsamsa Chart", "status": "NOT VERIFIED"},
    "D30": {"name": "Trimsamsa Chart", "status": "NOT VERIFIED"},
    "D40": {"name": "Khavedamsa Chart", "status": "NOT VERIFIED"},
    "D45": {"name": "Akshavedamsa Chart", "status": "NOT VERIFIED"},
    "D60": {"name": "Shashtiamsa Chart", "status": "NOT VERIFIED"},
}

# Sign index to name mapping
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
        
        # Extract varga chart from response
        varga_data = data.get(varga_key, {})
        if not varga_data:
            # Try nested structure
            varga_data = data.get("data", {}).get("kundli", {}).get(varga_key, {})
        
        return varga_data if varga_data else None
    except Exception as e:
        print(f"❌ Error fetching {varga_key} for {birth['name']}: {e}")
        return None


def extract_planet_signs(varga_data: Dict) -> Dict[str, str]:
    """Extract planet→sign mappings from varga chart data."""
    planet_signs = {}
    
    # Extract Ascendant
    ascendant = varga_data.get("Ascendant", {})
    if ascendant:
        sign_index = ascendant.get("sign_index")
        if sign_index is not None:
            planet_signs["Ascendant"] = get_sign_name(sign_index)
    
    # Extract planets
    planets = varga_data.get("Planets", {})
    for planet_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        planet = planets.get(planet_name, {})
        if planet:
            sign_index = planet.get("sign_index")
            if sign_index is not None:
                planet_signs[planet_name] = get_sign_name(sign_index)
    
    return planet_signs


def compare_with_jhora(engine_signs: Dict[str, str], jhora_signs: Dict[str, str], birth_name: str, varga_key: str) -> Dict:
    """Compare engine output with JHora ground truth."""
    mismatches = []
    matches = []
    
    all_planets = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    
    for planet in all_planets:
        engine_sign = engine_signs.get(planet)
        jhora_sign = jhora_signs.get(planet)
        
        if engine_sign and jhora_sign:
            if engine_sign == jhora_sign:
                matches.append(planet)
            else:
                mismatches.append({
                    "planet": planet,
                    "engine": engine_sign,
                    "jhora": jhora_sign
                })
        elif engine_sign and not jhora_sign:
            mismatches.append({
                "planet": planet,
                "engine": engine_sign,
                "jhora": "MISSING"
            })
        elif not engine_sign and jhora_sign:
            mismatches.append({
                "planet": planet,
                "engine": "MISSING",
                "jhora": jhora_sign
            })
    
    return {
        "birth": birth_name,
        "varga": varga_key,
        "matches": matches,
        "mismatches": mismatches,
        "match_count": len(matches),
        "total_planets": len([p for p in all_planets if engine_signs.get(p) or jhora_signs.get(p)]),
        "is_verified": len(mismatches) == 0
    }


def print_verification_report(results: List[Dict], varga_key: str):
    """Print detailed verification report."""
    print("\n" + "=" * 100)
    print(f"{varga_key} VERIFICATION REPORT")
    print("=" * 100)
    
    all_verified = all(r["is_verified"] for r in results)
    
    for result in results:
        print(f"\n{result['birth']}:")
        print(f"  Matches: {result['match_count']}/{result['total_planets']} planets")
        
        if result["mismatches"]:
            print(f"  ❌ MISMATCHES ({len(result['mismatches'])}):")
            for mismatch in result["mismatches"]:
                print(f"    {mismatch['planet']:<12} Engine: {mismatch['engine']:<15} JHora: {mismatch['jhora']}")
        else:
            print(f"  ✅ ALL PLANETS MATCH")
    
    print("\n" + "-" * 100)
    if all_verified:
        print(f"✅ {varga_key} is VERIFIED (100% match across all three births)")
    else:
        print(f"❌ {varga_key} is NOT VERIFIED (mismatches found)")
    print("=" * 100 + "\n")


def main():
    """Main verification function."""
    print("=" * 100)
    print("COMPREHENSIVE VARGA VERIFICATION (JHora Authority)")
    print("=" * 100)
    print("\nVerified Birth Charts:")
    for birth in VERIFIED_BIRTHS:
        print(f"  • {birth['name']}: {birth['dob']} {birth['time']} IST, Bangalore")
    print(f"\nAyanamsa: Lahiri")
    print(f"Authority: Jagannatha Hora (JHora)")
    print(f"Tolerance: ZERO (even one planet mismatch = FAIL)")
    print("-" * 100)
    
    # For now, this script will fetch engine data
    # User must provide JHora ground truth data for comparison
    print("\n⚠️  NOTE: This script fetches engine data.")
    print("   You must provide JHora ground truth data for comparison.")
    print("   Use the template format below to add JHora data.\n")
    
    # Example: Fetch D3 data for all three births
    varga_to_test = "D3"  # Start with D3
    
    print(f"\n📊 Fetching {varga_to_test} data for all three births...")
    print("-" * 100)
    
    engine_results = {}
    for birth in VERIFIED_BIRTHS:
        print(f"\nFetching {varga_to_test} for {birth['name']}...")
        varga_data = fetch_varga_chart(birth, varga_to_test)
        
        if varga_data:
            planet_signs = extract_planet_signs(varga_data)
            engine_results[birth["name"]] = planet_signs
            
            print(f"✅ {birth['name']} {varga_to_test} data extracted:")
            for planet, sign in sorted(planet_signs.items()):
                print(f"   {planet:<12} → {sign}")
        else:
            print(f"❌ Failed to fetch {varga_to_test} for {birth['name']}")
    
    # Template for JHora ground truth (user must fill this)
    print("\n" + "=" * 100)
    print("JHORA GROUND TRUTH TEMPLATE (Fill this with JHora data)")
    print("=" * 100)
    print("\nCopy this template and fill with JHora planet→sign data:\n")
    
    jhora_template = {}
    for birth in VERIFIED_BIRTHS:
        jhora_template[birth["name"]] = {
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
        }
    
    print(json.dumps(jhora_template, indent=2))
    print("\n" + "=" * 100)
    print("After filling JHora data, run comparison to identify mismatches.")
    print("=" * 100 + "\n")


if __name__ == "__main__":
    main()

