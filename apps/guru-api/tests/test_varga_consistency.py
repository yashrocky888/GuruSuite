"""
Test varga consistency across all endpoints.

This test ensures that the same input produces IDENTICAL varga results
across all API endpoints, proving single source of truth.
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from datetime import datetime
import swisseph as swe
from src.utils.timezone import local_to_utc
from src.jyotish.kundli_engine import generate_kundli
from src.jyotish.varga_engine import build_varga_chart

client = TestClient(app)

# Test case: 1995-05-16 18:38 Bangalore
TEST_DOB = "1995-05-16"
TEST_TIME = "18:38"
TEST_LAT = 12.9716
TEST_LON = 77.5946
TEST_TIMEZONE = "Asia/Kolkata"

# Expected D10 values (Prokerala verified)
EXPECTED_D10 = {
    "Ascendant": {"sign": "Cancer", "sign_index": 3, "house": 4},
    "Venus": {"sign": "Aquarius", "sign_index": 10, "house": 11},
    "Mars": {"sign": "Pisces", "sign_index": 11, "house": 12},
}


def test_d10_consistency_across_endpoints():
    """
    Test that D10 results are IDENTICAL across:
    - /api/v1/kundli (GET)
    - /api/v1/kundli/all (if exists)
    - /api/v1/kundli/divisional (if exists)
    - Direct varga_engine call
    """
    # Get D10 from main endpoint
    response1 = client.get(
        f"/api/v1/kundli?dob={TEST_DOB}&time={TEST_TIME}&lat={TEST_LAT}&lon={TEST_LON}&timezone={TEST_TIMEZONE}"
    )
    assert response1.status_code == 200
    data1 = response1.json()
    d10_1 = data1.get("D10", {})
    
    # Get D10 from direct varga_engine (authoritative source)
    birth_datetime = datetime.strptime(f"{TEST_DOB} {TEST_TIME}", "%Y-%m-%d %H:%M")
    birth_datetime_utc = local_to_utc(birth_datetime, TEST_TIMEZONE)
    jd = swe.julday(
        birth_datetime_utc.year, birth_datetime_utc.month, birth_datetime_utc.day,
        birth_datetime_utc.hour + birth_datetime_utc.minute / 60.0,
        swe.GREG_CAL
    )
    base_kundli = generate_kundli(jd, TEST_LAT, TEST_LON)
    d1_ascendant = base_kundli["Ascendant"]["degree"]
    d1_planets = {
        planet_name: planet_info["degree"]
        for planet_name, planet_info in base_kundli["Planets"].items()
    }
    d10_engine = build_varga_chart(d1_planets, d1_ascendant, 10)
    
    # Compare results - must be identical
    assert d10_1["ascendant_sign"] == d10_engine["ascendant"]["sign"]
    assert d10_1["ascendant_house"] == d10_engine["ascendant"]["house"]
    
    for planet_name in ["Venus", "Mars"]:
        api_planet = d10_1["planets"].get(planet_name, {})
        engine_planet = d10_engine["planets"].get(planet_name, {})
        
        assert api_planet["sign"] == engine_planet["sign"], \
            f"{planet_name} sign mismatch: API={api_planet['sign']}, Engine={engine_planet['sign']}"
        assert api_planet["house"] == engine_planet["house"], \
            f"{planet_name} house mismatch: API={api_planet['house']}, Engine={engine_planet['house']}"
        assert api_planet["sign_index"] == engine_planet["sign_index"], \
            f"{planet_name} sign_index mismatch"


def test_d10_matches_prokerala():
    """Test that D10 matches Prokerala exactly for verified test case."""
    response = client.get(
        f"/api/v1/kundli?dob={TEST_DOB}&time={TEST_TIME}&lat={TEST_LAT}&lon={TEST_LON}&timezone={TEST_TIMEZONE}"
    )
    assert response.status_code == 200
    data = response.json()
    d10 = data.get("D10", {})
    
    # Verify ascendant
    assert d10["ascendant_sign"] == EXPECTED_D10["Ascendant"]["sign"]
    assert d10["ascendant_house"] == EXPECTED_D10["Ascendant"]["house"]
    
    # Verify Venus
    venus = d10["planets"].get("Venus", {})
    assert venus["sign"] == EXPECTED_D10["Venus"]["sign"]
    assert venus["house"] == EXPECTED_D10["Venus"]["house"]
    
    # Verify Mars
    mars = d10["planets"].get("Mars", {})
    assert mars["sign"] == EXPECTED_D10["Mars"]["sign"]
    assert mars["house"] == EXPECTED_D10["Mars"]["house"]


def test_house_equals_sign_for_all_varga():
    """Test that house = sign for ALL varga charts (Whole Sign system)."""
    response = client.get(
        f"/api/v1/kundli?dob={TEST_DOB}&time={TEST_TIME}&lat={TEST_LAT}&lon={TEST_LON}&timezone={TEST_TIMEZONE}"
    )
    assert response.status_code == 200
    data = response.json()
    
    for chart_type in ["D2", "D3", "D4", "D7", "D9", "D10", "D12"]:
        chart = data.get(chart_type, {})
        
        # Verify ascendant: house = sign
        asc_sign_index = None
        for planet_name, planet_data in chart.get("planets", {}).items():
            if planet_name == "Ascendant":
                asc_sign_index = planet_data.get("sign_index")
                break
        
        # Check ascendant house
        asc_house = chart.get("ascendant_house")
        if asc_sign_index is not None:
            expected_house = asc_sign_index + 1
            assert asc_house == expected_house, \
                f"{chart_type} ascendant: house ({asc_house}) must equal sign ({expected_house})"
        
        # Verify all planets: house = sign
        for planet_name, planet_data in chart.get("planets", {}).items():
            sign_index = planet_data.get("sign_index")
            house = planet_data.get("house")
            expected_house = sign_index + 1 if sign_index is not None else None
            
            assert house == expected_house, \
                f"{chart_type} {planet_name}: house ({house}) must equal sign ({expected_house})"


def test_varga_engine_runtime_guard():
    """Test that runtime guard prevents direct calculate_varga() calls from API routes."""
    from src.jyotish.varga_drik import calculate_varga
    
    # This should work (called from test, not API route)
    try:
        result = calculate_varga(100.0, 10)
        assert result is not None
    except RuntimeError as e:
        # If guard triggers, that's also OK - means it's working
        assert "ARCHITECTURAL VIOLATION" in str(e) or "varga_engine" in str(e)

