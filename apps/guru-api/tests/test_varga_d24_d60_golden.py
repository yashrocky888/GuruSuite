"""
🔒 GOLDEN TESTS — VARGA D24-D60 PROKERALA VERIFICATION

This file contains GOLDEN TESTS that verify D24-D60 varga calculations
match Prokerala output exactly.

⚠️ DO NOT MODIFY THESE TESTS WITHOUT UPDATING PROKERALA REFERENCE DATA
⚠️ These tests are the AUTHORITATIVE verification of varga correctness
⚠️ Any failures indicate a regression in varga math

Reference Data:
- Birth: 1995-05-16, 18:38 IST, Bangalore
- Ayanamsa: Lahiri
- Source: Prokerala screenshots (manually extracted)
- File: PROKERALA_VERIFICATION_COMPARISON.md

Test Structure:
- Each varga (D24, D27, D30, D40, D45, D60) has a test
- Each test verifies ALL 10 planets + Ascendant
- Sign indices are compared (0-11)
- Exact match required (no tolerance)
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from jyotish.varga_drik import calculate_varga_sign
from jyotish.kundli_engine import generate_kundli
from datetime import datetime
import pytz


# 🔒 GOLDEN REFERENCE DATA — PROKERALA VERIFIED
# Birth: 1995-05-16, 18:38 IST, Bangalore
# Ayanamsa: Lahiri
# Source: PROKERALA_VERIFICATION_COMPARISON.md

PROKERALA_REFERENCE = {
    "D24": {
        "Ascendant": 4,  # Leo
        "Sun": 4,  # Leo
        "Moon": 0,  # Aries
        "Mars": 5,  # Virgo
        "Mercury": 8,  # Sagittarius
        "Jupiter": 5,  # Virgo
        "Venus": 8,  # Sagittarius
        "Saturn": 2,  # Gemini
        "Rahu": 11,  # Pisces
        "Ketu": 11,  # Pisces
    },
    "D27": {
        "Ascendant": 11,  # Pisces
        "Sun": 4,  # Leo
        "Moon": 7,  # Scorpio
        "Mars": 2,  # Gemini
        "Mercury": 10,  # Aquarius
        "Jupiter": 1,  # Taurus
        "Venus": 5,  # Virgo
        "Saturn": 8,  # Sagittarius
        "Rahu": 3,  # Cancer
        "Ketu": 9,  # Capricorn
    },
    "D30": {
        "Ascendant": 1,  # Taurus
        "Sun": 1,  # Taurus
        "Moon": 7,  # Scorpio
        "Mars": 0,  # Aries
        "Mercury": 9,  # Capricorn
        "Jupiter": 11,  # Pisces
        "Venus": 10,  # Aquarius
        "Saturn": 6,  # Libra
        "Rahu": 8,  # Sagittarius
        "Ketu": 8,  # Sagittarius
    },
    "D40": {
        "Ascendant": 9,  # Capricorn
        "Sun": 8,  # Sagittarius
        "Moon": 0,  # Aries
        "Mars": 9,  # Capricorn
        "Mercury": 11,  # Pisces
        "Jupiter": 6,  # Libra
        "Venus": 8,  # Sagittarius
        "Saturn": 2,  # Gemini
        "Rahu": 1,  # Taurus
        "Ketu": 1,  # Taurus
    },
    "D45": {
        "Ascendant": 7,  # Scorpio
        "Sun": 6,  # Libra
        "Moon": 5,  # Virgo
        "Mars": 7,  # Scorpio
        "Mercury": 1,  # Taurus
        "Jupiter": 8,  # Sagittarius
        "Venus": 8,  # Sagittarius
        "Saturn": 11,  # Pisces
        "Rahu": 4,  # Leo
        "Ketu": 4,  # Leo
    },
    "D60": {
        "Ascendant": 11,  # Pisces
        "Sun": 3,  # Cancer
        "Moon": 9,  # Capricorn
        "Mars": 8,  # Sagittarius
        "Mercury": 9,  # Capricorn
        "Jupiter": 8,  # Sagittarius
        "Venus": 11,  # Pisces
        "Saturn": 7,  # Scorpio
        "Rahu": 3,  # Cancer
        "Ketu": 9,  # Capricorn
    },
}

# Test birth data
TEST_BIRTH_DATE = datetime(1995, 5, 16, 18, 38, 0)
TEST_TIMEZONE = pytz.timezone('Asia/Kolkata')
TEST_LATITUDE = 12.9716  # Bangalore
TEST_LONGITUDE = 77.5946  # Bangalore


def get_planet_longitude_from_kundli(kundli_data: dict, planet_name: str) -> float:
    """Extract planet longitude from kundli data"""
    planets = kundli_data.get("Planets", {})
    planet = planets.get(planet_name, {})
    return planet.get("longitude", 0.0)


def get_ascendant_longitude_from_kundli(kundli_data: dict) -> float:
    """Extract Ascendant longitude from kundli data"""
    ascendant = kundli_data.get("Ascendant", {})
    return ascendant.get("longitude", 0.0)


@pytest.fixture(scope="module")
def test_kundli():
    """Generate kundli for test birth data"""
    from jyotish.drik_panchang_engine import get_julian_day_utc
    
    birth_dt = TEST_TIMEZONE.localize(TEST_BIRTH_DATE)
    jd = get_julian_day_utc(birth_dt, "18:38:00", "Asia/Kolkata")
    
    kundli = generate_kundli(jd, TEST_LATITUDE, TEST_LONGITUDE)
    return kundli


def test_d24_golden(test_kundli):
    """🔒 GOLDEN TEST: D24 (Chaturvimsamsa) - Prokerala Verified"""
    varga = "D24"
    reference = PROKERALA_REFERENCE[varga]
    
    failures = []
    
    # Test Ascendant
    asc_long = get_ascendant_longitude_from_kundli(test_kundli)
    asc_sign = int(asc_long / 30.0)
    asc_deg = asc_long % 30.0
    result = calculate_varga_sign(asc_sign, asc_deg, varga)
    expected = reference["Ascendant"]
    if result != expected:
        failures.append(f"Ascendant: got {result}, expected {expected}")
    
    # Test all planets
    for planet_name, expected_sign in reference.items():
        if planet_name == "Ascendant":
            continue
        
        planet_long = get_planet_longitude_from_kundli(test_kundli, planet_name)
        planet_sign = int(planet_long / 30.0)
        planet_deg = planet_long % 30.0
        result = calculate_varga_sign(planet_sign, planet_deg, varga)
        
        if result != expected_sign:
            failures.append(f"{planet_name}: got {result}, expected {expected_sign}")
    
    assert len(failures) == 0, f"D24 failures: {', '.join(failures)}"


def test_d27_golden(test_kundli):
    """🔒 GOLDEN TEST: D27 (Saptavimsamsa) - Prokerala Verified"""
    varga = "D27"
    reference = PROKERALA_REFERENCE[varga]
    
    failures = []
    
    # Test Ascendant
    asc_long = get_ascendant_longitude_from_kundli(test_kundli)
    asc_sign = int(asc_long / 30.0)
    asc_deg = asc_long % 30.0
    result = calculate_varga_sign(asc_sign, asc_deg, varga)
    expected = reference["Ascendant"]
    if result != expected:
        failures.append(f"Ascendant: got {result}, expected {expected}")
    
    # Test all planets
    for planet_name, expected_sign in reference.items():
        if planet_name == "Ascendant":
            continue
        
        planet_long = get_planet_longitude_from_kundli(test_kundli, planet_name)
        planet_sign = int(planet_long / 30.0)
        planet_deg = planet_long % 30.0
        result = calculate_varga_sign(planet_sign, planet_deg, varga)
        
        if result != expected_sign:
            failures.append(f"{planet_name}: got {result}, expected {expected_sign}")
    
    assert len(failures) == 0, f"D27 failures: {', '.join(failures)}"


def test_d30_golden(test_kundli):
    """🔒 GOLDEN TEST: D30 (Trimsamsa) - Prokerala Verified"""
    varga = "D30"
    reference = PROKERALA_REFERENCE[varga]
    
    failures = []
    
    # Test Ascendant
    asc_long = get_ascendant_longitude_from_kundli(test_kundli)
    asc_sign = int(asc_long / 30.0)
    asc_deg = asc_long % 30.0
    result = calculate_varga_sign(asc_sign, asc_deg, varga)
    expected = reference["Ascendant"]
    if result != expected:
        failures.append(f"Ascendant: got {result}, expected {expected}")
    
    # Test all planets
    for planet_name, expected_sign in reference.items():
        if planet_name == "Ascendant":
            continue
        
        planet_long = get_planet_longitude_from_kundli(test_kundli, planet_name)
        planet_sign = int(planet_long / 30.0)
        planet_deg = planet_long % 30.0
        result = calculate_varga_sign(planet_sign, planet_deg, varga)
        
        if result != expected_sign:
            failures.append(f"{planet_name}: got {result}, expected {expected_sign}")
    
    assert len(failures) == 0, f"D30 failures: {', '.join(failures)}"


def test_d40_golden(test_kundli):
    """🔒 GOLDEN TEST: D40 (Khavedamsa) - Prokerala Verified"""
    varga = "D40"
    reference = PROKERALA_REFERENCE[varga]
    
    failures = []
    
    # Test Ascendant
    asc_long = get_ascendant_longitude_from_kundli(test_kundli)
    asc_sign = int(asc_long / 30.0)
    asc_deg = asc_long % 30.0
    result = calculate_varga_sign(asc_sign, asc_deg, varga)
    expected = reference["Ascendant"]
    if result != expected:
        failures.append(f"Ascendant: got {result}, expected {expected}")
    
    # Test all planets
    for planet_name, expected_sign in reference.items():
        if planet_name == "Ascendant":
            continue
        
        planet_long = get_planet_longitude_from_kundli(test_kundli, planet_name)
        planet_sign = int(planet_long / 30.0)
        planet_deg = planet_long % 30.0
        result = calculate_varga_sign(planet_sign, planet_deg, varga)
        
        if result != expected_sign:
            failures.append(f"{planet_name}: got {result}, expected {expected_sign}")
    
    assert len(failures) == 0, f"D40 failures: {', '.join(failures)}"


def test_d45_golden(test_kundli):
    """🔒 GOLDEN TEST: D45 (Akshavedamsa) - Prokerala Verified"""
    varga = "D45"
    reference = PROKERALA_REFERENCE[varga]
    
    failures = []
    
    # Test Ascendant
    asc_long = get_ascendant_longitude_from_kundli(test_kundli)
    asc_sign = int(asc_long / 30.0)
    asc_deg = asc_long % 30.0
    result = calculate_varga_sign(asc_sign, asc_deg, varga)
    expected = reference["Ascendant"]
    if result != expected:
        failures.append(f"Ascendant: got {result}, expected {expected}")
    
    # Test all planets
    for planet_name, expected_sign in reference.items():
        if planet_name == "Ascendant":
            continue
        
        planet_long = get_planet_longitude_from_kundli(test_kundli, planet_name)
        planet_sign = int(planet_long / 30.0)
        planet_deg = planet_long % 30.0
        result = calculate_varga_sign(planet_sign, planet_deg, varga)
        
        if result != expected_sign:
            failures.append(f"{planet_name}: got {result}, expected {expected_sign}")
    
    assert len(failures) == 0, f"D45 failures: {', '.join(failures)}"


def test_d60_golden(test_kundli):
    """🔒 GOLDEN TEST: D60 (Shashtiamsha) - Prokerala Verified"""
    varga = "D60"
    reference = PROKERALA_REFERENCE[varga]
    
    failures = []
    
    # Test Ascendant
    asc_long = get_ascendant_longitude_from_kundli(test_kundli)
    asc_sign = int(asc_long / 30.0)
    asc_deg = asc_long % 30.0
    result = calculate_varga_sign(asc_sign, asc_deg, varga)
    expected = reference["Ascendant"]
    if result != expected:
        failures.append(f"Ascendant: got {result}, expected {expected}")
    
    # Test all planets
    for planet_name, expected_sign in reference.items():
        if planet_name == "Ascendant":
            continue
        
        planet_long = get_planet_longitude_from_kundli(test_kundli, planet_name)
        planet_sign = int(planet_long / 30.0)
        planet_deg = planet_long % 30.0
        result = calculate_varga_sign(planet_sign, planet_deg, varga)
        
        if result != expected_sign:
            failures.append(f"{planet_name}: got {result}, expected {expected_sign}")
    
    assert len(failures) == 0, f"D60 failures: {', '.join(failures)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

