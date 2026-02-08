#!/usr/bin/env python3
"""
D3 (Drekkana) JHora Verification - FOCUSED EFFORT
Compares D3 against JHora ground truth for ALL THREE births.

NO CODE CHANGES - Only data collection and reporting.
"""

import json
import sys
import os
import requests
from typing import Dict, Optional

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.dirname(__file__))

from maitreya8_python_implementation import calculate_maitreya8_varga, SIGN_NAMES

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

# PLANETS TO EXTRACT
PLANETS = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

API_BASE_URL = "http://localhost:8000"

# JHora D3 Ground Truth (to be filled)
JHORA_D3_GROUND_TRUTH = {
    "Birth 1": {
        # To be filled: Ascendant, Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu
    },
    "Birth 2": {
        # To be filled
    },
    "Birth 3": {
        # Known: Moon = Aquarius, Jupiter = Cancer (from user confirmation)
        # Rest to be filled
    }
}

# Prokerala D3 Ground Truth (to be filled)
PROKERALA_D3_GROUND_TRUTH = {
    "Birth 1": {},
    "Birth 2": {},
    "Birth 3": {
        # Known: Moon = Aquarius, Jupiter = Cancer (matches JHora)
        # Rest to be filled
    }
}


def fetch_d1_data(birth: Dict) -> Optional[Dict]:
    """Fetch D1 chart data from our API."""
    url = f"{API_BASE_URL}/api/v1/kundli"
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
        print(f"❌ Error fetching D1 data for {birth['name']}: {e}")
        return None


def extract_longitude(planet_data: Dict) -> Optional[float]:
    """Extract longitude from planet data."""
    if not planet_data:
        return None
    if "degree" in planet_data:
        return float(planet_data["degree"])
    elif "longitude" in planet_data:
        return float(planet_data["longitude"])
    return None


def get_planet_longitude(d1_data: Dict, planet_name: str) -> Optional[float]:
    """Get planet longitude from D1 data."""
    if planet_name == "Ascendant":
        asc = d1_data.get("Ascendant", {})
        return extract_longitude(asc)
    else:
        planets = d1_data.get("Planets", {})
        planet_data = planets.get(planet_name, {})
        return extract_longitude(planet_data)


def calculate_our_engine_d3(longitude: float) -> str:
    """Calculate our engine D3 sign."""
    try:
        from jyotish.varga_drik import calculate_varga_sign
        sign_idx = calculate_varga_sign(
            int(longitude // 30),
            longitude % 30,
            "D3"
        )
        return SIGN_NAMES[sign_idx]
    except Exception as e:
        return f"ERROR: {e}"


def calculate_maitreya8_d3(longitude: float) -> str:
    """Calculate Maitreya8 D3 sign."""
    sign_idx = calculate_maitreya8_varga(longitude, 3, mode=0)
    return SIGN_NAMES[sign_idx]


def generate_d3_comparison_table(birth: Dict,
                                  jhora_data: Dict,
                                  prokerala_data: Dict,
                                  our_engine_data: Dict,
                                  maitreya8_data: Dict) -> Tuple[str, bool, int]:
    """Generate D3 comparison table."""
    birth_name = birth["name"]
    
    table = f"\n{'='*120}\n"
    table += f"D3 (DREKKANA) VERIFICATION | BIRTH: {birth_name} ({birth['dob']} {birth['time']} IST)\n"
    table += f"{'='*120}\n"
    table += f"{'Planet':<12} | {'JHora':<12} | {'Prokerala':<12} | {'Our Engine':<15} | {'Maitreya8':<12} | {'Status'}\n"
    table += f"{'-'*120}\n"
    
    all_match = True
    match_count = 0
    
    for planet in PLANETS:
        jhora_sign = jhora_data.get(planet, "N/A")
        prokerala_sign = prokerala_data.get(planet, "N/A")
        our_sign = our_engine_data.get(planet, "N/A")
        maitreya8_sign = maitreya8_data.get(planet, "N/A")
        
        # Check if all match
        if (jhora_sign != "N/A" and prokerala_sign != "N/A" and
            our_sign != "N/A" and maitreya8_sign != "N/A"):
            if jhora_sign == prokerala_sign == our_sign:
                status = "✅ PASS"
                match_count += 1
            else:
                status = "❌ FAIL"
                all_match = False
                # Highlight specific mismatches
                if jhora_sign != our_sign:
                    status += f" (Our Engine ≠ JHora)"
                if prokerala_sign != our_sign:
                    status += f" (Our Engine ≠ Prokerala)"
        elif jhora_sign != "N/A":
            # Only JHora data available
            if jhora_sign == our_sign:
                status = "✅ PASS (JHora)"
                match_count += 1
            else:
                status = "❌ FAIL (Our Engine ≠ JHora)"
                all_match = False
        else:
            status = "⏳ PENDING"
        
        table += f"{planet:<12} | {jhora_sign:<12} | {prokerala_sign:<12} | {our_sign:<15} | {maitreya8_sign:<12} | {status}\n"
    
    table += f"{'-'*120}\n"
    table += f"Match Rate: {match_count}/10 planets\n"
    
    if jhora_data and any(v != "N/A" for v in jhora_data.values()):
        if all_match and match_count == 10:
            table += f"STATUS: ✅ VERIFIED (100% match with JHora and Prokerala)\n"
        else:
            table += f"STATUS: ❌ NOT VERIFIED (mismatches found)\n"
            # List mismatches
            mismatches = []
            for planet in PLANETS:
                jhora_sign = jhora_data.get(planet, "N/A")
                our_sign = our_engine_data.get(planet, "N/A")
                if jhora_sign != "N/A" and our_sign != "N/A" and jhora_sign != our_sign:
                    mismatches.append(f"{planet}: Our={our_sign}, JHora={jhora_sign}")
            if mismatches:
                table += f"Mismatches: {', '.join(mismatches)}\n"
    else:
        table += f"STATUS: ⏳ PENDING (JHora data not available)\n"
    
    table += f"{'='*120}\n"
    
    return table, all_match, match_count


def main():
    """Main verification function."""
    print("="*120)
    print("D3 (DREKKANA) JHORA VERIFICATION - FOCUSED EFFORT")
    print("="*120)
    print("\n⚠️  D3 STATUS: NOT VERIFIED")
    print("⚠️  Reason: Mismatches JHora for Moon & Jupiter (Birth 3)")
    print("⚠️  All other vargas: BLOCKED until D3 verified\n")
    
    # Load existing comparison data
    try:
        with open("maitreya8_comparison_results.json", "r") as f:
            comparison_data = json.load(f)
    except FileNotFoundError:
        print("❌ maitreya8_comparison_results.json not found. Run execute_maitreya8_comparison.py first.")
        return
    
    print("="*120)
    print("GENERATING D3 COMPARISON TABLES")
    print("="*120)
    
    all_births_verified = True
    
    for birth in VERIFIED_BIRTHS:
        birth_name = birth["name"]
        
        # Get JHora and Prokerala data
        jhora_data = JHORA_D3_GROUND_TRUTH.get(birth_name, {})
        prokerala_data = PROKERALA_D3_GROUND_TRUTH.get(birth_name, {})
        
        # Get our engine and Maitreya8 data
        birth_data = comparison_data.get(birth_name, {})
        d3_data = birth_data.get("D3", {})
        our_engine_data = d3_data.get("our_engine", {})
        maitreya8_data = d3_data.get("maitreya8", {})
        
        # Generate table
        table, all_match, match_count = generate_d3_comparison_table(
            birth, jhora_data, prokerala_data,
            our_engine_data, maitreya8_data
        )
        print(table)
        
        if not all_match or match_count < 10:
            all_births_verified = False
    
    # Final summary
    print("\n" + "="*120)
    print("D3 VERIFICATION SUMMARY")
    print("="*120)
    
    if all_births_verified:
        print("✅ D3 = VERIFIED (100% match with JHora and Prokerala for all 3 births)")
    else:
        print("❌ D3 = NOT VERIFIED (mismatches found)")
        print("\n⚠️  ALL OTHER VARGAS BLOCKED until D3 is verified")
    
    print("\n" + "="*120)
    print("INSTRUCTIONS FOR ADDING JHORA DATA")
    print("="*120)
    print("\nTo add JHora D3 ground truth data, edit this file and update:")
    print("  JHORA_D3_GROUND_TRUTH['Birth 1'] = {")
    print("    'Ascendant': 'Sign',")
    print("    'Sun': 'Sign',")
    print("    'Moon': 'Sign',")
    print("    ...")
    print("  }")
    print("\nThen re-run this script to generate comparison tables.")
    print("="*120 + "\n")


if __name__ == "__main__":
    main()

