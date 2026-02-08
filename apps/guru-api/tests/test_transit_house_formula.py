"""
Unit tests for transit house calculation (FINAL PRECISION LOCK).

Formula: house_number = ((transit_sign_index - lagna_sign_index) % 12) + 1
No degree-based calculation. No frontend override.
"""

import pytest
from src.jyotish.ai.guru_payload import _house_from_lagna_sign


def test_scorpio_lagna_aquarius_transit():
    """Scorpio Lagna (7), Aquarius (10) → house 4."""
    assert _house_from_lagna_sign(10, 7) == 4


def test_aries_lagna_aries_transit():
    """Aries Lagna (0), Aries transit (0) → house 1."""
    assert _house_from_lagna_sign(0, 0) == 1


def test_pisces_lagna_aries_transit():
    """Pisces Lagna (11), Aries transit (0) → house 2."""
    assert _house_from_lagna_sign(0, 11) == 2


def test_all_twelve_houses_aries_lagna():
    """Aries Lagna (0): each sign maps to house (sign_index + 1)."""
    for sign in range(12):
        assert _house_from_lagna_sign(sign, 0) == sign + 1


def test_all_twelve_houses_scorpio_lagna():
    """Scorpio Lagna (7): Aquarius=4, Pisces=5, Aries=6, ..., Libra=12, Scorpio=1."""
    assert _house_from_lagna_sign(7, 7) == 1   # Scorpio in 1st
    assert _house_from_lagna_sign(8, 7) == 2   # Sagittarius in 2nd
    assert _house_from_lagna_sign(9, 7) == 3   # Capricorn in 3rd
    assert _house_from_lagna_sign(10, 7) == 4  # Aquarius in 4th
    assert _house_from_lagna_sign(0, 7) == 6   # Aries in 6th
    assert _house_from_lagna_sign(6, 7) == 12  # Libra in 12th
