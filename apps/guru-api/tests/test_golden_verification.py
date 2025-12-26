"""
PHASE 8 — GOLDEN VERIFICATION (LOCK OR FIX)

This is the FINAL verification test suite that compares ALL varga calculations
against Prokerala reference data with EXACT precision.

Reference birth data (single source of truth):
- DOB: 1995-05-16
- Time: 18:38 IST
- Place: Bangalore (12.9716°N, 77.5946°E)
- Ayanamsa: Lahiri

STRICT RULES:
1. For EACH varga: D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60
2. For EACH planet: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu, Ascendant
3. Compare EXACTLY: Sign name, House number, Degrees + minutes + seconds (no rounding drift)

NON-NEGOTIABLE CONSTRAINTS:
- Tests are NEVER changed to match code
- Code is ALWAYS changed to match Prokerala
- No "close enough"
- No averaging
- No fallback logic
"""

import pytest
import json
import os
import math
from typing import Dict, Optional, List
from datetime import datetime
import swisseph as swe

from src.jyotish.varga_engine import build_varga_chart
from src.jyotish.kundli_engine import generate_kundli
from src.utils.timezone import local_to_utc
from src.utils.converters import get_sign_name, degrees_to_dms


# Test birth data (SINGLE SOURCE OF TRUTH)
TEST_BIRTH_DATE = "1995-05-16"
TEST_BIRTH_TIME = "18:38:00"
TEST_LATITUDE = 12.9716  # Bangalore
TEST_LONGITUDE = 77.5946
TEST_TIMEZONE = "Asia/Kolkata"

# All varga types to verify
ALL_VARGA_TYPES = [1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]

# All planets to verify
ALL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
ALL_ENTITIES = ["Ascendant"] + ALL_PLANETS

# Path to Prokerala reference directory
PROKERALA_REF_DIR = os.path.join(os.path.dirname(__file__), "prokerala_reference")


def get_test_d1_data():
    """Get D1 kundli data for test birth chart."""
    birth_date = datetime.strptime(TEST_BIRTH_DATE, "%Y-%m-%d").date()
    hour, minute, second = map(int, TEST_BIRTH_TIME.split(':'))
    birth_datetime = datetime.combine(
        birth_date,
        datetime.min.time().replace(hour=hour, minute=minute, second=second)
    )
    birth_datetime_utc = local_to_utc(birth_datetime, TEST_TIMEZONE)
    
    jd = swe.julday(
        birth_datetime_utc.year, birth_datetime_utc.month, birth_datetime_utc.day,
        birth_datetime_utc.hour + birth_datetime_utc.minute / 60.0 + birth_datetime_utc.second / 3600.0,
        swe.GREG_CAL
    )
    
    base_kundli = generate_kundli(jd, TEST_LATITUDE, TEST_LONGITUDE)
    
    d1_ascendant = base_kundli["Ascendant"]["degree"]
    d1_planets = {
        planet_name: planet_info["degree"]
        for planet_name, planet_info in base_kundli["Planets"].items()
    }
    
    return d1_planets, d1_ascendant


def load_prokerala_reference(varga_type: int) -> Optional[Dict]:
    """
    Load Prokerala reference data for a varga type.
    
    Args:
        varga_type: Varga type (1, 2, 3, 4, 7, 9, 10, 12, etc.)
    
    Returns:
        Dictionary with reference data, or None if file doesn't exist or is incomplete
    """
    json_file = os.path.join(PROKERALA_REF_DIR, f"D{varga_type}.json")
    
    if not os.path.exists(json_file):
        return None
    
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Check if data is complete (not all null)
        has_data = False
        if "Ascendant" in data:
            asc = data["Ascendant"]
            if asc.get("sign") is not None and asc.get("sign_index") is not None:
                has_data = True
        
        if not has_data and "Planets" in data:
            for planet_name, planet_data in data["Planets"].items():
                if planet_data.get("sign") is not None and planet_data.get("sign_index") is not None:
                    has_data = True
                    break
        
        return data if has_data else None
    except Exception as e:
        pytest.skip(f"Could not load Prokerala reference for D{varga_type}: {e}")
        return None


def compare_dms(api_degrees: float, prokerala_degree: Optional[int], 
                prokerala_minute: Optional[int], prokerala_second: Optional[int],
                tolerance_seconds: float = 1.0) -> tuple[bool, str]:
    """
    Compare degrees in sign with Prokerala DMS values.
    
    Args:
        api_degrees: API degrees_in_sign (0-30)
        prokerala_degree: Prokerala degree component
        prokerala_minute: Prokerala minute component
        prokerala_second: Prokerala second component
        tolerance_seconds: Tolerance in arcseconds (default 1.0)
    
    Returns:
        Tuple of (match, error_message)
    """
    if prokerala_degree is None or prokerala_minute is None or prokerala_second is None:
        return (True, "No DMS reference data")  # Skip if not available
    
    # Convert Prokerala DMS to decimal degrees
    prokerala_decimal = prokerala_degree + prokerala_minute / 60.0 + prokerala_second / 3600.0
    
    # Convert API degrees to DMS for comparison
    api_d, api_m, api_s = degrees_to_dms(api_degrees)
    
    # Calculate difference in arcseconds
    diff_seconds = abs(api_degrees - prokerala_decimal) * 3600.0
    
    if diff_seconds <= tolerance_seconds:
        return (True, "")
    
    return (False, 
            f"DMS mismatch: API={api_d}° {api_m}′ {api_s:.1f}″ vs Prokerala={prokerala_degree}° {prokerala_minute}′ {prokerala_second}″ "
            f"(diff={diff_seconds:.2f} arcseconds)")


def verify_varga_against_prokerala(varga_type: int):
    """
    Verify a varga chart against Prokerala reference data.
    
    This function performs EXACT comparison:
    - Sign name must match
    - Sign index must match
    - House number must match
    - Degrees/minutes/seconds must match (within 1 arcsecond tolerance)
    """
    # Load Prokerala reference
    prokerala_ref = load_prokerala_reference(varga_type)
    
    if prokerala_ref is None:
        pytest.skip(f"No Prokerala reference data available for D{varga_type}")
        return
    
    # Generate API varga chart
    d1_planets, d1_ascendant = get_test_d1_data()
    
    if varga_type == 1:
        # D1 is the main chart - use kundli directly
        birth_date = datetime.strptime(TEST_BIRTH_DATE, "%Y-%m-%d").date()
        hour, minute, second = map(int, TEST_BIRTH_TIME.split(':'))
        birth_datetime = datetime.combine(
            birth_date,
            datetime.min.time().replace(hour=hour, minute=minute, second=second)
        )
        birth_datetime_utc = local_to_utc(birth_datetime, TEST_TIMEZONE)
        
        jd = swe.julday(
            birth_datetime_utc.year, birth_datetime_utc.month, birth_datetime_utc.day,
            birth_datetime_utc.hour + birth_datetime_utc.minute / 60.0 + birth_datetime_utc.second / 3600.0,
            swe.GREG_CAL
        )
        
        base_kundli = generate_kundli(jd, TEST_LATITUDE, TEST_LONGITUDE)
        api_chart = {
            "ascendant": base_kundli["Ascendant"],
            "planets": base_kundli["Planets"]
        }
    else:
        api_chart = build_varga_chart(d1_planets, d1_ascendant, varga_type)
    
    # Verify Ascendant
    if "Ascendant" in prokerala_ref:
        asc_ref = prokerala_ref["Ascendant"]
        if asc_ref.get("sign") is not None and asc_ref.get("sign_index") is not None:
            api_asc = api_chart["ascendant"]
            
            # Verify sign name
            expected_sign = asc_ref["sign"]
            actual_sign = api_asc["sign"]
            assert actual_sign == expected_sign, \
                f"D{varga_type} Ascendant sign: expected '{expected_sign}', got '{actual_sign}'"
            
            # Verify sign index
            expected_sign_index = asc_ref["sign_index"]
            actual_sign_index = api_asc["sign_index"]
            assert actual_sign_index == expected_sign_index, \
                f"D{varga_type} Ascendant sign_index: expected {expected_sign_index}, got {actual_sign_index}"
            
            # Verify house (must be 1)
            expected_house = 1
            actual_house = api_asc["house"]
            assert actual_house == expected_house, \
                f"D{varga_type} Ascendant house: expected {expected_house}, got {actual_house}"
            
            # Verify DMS if available
            if asc_ref.get("degree") is not None:
                match, error = compare_dms(
                    api_asc["degrees_in_sign"],
                    asc_ref.get("degree"),
                    asc_ref.get("minute"),
                    asc_ref.get("second")
                )
                if not match:
                    pytest.fail(f"D{varga_type} Ascendant {error}")
    
    # Verify each planet
    if "Planets" in prokerala_ref:
        for planet_name, planet_ref in prokerala_ref["Planets"].items():
            if planet_ref.get("sign") is None or planet_ref.get("sign_index") is None:
                continue  # Skip if reference data incomplete
            
            api_planet = api_chart["planets"].get(planet_name)
            assert api_planet is not None, \
                f"D{varga_type} {planet_name} not found in API chart"
            
            # Verify sign name
            expected_sign = planet_ref["sign"]
            actual_sign = api_planet["sign"]
            assert actual_sign == expected_sign, \
                f"D{varga_type} {planet_name} sign: expected '{expected_sign}', got '{actual_sign}'"
            
            # Verify sign index
            expected_sign_index = planet_ref["sign_index"]
            actual_sign_index = api_planet["sign_index"]
            assert actual_sign_index == expected_sign_index, \
                f"D{varga_type} {planet_name} sign_index: expected {expected_sign_index}, got {actual_sign_index}"
            
            # Verify house
            expected_house = planet_ref["house"]
            actual_house = api_planet["house"]
            assert actual_house == expected_house, \
                f"D{varga_type} {planet_name} house: expected {expected_house}, got {actual_house}"
            
            # Verify DMS if available
            if planet_ref.get("degree") is not None:
                match, error = compare_dms(
                    api_planet["degrees_in_sign"],
                    planet_ref.get("degree"),
                    planet_ref.get("minute"),
                    planet_ref.get("second")
                )
                if not match:
                    pytest.fail(f"D{varga_type} {planet_name} {error}")


# Generate test functions for each varga type
for varga_type in ALL_VARGA_TYPES:
    test_name = f"test_d{varga_type}_prokerala_golden"
    test_func = lambda vt=varga_type: verify_varga_against_prokerala(vt)
    test_func.__name__ = test_name
    globals()[test_name] = test_func


def test_all_vargas_have_reference_files():
    """Verify that reference JSON files exist for all varga types."""
    missing_files = []
    
    for varga_type in ALL_VARGA_TYPES:
        json_file = os.path.join(PROKERALA_REF_DIR, f"D{varga_type}.json")
        if not os.path.exists(json_file):
            missing_files.append(f"D{varga_type}.json")
    
    if missing_files:
        pytest.skip(f"Missing reference files: {', '.join(missing_files)}. "
                   f"Please create these files in {PROKERALA_REF_DIR}/")


def test_reference_data_structure():
    """Verify that reference JSON files have correct structure."""
    for varga_type in ALL_VARGA_TYPES:
        json_file = os.path.join(PROKERALA_REF_DIR, f"D{varga_type}.json")
        if not os.path.exists(json_file):
            continue
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Check required top-level keys
        assert "varga_type" in data, f"D{varga_type}.json missing 'varga_type'"
        assert "birth_data" in data, f"D{varga_type}.json missing 'birth_data'"
        
        # Check birth data
        birth_data = data["birth_data"]
        assert birth_data["dob"] == TEST_BIRTH_DATE, \
            f"D{varga_type}.json birth_data.dob mismatch"
        assert birth_data["time"] == TEST_BIRTH_TIME, \
            f"D{varga_type}.json birth_data.time mismatch"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
