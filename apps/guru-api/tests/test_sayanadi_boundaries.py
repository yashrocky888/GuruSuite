"""
Sayanadi degree edge lock. Jagrat/Swapna/Sushupti mapping for odd and even signs.
"""

import pytest
from src.jyotish.strength.avastha import get_transit_avastha


def _sayanadi_for_deg(deg: float, sign_index: int) -> str:
    """Helper: get sayanadi from avastha result."""
    r = get_transit_avastha("Mars", deg + sign_index * 30.0)
    return (r or {}).get("sayanadi") or ""


def test_0_deg_odd_sign():
    """0.000° in odd sign → Jagrat."""
    r = get_transit_avastha("Mars", 0.001)  # Aries 0°, odd
    assert r and r.get("sayanadi") == "Jagrat"


def test_999_deg_odd_sign():
    """9.999° in odd sign → Jagrat."""
    r = get_transit_avastha("Mars", 9.999)
    assert r and r.get("sayanadi") == "Jagrat"


def test_10_deg_odd_sign():
    """10.000° in odd sign → Swapna."""
    r = get_transit_avastha("Mars", 10.0)
    assert r and r.get("sayanadi") == "Swapna"


def test_19999_deg_odd_sign():
    """19.999° in odd sign → Swapna."""
    r = get_transit_avastha("Mars", 19.999)
    assert r and r.get("sayanadi") == "Swapna"


def test_20_deg_odd_sign():
    """20.000° in odd sign → Sushupti."""
    r = get_transit_avastha("Mars", 20.0)
    assert r and r.get("sayanadi") == "Sushupti"


def test_29999_deg_odd_sign():
    """29.999° in odd sign → Sushupti."""
    r = get_transit_avastha("Mars", 29.999)
    assert r and r.get("sayanadi") == "Sushupti"


def test_even_sign_reversed():
    """Even sign (Taurus=1): 0-10 Sushupti, 10-20 Swapna, 20-30 Jagrat."""
    r = get_transit_avastha("Mars", 31.0)   # Taurus 1°
    assert r and r.get("sayanadi") == "Sushupti"
    r = get_transit_avastha("Mars", 41.0)   # Taurus 11°
    assert r and r.get("sayanadi") == "Swapna"
    r = get_transit_avastha("Mars", 51.0)   # Taurus 21°
    assert r and r.get("sayanadi") == "Jagrat"
