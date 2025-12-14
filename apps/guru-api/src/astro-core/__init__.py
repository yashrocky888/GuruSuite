"""
Core Astrological Calculation Engine

ABSOLUTE RULES:
1. Sidereal zodiac ONLY
2. Lahiri ayanamsa ONLY
3. Swiss Ephemeris (sidereal mode)
4. Whole sign houses for varga charts
5. NO shortcuts, NO approximations

This module is the SINGLE SOURCE OF TRUTH for all astrological calculations.
"""

from .planets import calculate_planets_sidereal
from .houses import calculate_houses_sidereal
from .varga import calculate_varga_chart
from .ascendant import calculate_ascendant_sidereal

__all__ = [
    "calculate_planets_sidereal",
    "calculate_houses_sidereal",
    "calculate_varga_chart",
    "calculate_ascendant_sidereal",
]

