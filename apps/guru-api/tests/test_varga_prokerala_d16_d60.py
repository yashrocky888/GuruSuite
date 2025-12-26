"""
Golden Test Suite for D16-D60 Varga Charts
Compares API output against Prokerala/JHora reference data

Test Birth Data:
- DOB: 1995-05-16
- Time: 18:38 IST
- Place: Bangalore (12.9716°N, 77.5946°E)

Reference: https://www.prokerala.com/astrology/divisional-charts.php
"""

import pytest
import swisseph as swe
from datetime import datetime
from src.jyotish.varga_engine import build_varga_chart
from src.jyotish.kundli_engine import generate_kundli
from src.utils.timezone import local_to_utc
from src.utils.converters import get_sign_name

# Test birth data
TEST_DOB = datetime(1995, 5, 16, 18, 38, 0)
TEST_LAT = 12.9716
TEST_LON = 77.5946
TEST_TIMEZONE = 'Asia/Kolkata'


def get_d1_data():
    """Generate D1 kundli for test birth data"""
    birth_dt_utc = local_to_utc(TEST_DOB, TEST_TIMEZONE)
    jd = swe.julday(
        birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day,
        birth_dt_utc.hour + birth_dt_utc.minute / 60.0,
        swe.GREG_CAL
    )
    kundli = generate_kundli(jd, TEST_LAT, TEST_LON)
    d1_ascendant = kundli["Ascendant"]["degree"]
    d1_planets = {
        planet_name: planet_info["degree"]
        for planet_name, planet_info in kundli["Planets"].items()
    }
    return d1_ascendant, d1_planets


# PROKERALA REFERENCE DATA (to be populated from actual Prokerala output)
# Format: {varga: {planet: {sign: str, sign_index: int, house: int}}}
PROKERALA_REFERENCE = {
    # D16, D20, D24, D27, D30, D40, D45, D60 will be added here
    # after manual verification against Prokerala website
}


def test_varga_against_prokerala(varga_type: int, planet_name: str, expected_sign: str, expected_sign_index: int):
    """
    Test a specific planet in a varga chart against Prokerala reference.
    
    Args:
        varga_type: Varga type (16, 20, 24, 27, 30, 40, 45, 60)
        planet_name: Planet name (Sun, Moon, Mars, etc.)
        expected_sign: Expected sign name from Prokerala
        expected_sign_index: Expected sign index (0-11)
    """
    d1_ascendant, d1_planets = get_d1_data()
    
    if planet_name not in d1_planets:
        pytest.skip(f"Planet {planet_name} not in D1 data")
    
    # Build varga chart
    varga_chart = build_varga_chart(d1_planets, d1_ascendant, varga_type)
    
    # Get planet data
    planet_data = varga_chart["planets"].get(planet_name)
    if not planet_data:
        pytest.fail(f"Planet {planet_name} not found in D{varga_type} chart")
    
    actual_sign = planet_data["sign"]
    actual_sign_index = planet_data["sign_index"]
    
    # Verify sign
    assert actual_sign == expected_sign, \
        f"D{varga_type} {planet_name}: Expected {expected_sign} (index {expected_sign_index}), got {actual_sign} (index {actual_sign_index})"
    
    assert actual_sign_index == expected_sign_index, \
        f"D{varga_type} {planet_name}: Expected sign_index {expected_sign_index}, got {actual_sign_index}"


def test_d16_ascendant_prokerala():
    """Test D16 ascendant against Prokerala"""
    d1_ascendant, d1_planets = get_d1_data()
    varga_chart = build_varga_chart(d1_planets, d1_ascendant, 16)
    
    # TODO: Add Prokerala reference data
    # expected_sign = "Leo"  # Example
    # expected_sign_index = 4  # Example
    # 
    # actual_sign = varga_chart["ascendant"]["sign"]
    # actual_sign_index = varga_chart["ascendant"]["sign_index"]
    # 
    # assert actual_sign == expected_sign
    # assert actual_sign_index == expected_sign_index
    
    # For now, just verify structure
    assert "ascendant" in varga_chart
    assert "sign" in varga_chart["ascendant"]
    assert "sign_index" in varga_chart["ascendant"]
    assert varga_chart["ascendant"]["house"] == 1


if __name__ == "__main__":
    # Print current D16-D60 outputs for manual comparison
    d1_ascendant, d1_planets = get_d1_data()
    
    print("=" * 60)
    print("D16-D60 VARGA CHART OUTPUTS (for Prokerala comparison)")
    print("=" * 60)
    print(f"D1 Ascendant: {get_sign_name(int(d1_ascendant / 30))} ({d1_ascendant:.4f}°)")
    print()
    
    for varga_type in [16, 20, 24, 27, 30, 40, 45, 60]:
        varga_chart = build_varga_chart(d1_planets, d1_ascendant, varga_type)
        asc = varga_chart["ascendant"]
        print(f"D{varga_type} Ascendant: {asc['sign']} (index {asc['sign_index']}, house {asc['house']})")
        
        # Print first few planets
        planets = varga_chart["planets"]
        for planet_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            if planet_name in planets:
                p = planets[planet_name]
                print(f"  {planet_name}: {p['sign']} (index {p['sign_index']}, house {p['house']})")
        print()

