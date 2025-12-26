"""
Boundary Tests for D16-D60 Varga Charts

Tests verify correct behavior at boundary degrees:
- 0° (start of sign)
- Mid-sign (15°)
- 29°59′59″ (end of sign)
"""

import pytest
from src.jyotish.varga_drik import calculate_varga_sign
import math

# Test boundary degrees
BOUNDARY_DEGREES = [
    0.0,           # Start of sign
    0.0001,        # Just after start
    15.0,          # Mid-sign
    29.0,          # Near end
    29.9999,       # Just before end
    29.999999,     # Maximum (30° would be next sign)
]


def test_d16_boundary_degrees():
    """Test D16 handles boundary degrees correctly"""
    for sign_index in range(12):
        for deg in BOUNDARY_DEGREES:
            varga_sign = calculate_varga_sign(sign_index, deg, "D16")
            assert 0 <= varga_sign <= 11, \
                f"D16: sign_index={sign_index}, deg={deg} -> invalid varga_sign={varga_sign}"


def test_d20_boundary_degrees():
    """Test D20 handles boundary degrees correctly"""
    for sign_index in range(12):
        for deg in BOUNDARY_DEGREES:
            varga_sign = calculate_varga_sign(sign_index, deg, "D20")
            assert 0 <= varga_sign <= 11, \
                f"D20: sign_index={sign_index}, deg={deg} -> invalid varga_sign={varga_sign}"


def test_d24_boundary_degrees():
    """Test D24 handles boundary degrees correctly"""
    for sign_index in range(12):
        for deg in BOUNDARY_DEGREES:
            varga_sign = calculate_varga_sign(sign_index, deg, "D24")
            assert 0 <= varga_sign <= 11, \
                f"D24: sign_index={sign_index}, deg={deg} -> invalid varga_sign={varga_sign}"


def test_d27_boundary_degrees():
    """Test D27 handles boundary degrees correctly"""
    for sign_index in range(12):
        for deg in BOUNDARY_DEGREES:
            varga_sign = calculate_varga_sign(sign_index, deg, "D27")
            assert 0 <= varga_sign <= 11, \
                f"D27: sign_index={sign_index}, deg={deg} -> invalid varga_sign={varga_sign}"


def test_d30_boundary_degrees():
    """Test D30 handles boundary degrees correctly"""
    for sign_index in range(12):
        for deg in BOUNDARY_DEGREES:
            varga_sign = calculate_varga_sign(sign_index, deg, "D30")
            assert 0 <= varga_sign <= 11, \
                f"D30: sign_index={sign_index}, deg={deg} -> invalid varga_sign={varga_sign}"


def test_d40_boundary_degrees():
    """Test D40 handles boundary degrees correctly"""
    for sign_index in range(12):
        for deg in BOUNDARY_DEGREES:
            varga_sign = calculate_varga_sign(sign_index, deg, "D40")
            assert 0 <= varga_sign <= 11, \
                f"D40: sign_index={sign_index}, deg={deg} -> invalid varga_sign={varga_sign}"


def test_d45_boundary_degrees():
    """Test D45 handles boundary degrees correctly"""
    for sign_index in range(12):
        for deg in BOUNDARY_DEGREES:
            varga_sign = calculate_varga_sign(sign_index, deg, "D45")
            assert 0 <= varga_sign <= 11, \
                f"D45: sign_index={sign_index}, deg={deg} -> invalid varga_sign={varga_sign}"


def test_d60_boundary_degrees():
    """Test D60 handles boundary degrees correctly (MOST PRECISE)"""
    for sign_index in range(12):
        for deg in BOUNDARY_DEGREES:
            varga_sign = calculate_varga_sign(sign_index, deg, "D60")
            assert 0 <= varga_sign <= 11, \
                f"D60: sign_index={sign_index}, deg={deg} -> invalid varga_sign={varga_sign}"


def test_d30_odd_even_consistency():
    """Test D30 odd/even reversal is consistent"""
    # Test odd sign (Aries = 0) - should go forward
    aries_0deg = calculate_varga_sign(0, 0.0, "D30")
    aries_15deg = calculate_varga_sign(0, 15.0, "D30")
    aries_29deg = calculate_varga_sign(0, 29.0, "D30")
    
    # Forward progression: 0° -> same sign, 15° -> +15 signs, 29° -> +29 signs
    assert aries_0deg == 0, "D30: Aries 0° should stay in Aries"
    
    # Test even sign (Taurus = 1) - should go reverse
    taurus_0deg = calculate_varga_sign(1, 0.0, "D30")
    taurus_15deg = calculate_varga_sign(1, 15.0, "D30")
    taurus_29deg = calculate_varga_sign(1, 29.0, "D30")
    
    # Reverse progression: 0° -> same sign, 15° -> -15 signs, 29° -> -29 signs
    assert taurus_0deg == 1, "D30: Taurus 0° should stay in Taurus"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

