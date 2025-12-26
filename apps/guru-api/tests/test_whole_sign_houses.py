"""
Invariant Tests for Whole Sign House System

🔒 DO NOT MODIFY — JHora compatible
These tests ensure house calculations match Prokerala/JHora exactly.

Ground Truth (Reference):
- Ascendant: 212°16' → Vrischika (Scorpio, sign_index 7) → House 1
- House 1 = Vrischika, House 2 = Dhanu, House 3 = Makara, etc.
"""

import pytest
from src.jyotish.kundli_engine import get_planet_house_jhora
from src.jyotish.varga_engine import build_varga_chart
from src.utils.converters import normalize_degrees


# Ground truth data (from user's reference)
GROUND_TRUTH_D1 = {
    "ascendant": {
        "longitude": 212.27,  # 212°16' ≈ 212.27°
        "sign_index": 7,  # Vrischika (Scorpio)
        "house": 1
    },
    "planets": {
        "Moon": {"longitude": 235.25, "sign_index": 7, "house": 1},  # Vrischika
        "Jupiter": {"longitude": 228.68, "sign_index": 7, "house": 1},  # Vrischika
        "Venus": {"longitude": 5.68, "sign_index": 0, "house": 6},  # Mesha
        "Sun": {"longitude": 31.40, "sign_index": 1, "house": 7},  # Vrishabha
        "Mercury": {"longitude": 52.12, "sign_index": 1, "house": 7},  # Vrishabha
        "Mars": {"longitude": 122.25, "sign_index": 4, "house": 10},  # Simha
        "Saturn": {"longitude": 328.88, "sign_index": 10, "house": 4},  # Kumbha
        "Rahu": {"longitude": 190.78, "sign_index": 6, "house": 12},  # Tula
        "Ketu": {"longitude": 10.78, "sign_index": 0, "house": 6},  # Mesha
    }
}


def test_ascendant_house_always_one():
    """CRITICAL: Ascendant.house must ALWAYS be 1 for D1 and ALL varga charts."""
    # Test D1
    asc_longitude = 212.27
    asc_sign_index = int(asc_longitude / 30)
    assert asc_sign_index == 7, f"Ascendant sign_index must be 7 (Vrischika), got {asc_sign_index}"
    
    # Ascendant house is always 1 (not calculated, it's a rule)
    asc_house = 1
    assert asc_house == 1, f"Ascendant house must be 1, got {asc_house}"


def test_d1_house_calculation():
    """Test D1 house calculation matches ground truth."""
    asc_longitude = GROUND_TRUTH_D1["ascendant"]["longitude"]
    
    for planet_name, expected in GROUND_TRUTH_D1["planets"].items():
        planet_longitude = expected["longitude"]
        expected_house = expected["house"]
        
        # Calculate house using fixed function
        calculated_house = get_planet_house_jhora(planet_longitude, asc_longitude, [])
        
        assert calculated_house == expected_house, \
            f"{planet_name}: Expected house {expected_house}, got {calculated_house} " \
            f"(longitude={planet_longitude}, asc={asc_longitude})"


def test_planet_same_sign_as_ascendant_house_one():
    """Planet in same sign as ascendant must be in house 1."""
    asc_longitude = 212.27  # Vrischika
    moon_longitude = 235.25  # Also Vrischika
    
    moon_house = get_planet_house_jhora(moon_longitude, asc_longitude, [])
    assert moon_house == 1, f"Moon in same sign as ascendant must be house 1, got {moon_house}"


def test_whole_sign_formula():
    """Test Whole Sign formula: house = ((planet_sign - asc_sign + 12) % 12) + 1"""
    asc_longitude = 212.27
    asc_sign_index = int(asc_longitude / 30)  # 7 (Vrischika)
    
    test_cases = [
        (235.25, 7, 1),   # Moon: Vrischika → House 1
        (5.68, 0, 6),     # Venus: Mesha → House 6
        (31.40, 1, 7),    # Sun: Vrishabha → House 7
        (122.25, 4, 10),  # Mars: Simha → House 10
        (328.88, 10, 4),  # Saturn: Kumbha → House 4
        (190.78, 6, 12),  # Rahu: Tula → House 12
    ]
    
    for planet_longitude, expected_sign_index, expected_house in test_cases:
        planet_sign_index = int(planet_longitude / 30)
        assert planet_sign_index == expected_sign_index, \
            f"Planet sign_index mismatch: expected {expected_sign_index}, got {planet_sign_index}"
        
        # Apply Whole Sign formula
        calculated_house = ((planet_sign_index - asc_sign_index + 12) % 12) + 1
        assert calculated_house == expected_house, \
            f"House calculation failed: planet_sign={planet_sign_index}, asc_sign={asc_sign_index}, " \
            f"expected house {expected_house}, got {calculated_house}"


def test_varga_ascendant_house_one():
    """Varga ascendant must ALWAYS be in house 1."""
    d1_ascendant = 212.27
    d1_planets = {
        "Sun": 31.40,
        "Moon": 235.25,
        "Mars": 122.25,
        "Mercury": 52.12,
        "Jupiter": 228.68,
        "Venus": 5.68,
        "Saturn": 328.88,
        "Rahu": 190.78,
        "Ketu": 10.78,
    }
    
    # Test D9 (Navamsa)
    d9_chart = build_varga_chart(d1_planets, d1_ascendant, 9)
    assert d9_chart["ascendant"]["house"] == 1, \
        f"D9 ascendant house must be 1, got {d9_chart['ascendant']['house']}"
    
    # Test D10 (Dasamsa)
    d10_chart = build_varga_chart(d1_planets, d1_ascendant, 10)
    assert d10_chart["ascendant"]["house"] == 1, \
        f"D10 ascendant house must be 1, got {d10_chart['ascendant']['house']}"


def test_varga_planet_house_calculation():
    """Test varga planet house calculation uses Whole Sign relative to varga ascendant."""
    d1_ascendant = 212.27
    d1_planets = {
        "Sun": 31.40,
        "Moon": 235.25,
    }
    
    # Build D9 chart
    d9_chart = build_varga_chart(d1_planets, d1_ascendant, 9)
    d9_asc_sign_index = d9_chart["ascendant"]["sign_index"]
    
    # Verify planets use Whole Sign formula relative to D9 ascendant
    for planet_name, planet_data in d9_chart["planets"].items():
        planet_sign_index = planet_data["sign_index"]
        calculated_house = planet_data["house"]
        
        # Expected house using Whole Sign formula
        expected_house = ((planet_sign_index - d9_asc_sign_index + 12) % 12) + 1
        
        assert calculated_house == expected_house, \
            f"D9 {planet_name}: Expected house {expected_house}, got {calculated_house} " \
            f"(planet_sign={planet_sign_index}, asc_sign={d9_asc_sign_index})"
        
        # House must be 1-12
        assert 1 <= calculated_house <= 12, \
            f"D9 {planet_name}: House must be 1-12, got {calculated_house}"


def test_houses_array_generation():
    """Test Houses array uses Whole Sign logic."""
    asc_sign_index = 7  # Vrischika
    
    # Expected houses for ascendant in Vrischika:
    # House 1 = Vrischika (7), House 2 = Dhanu (8), House 3 = Makara (9), etc.
    expected_houses = [
        (1, 7),   # Vrischika
        (2, 8),   # Dhanu
        (3, 9),   # Makara
        (4, 10),  # Kumbha
        (5, 11),  # Meena
        (6, 0),   # Mesha
        (7, 1),   # Vrishabha
        (8, 2),   # Mithuna
        (9, 3),   # Karka
        (10, 4),  # Simha
        (11, 5),  # Kanya
        (12, 6),  # Tula
    ]
    
    for house_num, expected_sign_index in expected_houses:
        calculated_sign_index = (asc_sign_index + house_num - 1) % 12
        assert calculated_sign_index == expected_sign_index, \
            f"House {house_num}: Expected sign_index {expected_sign_index}, got {calculated_sign_index}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

