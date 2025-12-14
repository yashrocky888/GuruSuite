"""
Test varga calculations against absolute reference data.

This test file uses EXPECTED_VARGAS as the ABSOLUTE TRUTH.
All varga calculations must match these values exactly.
"""

import pytest
from datetime import datetime
from src.utils.timezone import local_to_utc
import swisseph as swe
from src.jyotish.kundli_engine import generate_kundli
from src.jyotish.varga_drik import calculate_varga

# Test birth data: 16/05/1995, 18:38, Bangalore
TEST_DOB = "1995-05-16"
TEST_TIME = "18:38"
TEST_LAT = 12.9716
TEST_LON = 77.5946
TEST_TIMEZONE = "Asia/Kolkata"

# ABSOLUTE TRUTH - Expected varga signs (1-12 format, where 1=Aries, 12=Pisces)
EXPECTED_VARGAS = {
    "D7": {
        "Asc": 2,   # Taurus
        "Sun": 7,   # Scorpio
        "Moon": 6,  # Libra
        "Mercury": 12,  # Aries (12th sign = 0-indexed 11, but we use 1-12)
        "Venus": 2,  # Taurus
        "Mars": 4,   # Leo
        "Jupiter": 5,  # Virgo
        "Saturn": 4,  # Leo
        "Rahu": 9,   # Capricorn
        "Ketu": 3,   # Cancer
    },
    "D10": {
        "Asc": 4,   # Cancer (Karka)
        "Sun": 8,   # Scorpio (Vrischika)
        "Moon": 9,  # Sagittarius (Dhanu)
        "Mercury": 12,  # Pisces (Meena)
        "Venus": 11,  # Aquarius (Kumbha)
        "Mars": 12,  # Pisces (Meena)
        "Jupiter": 8,  # Scorpio (Vrischika)
        "Saturn": 8,  # Scorpio (Vrischika)
        "Rahu": 8,   # Scorpio (Vrischika)
        "Ketu": 4,   # Cancer (Karka)
    },
    "D12": {
        "Asc": None,  # Not explicitly in reference
        "Sun": 7,   # Cancer (7 in 1-12 = Cancer, 0-indexed = 6)
        "Moon": 9,  # Virgo
        "Mercury": 1,  # Capricorn
        "Venus": 6,  # Gemini
        "Mars": 8,   # Leo
        "Jupiter": 6,  # Gemini
        "Saturn": 1,  # Capricorn
        "Rahu": 2,   # Aquarius
        "Ketu": 8,   # Leo
    }
}

# Convert 1-12 to 0-11 for internal use
def sign_12_to_0(sign_12: int) -> int:
    """Convert sign 1-12 to 0-11"""
    return (sign_12 - 1) % 12

def sign_0_to_12(sign_0: int) -> int:
    """Convert sign 0-11 to 1-12"""
    return sign_0 + 1

@pytest.fixture
def test_kundli():
    """Generate kundli for test birth data"""
    birth_date = datetime.strptime(TEST_DOB, "%Y-%m-%d").date()
    time_parts = TEST_TIME.split(':')
    hour = int(time_parts[0])
    minute = int(time_parts[1])
    birth_dt_local = datetime.combine(birth_date, datetime.min.time().replace(hour=hour, minute=minute))
    birth_dt_utc = local_to_utc(birth_dt_local, TEST_TIMEZONE)
    jd = swe.julday(birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day,
                    birth_dt_utc.hour + birth_dt_utc.minute / 60.0 + birth_dt_utc.second / 3600.0, swe.GREG_CAL)
    return generate_kundli(jd, TEST_LAT, TEST_LON)

def test_d7_saptamsa(test_kundli):
    """Test D7 (Saptamsa) calculations"""
    expected = EXPECTED_VARGAS["D7"]
    
    # Test Ascendant
    asc_d1 = test_kundli["Ascendant"]["degree"]
    asc_d7 = calculate_varga(asc_d1, 7)
    asc_d7_sign_12 = sign_0_to_12(asc_d7["sign"])
    assert asc_d7_sign_12 == expected["Asc"], f"Ascendant D7: got {asc_d7_sign_12}, expected {expected['Asc']}"
    
    # Test planets
    planet_map = {
        "Sun": "Sun",
        "Moon": "Moon",
        "Mercury": "Mercury",
        "Venus": "Venus",
        "Mars": "Mars",
        "Jupiter": "Jupiter",
        "Saturn": "Saturn",
        "Rahu": "Rahu",
        "Ketu": "Ketu"
    }
    
    for planet_name, planet_key in planet_map.items():
        if planet_key in expected:
            d1_deg = test_kundli["Planets"][planet_name]["degree"]
            d7_data = calculate_varga(d1_deg, 7)
            d7_sign_12 = sign_0_to_12(d7_data["sign"])
            assert d7_sign_12 == expected[planet_key], \
                f"{planet_name} D7: got {d7_sign_12}, expected {expected[planet_key]}"

def test_d10_dasamsa(test_kundli):
    """Test D10 (Dasamsa) calculations"""
    expected = EXPECTED_VARGAS["D10"]
    
    # Test Ascendant
    asc_d1 = test_kundli["Ascendant"]["degree"]
    asc_d10 = calculate_varga(asc_d1, 10)
    asc_d10_sign_12 = sign_0_to_12(asc_d10["sign"])
    assert asc_d10_sign_12 == expected["Asc"], f"Ascendant D10: got {asc_d10_sign_12}, expected {expected['Asc']}"
    
    # Test planets
    planet_map = {
        "Sun": "Sun",
        "Moon": "Moon",
        "Mercury": "Mercury",
        "Venus": "Venus",
        "Mars": "Mars",
        "Jupiter": "Jupiter",
        "Saturn": "Saturn",
        "Rahu": "Rahu",
        "Ketu": "Ketu"
    }
    
    for planet_name, planet_key in planet_map.items():
        if planet_key in expected and expected[planet_key] is not None:
            d1_deg = test_kundli["Planets"][planet_name]["degree"]
            d10_data = calculate_varga(d1_deg, 10)
            d10_sign_12 = sign_0_to_12(d10_data["sign"])
            assert d10_sign_12 == expected[planet_key], \
                f"{planet_name} D10: got {d10_sign_12}, expected {expected[planet_key]}"

def test_d12_dwadasamsa(test_kundli):
    """Test D12 (Dwadasamsa) calculations"""
    expected = EXPECTED_VARGAS["D12"]
    
    # Test planets
    planet_map = {
        "Sun": "Sun",
        "Moon": "Moon",
        "Mercury": "Mercury",
        "Venus": "Venus",
        "Mars": "Mars",
        "Jupiter": "Jupiter",
        "Saturn": "Saturn",
        "Rahu": "Rahu",
        "Ketu": "Ketu"
    }
    
    for planet_name, planet_key in planet_map.items():
        if planet_key in expected and expected[planet_key] is not None:
            d1_deg = test_kundli["Planets"][planet_name]["degree"]
            d12_data = calculate_varga(d1_deg, 12)
            d12_sign_12 = sign_0_to_12(d12_data["sign"])
            assert d12_sign_12 == expected[planet_key], \
                f"{planet_name} D12: got {d12_sign_12}, expected {expected[planet_key]}"

