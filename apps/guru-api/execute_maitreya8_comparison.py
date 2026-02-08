#!/usr/bin/env python3
"""
Maitreya8 Comparison Execution Script
Generates Maitreya8 outputs and compares with JHora, Prokerala, and our engine.

NO CODE CHANGES - Only data collection and reporting.
"""

import sys
import os
import requests
import json
from typing import Dict, List, Optional, Tuple

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

# VARGA TYPES TO VERIFY
VARGA_TYPES = [3, 4, 7, 10, 12, 16, 20, 27, 30, 40, 45, 60]

# PLANETS TO EXTRACT
PLANETS = ["Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

API_BASE_URL = "http://localhost:8000"


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
    
    # Try different possible keys (API uses "degree")
    if "degree" in planet_data:
        return float(planet_data["degree"])
    elif "longitude" in planet_data:
        return float(planet_data["longitude"])
    elif "lon" in planet_data:
        return float(planet_data["lon"])
    elif "longitude_deg" in planet_data:
        return float(planet_data["longitude_deg"])
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


def calculate_maitreya8_varga_sign(longitude: float, varga_type: int) -> str:
    """Calculate Maitreya8 varga sign."""
    if longitude is None:
        return "N/A"
    sign_idx = calculate_maitreya8_varga(longitude, varga_type, mode=0)  # Use Parasara mode
    return SIGN_NAMES[sign_idx]


def calculate_our_engine_varga_sign(longitude: float, varga_type: int) -> str:
    """Calculate our engine varga sign."""
    if longitude is None:
        return "N/A"
    
    try:
        from jyotish.varga_drik import calculate_varga_sign
        sign_idx = calculate_varga_sign(
            int(longitude // 30),  # sign_index
            longitude % 30,        # degrees_in_sign
            f"D{varga_type}"
        )
        return SIGN_NAMES[sign_idx]
    except Exception as e:
        return f"ERROR: {e}"


def generate_comparison_table(birth: Dict, varga_type: int, 
                              maitreya8_data: Dict, our_engine_data: Dict,
                              jhora_data: Optional[Dict] = None,
                              prokerala_data: Optional[Dict] = None) -> str:
    """Generate comparison table for a varga."""
    varga_name = f"D{varga_type}"
    
    table = f"\n{'='*120}\n"
    table += f"VARGA: {varga_name} | BIRTH: {birth['name']} ({birth['dob']} {birth['time']} IST)\n"
    table += f"{'='*120}\n"
    table += f"{'Planet':<12} | {'JHora':<12} | {'Prokerala':<12} | {'Maitreya8':<12} | {'Our Engine':<12} | {'Status'}\n"
    table += f"{'-'*120}\n"
    
    all_match = True
    
    for planet in PLANETS:
        maitreya8_sign = maitreya8_data.get(planet, "N/A")
        our_sign = our_engine_data.get(planet, "N/A")
        jhora_sign = jhora_data.get(planet, "N/A") if jhora_data else "N/A"
        prokerala_sign = prokerala_data.get(planet, "N/A") if prokerala_data else "N/A"
        
        # Check if all match (when data is available)
        if jhora_data and prokerala_data:
            if (maitreya8_sign == jhora_sign == prokerala_sign == our_sign and 
                maitreya8_sign != "N/A"):
                status = "✅ PASS"
            else:
                status = "❌ FAIL"
                all_match = False
        elif jhora_data:
            if maitreya8_sign == jhora_sign == our_sign and maitreya8_sign != "N/A":
                status = "✅ PASS"
            else:
                status = "⚠️  PARTIAL"
                all_match = False
        else:
            status = "⏳ PENDING"
        
        table += f"{planet:<12} | {jhora_sign:<12} | {prokerala_sign:<12} | {maitreya8_sign:<12} | {our_sign:<12} | {status}\n"
    
    table += f"{'-'*120}\n"
    
    if jhora_data and prokerala_data:
        if all_match:
            table += f"STATUS: ✅ VERIFIED (100% match with JHora and Prokerala)\n"
        else:
            table += f"STATUS: ❌ NOT VERIFIED (mismatches found)\n"
    elif jhora_data:
        table += f"STATUS: ⚠️  PARTIAL (JHora data available, Prokerala pending)\n"
    else:
        table += f"STATUS: ⏳ PENDING (JHora/Prokerala data not available)\n"
    
    table += f"{'='*120}\n"
    
    return table


def main():
    """Main execution function."""
    print("="*120)
    print("MAITREYA8 COMPARISON EXECUTION")
    print("="*120)
    print("\nGenerating Maitreya8 outputs and comparing with our engine...")
    print("JHora and Prokerala data will be inserted when available.\n")
    
    results = {}
    
    for birth in VERIFIED_BIRTHS:
        print(f"\n{'='*120}")
        print(f"Processing: {birth['name']} ({birth['dob']} {birth['time']} IST)")
        print(f"{'='*120}")
        
        # Fetch D1 data
        d1_data = fetch_d1_data(birth)
        if not d1_data:
            print(f"❌ Failed to fetch D1 data for {birth['name']}")
            continue
        
        birth_results = {}
        
        for varga_type in VARGA_TYPES:
            varga_name = f"D{varga_type}"
            print(f"\n  Calculating {varga_name}...")
            
            maitreya8_signs = {}
            our_engine_signs = {}
            
            for planet in PLANETS:
                longitude = get_planet_longitude(d1_data, planet)
                if longitude is None:
                    print(f"    ⚠️  {planet}: Longitude not found")
                    maitreya8_signs[planet] = "N/A"
                    our_engine_signs[planet] = "N/A"
                    continue
                
                # Calculate Maitreya8
                maitreya8_sign = calculate_maitreya8_varga_sign(longitude, varga_type)
                maitreya8_signs[planet] = maitreya8_sign
                
                # Calculate our engine
                our_sign = calculate_our_engine_varga_sign(longitude, varga_type)
                our_engine_signs[planet] = our_sign
            
            birth_results[varga_name] = {
                "maitreya8": maitreya8_signs,
                "our_engine": our_engine_signs
            }
        
        results[birth['name']] = birth_results
    
    # Generate comparison tables
    print("\n\n" + "="*120)
    print("COMPARISON TABLES")
    print("="*120)
    
    for birth in VERIFIED_BIRTHS:
        birth_results = results.get(birth['name'], {})
        
        for varga_type in VARGA_TYPES:
            varga_name = f"D{varga_type}"
            varga_data = birth_results.get(varga_name, {})
            
            if not varga_data:
                continue
            
            # Generate table (JHora/Prokerala data will be added when available)
            table = generate_comparison_table(
                birth, varga_type,
                varga_data.get("maitreya8", {}),
                varga_data.get("our_engine", {}),
                jhora_data=None,  # Will be added when available
                prokerala_data=None  # Will be added when available
            )
            print(table)
    
    # Save results to JSON for later analysis
    output_file = "maitreya8_comparison_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_file}")
    print("\n" + "="*120)
    print("NEXT STEPS:")
    print("="*120)
    print("1. Add JHora planet→sign data to comparison tables")
    print("2. Add Prokerala planet→sign data to comparison tables")
    print("3. Re-run comparison to get final VERIFIED/NOT VERIFIED status")
    print("4. Document exact mismatches and reasons")
    print("="*120 + "\n")


if __name__ == "__main__":
    main()

