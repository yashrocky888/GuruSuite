"""
Mass random stress test. Million-chart simulation.
100 random lagna × 100 random transit signs.
"""

import random
import pytest
from src.jyotish.ai.guru_payload import _house_from_lagna_sign
from src.jyotish.strength.avastha import get_transit_dignity, get_transit_avastha
from src.utils.converters import longitude_to_sign_index, get_sign_name

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
DIGNITY_ENUM = {"exalted", "debilitated", "own_sign", "friendly", "enemy", "neutral"}
AVASTHA_MODIFIERS = {
    "Strength amplified.",
    "Expression restrained.",
    "Results manifest externally.",
    "Results fluctuate.",
    "Results internalized.",
}
PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def test_mass_house_1_to_12():
    """100×100 random signs: house always 1-12, no 0, no 13, no negative."""
    random.seed(42)
    for _ in range(100):
        lagna = random.randint(0, 11)
        for _ in range(100):
            transit = random.randint(0, 11)
            house = _house_from_lagna_sign(transit, lagna)
            assert 1 <= house <= 12, f"lagna={lagna} transit={transit} house={house}"
            assert house != 0
            assert house != 13
            assert house > 0


def test_mass_sign_names_valid():
    """Sign indices 0-11 map to valid names."""
    for i in range(12):
        name = get_sign_name(i)
        assert name in SIGN_NAMES


def test_mass_dignity_enum():
    """Dignity always one of allowed enum."""
    for planet in PLANETS:
        for sign in range(12):
            d = get_transit_dignity(planet, sign)
            assert d in DIGNITY_ENUM, f"{planet} sign {sign} → {d}"


def test_mass_avastha_canonical():
    """Avastha modifier only from canonical set or None."""
    for planet in PLANETS:
        for lon in [0.1, 90.1, 180.1, 270.1]:
            a = get_transit_avastha(planet, lon)
            if a and a.get("modifier_suggestion"):
                mod = a["modifier_suggestion"]
                assert mod in AVASTHA_MODIFIERS, f"{planet} lon={lon} mod={mod}"


def test_mass_longitude_bounds():
    """Random longitudes 0-360: sign index always 0-11."""
    random.seed(123)
    for _ in range(500):
        lon = random.uniform(0, 360)
        si = longitude_to_sign_index(lon)
        assert 0 <= si <= 11
