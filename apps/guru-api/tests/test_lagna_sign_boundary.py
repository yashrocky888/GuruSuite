"""
Lagna sign edge lock. Uses floor. Never round.
"""

import pytest
from src.utils.converters import longitude_to_sign_index


def test_29999_aries():
    """29.999° → Aries (0)."""
    assert longitude_to_sign_index(29.999) == 0


def test_30000_taurus():
    """30.000° → Taurus (1)."""
    assert longitude_to_sign_index(30.000) == 1


def test_359999_pisces():
    """359.999° → Pisces (11)."""
    assert longitude_to_sign_index(359.999) == 11


def test_0_aries():
    """0.000° → Aries (0)."""
    assert longitude_to_sign_index(0.000) == 0


def test_360_normalized():
    """360.000° → Aries (0) after guard."""
    assert longitude_to_sign_index(360.000) == 0
