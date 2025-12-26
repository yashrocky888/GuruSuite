"""
Golden Test Suite for D16-D60 Varga Charts
Compares output against Prokerala/JHora reference data.

Test Birth Data: 1995-05-16, 18:38 IST, Bangalore (Lahiri)
D1 Ascendant: Vrishchika (Scorpio) - 212.2799°
D1 Moon: Vrishchika (Scorpio) - 235.2501°
D1 Rahu: Tula (Libra) - 190.7944°

REFERENCE DATA (Prokerala/JHora - TO BE FILLED):
Once Prokerala/JHora outputs are verified, update this file with exact values.
"""

import pytest
import sys
import os

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

import swisseph as swe
from datetime import datetime
from utils.timezone import local_to_utc
from jyotish.kundli_engine import generate_kundli
from jyotish.varga_engine import build_varga_chart


# Test birth data
TEST_BIRTH_DATE = datetime(1995, 5, 16, 18, 38, 0)
TEST_TIMEZONE = 'Asia/Kolkata'
TEST_LAT = 12.9716
TEST_LON = 77.5946

# Prokerala/JHora Reference Data (TO BE UPDATED WITH ACTUAL VALUES)
# Format: {varga: {'Ascendant': {'sign': str, 'sign_index': int}, 'Moon': {...}, 'Rahu': {...}}}
PROKERALA_REFERENCE = {
    16: {
        'Ascendant': {'sign': None, 'sign_index': None},  # TO BE FILLED
        'Moon': {'sign': None, 'sign_index': None},
        'Rahu': {'sign': None, 'sign_index': None},
    },
    20: {
        'Ascendant': {'sign': None, 'sign_index': None},
        'Moon': {'sign': None, 'sign_index': None},
        'Rahu': {'sign': None, 'sign_index': None},
    },
    24: {
        'Ascendant': {'sign': None, 'sign_index': None},
        'Moon': {'sign': None, 'sign_index': None},
        'Rahu': {'sign': None, 'sign_index': None},
    },
    27: {
        'Ascendant': {'sign': None, 'sign_index': None},
        'Moon': {'sign': None, 'sign_index': None},
        'Rahu': {'sign': None, 'sign_index': None},
    },
    30: {
        'Ascendant': {'sign': None, 'sign_index': None},
        'Moon': {'sign': None, 'sign_index': None},
        'Rahu': {'sign': None, 'sign_index': None},
    },
    40: {
        'Ascendant': {'sign': None, 'sign_index': None},
        'Moon': {'sign': None, 'sign_index': None},
        'Rahu': {'sign': None, 'sign_index': None},
    },
    45: {
        'Ascendant': {'sign': None, 'sign_index': None},
        'Moon': {'sign': None, 'sign_index': None},
        'Rahu': {'sign': None, 'sign_index': None},
    },
    60: {
        'Ascendant': {'sign': None, 'sign_index': None},
        'Moon': {'sign': None, 'sign_index': None},
        'Rahu': {'sign': None, 'sign_index': None},
    },
}


def get_test_kundli_data():
    """Generate D1 kundli data for test."""
    birth_dt_utc = local_to_utc(TEST_BIRTH_DATE, TEST_TIMEZONE)
    jd = swe.julday(birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day,
                    birth_dt_utc.hour + birth_dt_utc.minute/60.0, swe.GREG_CAL)
    
    d1 = generate_kundli(jd, TEST_LAT, TEST_LON)
    d1_asc = d1['Ascendant']['degree']
    d1_planets = {p: d1['Planets'][p]['degree'] for p in 
                  ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']}
    
    return d1_planets, d1_asc


@pytest.mark.parametrize("varga", [16, 20, 24, 27, 30, 40, 45, 60])
def test_varga_ascendant_matches_prokerala(varga):
    """Test that varga ascendant matches Prokerala/JHora exactly."""
    d1_planets, d1_asc = get_test_kundli_data()
    chart = build_varga_chart(d1_planets, d1_asc, varga)
    
    actual_sign = chart['ascendant']['sign']
    actual_sign_index = chart['ascendant']['sign_index']
    
    expected = PROKERALA_REFERENCE[varga]['Ascendant']
    
    # Skip if reference data not filled
    if expected['sign'] is None:
        pytest.skip(f"Prokerala reference data not available for D{varga}")
    
    assert actual_sign == expected['sign'], \
        f"D{varga} Ascendant sign mismatch: expected {expected['sign']}, got {actual_sign}"
    assert actual_sign_index == expected['sign_index'], \
        f"D{varga} Ascendant sign_index mismatch: expected {expected['sign_index']}, got {actual_sign_index}"


@pytest.mark.parametrize("varga", [16, 20, 24, 27, 30, 40, 45, 60])
def test_varga_moon_matches_prokerala(varga):
    """Test that Moon in varga chart matches Prokerala/JHora exactly."""
    d1_planets, d1_asc = get_test_kundli_data()
    chart = build_varga_chart(d1_planets, d1_asc, varga)
    
    actual_sign = chart['planets']['Moon']['sign']
    actual_sign_index = chart['planets']['Moon']['sign_index']
    
    expected = PROKERALA_REFERENCE[varga]['Moon']
    
    # Skip if reference data not filled
    if expected['sign'] is None:
        pytest.skip(f"Prokerala reference data not available for D{varga}")
    
    assert actual_sign == expected['sign'], \
        f"D{varga} Moon sign mismatch: expected {expected['sign']}, got {actual_sign}"
    assert actual_sign_index == expected['sign_index'], \
        f"D{varga} Moon sign_index mismatch: expected {expected['sign_index']}, got {actual_sign_index}"


@pytest.mark.parametrize("varga", [16, 20, 24, 27, 30, 40, 45, 60])
def test_varga_rahu_matches_prokerala(varga):
    """Test that Rahu in varga chart matches Prokerala/JHora exactly."""
    d1_planets, d1_asc = get_test_kundli_data()
    chart = build_varga_chart(d1_planets, d1_asc, varga)
    
    actual_sign = chart['planets']['Rahu']['sign']
    actual_sign_index = chart['planets']['Rahu']['sign_index']
    
    expected = PROKERALA_REFERENCE[varga]['Rahu']
    
    # Skip if reference data not filled
    if expected['sign'] is None:
        pytest.skip(f"Prokerala reference data not available for D{varga}")
    
    assert actual_sign == expected['sign'], \
        f"D{varga} Rahu sign mismatch: expected {expected['sign']}, got {actual_sign}"
    assert actual_sign_index == expected['sign_index'], \
        f"D{varga} Rahu sign_index mismatch: expected {expected['sign_index']}, got {actual_sign_index}"

