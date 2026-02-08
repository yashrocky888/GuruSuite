"""
Transit sign edge lock. Uses floor. Guard longitude normalization.
"""

import pytest
from src.utils.converters import longitude_to_sign_index, degrees_to_sign


def test_29999_sign_0():
    """29.999° → sign 0."""
    assert longitude_to_sign_index(29.999) == 0


def test_30000_sign_1():
    """30.000° → sign 1."""
    assert longitude_to_sign_index(30.000) == 1


def test_359999_sign_11():
    """359.999° → sign 11."""
    assert longitude_to_sign_index(359.999) == 11


def test_360000_sign_0():
    """360.000° → sign 0 (normalized)."""
    assert longitude_to_sign_index(360.000) == 0


def test_degrees_to_sign_boundaries():
    """degrees_to_sign uses same floor logic."""
    assert degrees_to_sign(29.999)[0] == 0
    assert degrees_to_sign(30.000)[0] == 1
    assert degrees_to_sign(359.999)[0] == 11
    assert degrees_to_sign(360.000)[0] == 0
