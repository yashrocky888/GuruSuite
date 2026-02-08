"""
Moon movement house consistency lock.
Uses exact same formula: ((transit_sign_index - lagna_sign_index) % 12) + 1
"""

import pytest
from src.jyotish.ai.guru_payload import _house_from_lagna_sign
from src.utils.converters import longitude_to_sign_index


def test_moon_house_formula_matches():
    """Moon from_house and to_house use sign-based formula only."""
    for lagna_sign in range(12):
        for moon_sign in range(12):
            expected = _house_from_lagna_sign(moon_sign, lagna_sign)
            assert 1 <= expected <= 12
            assert expected == ((moon_sign - lagna_sign) % 12) + 1


def test_no_degree_based_house():
    """House formula is sign-only; no degree division."""
    assert _house_from_lagna_sign(10, 7) == 4
    assert _house_from_lagna_sign(0, 0) == 1
    assert _house_from_lagna_sign(0, 11) == 2


def test_longitude_to_sign_consistent():
    """longitude_to_sign_index used for moon matches house formula input."""
    for lon in [0.0, 29.999, 30.0, 180.0, 359.999]:
        si = longitude_to_sign_index(lon)
        assert 0 <= si <= 11
        house = _house_from_lagna_sign(si, 0)
        assert 1 <= house <= 12
