"""
Dignity-avastha consistency lock.
Debilitated + Strength amplified -> no strong modifier allowed.
"""

import pytest
from src.jyotish.strength.avastha import get_transit_dignity, get_transit_avastha


def test_mars_in_cancer_debilitated_no_strong_modifier():
    """Mars in Cancer (sign 3) -> dignity=debilitated -> no Strength amplified."""
    dignity = get_transit_dignity("Mars", 3)
    assert dignity == "debilitated"
    avastha = get_transit_avastha("Mars", 95.0)
    assert avastha
    mod = avastha.get("modifier_suggestion")
    assert mod != "Strength amplified."
    assert mod == "Expression restrained."


def test_debilitated_never_gets_strength_amplified():
    """Any debilitated planet: modifier cannot be Strength amplified."""
    debilitated_cases = [
        ("Sun", 6, 186.0),
        ("Moon", 7, 216.0),
        ("Jupiter", 9, 276.0),
        ("Venus", 5, 156.0),
        ("Saturn", 0, 5.0),
    ]
    for planet, sign_idx, lon in debilitated_cases:
        d = get_transit_dignity(planet, sign_idx)
        assert d == "debilitated"
        a = get_transit_avastha(planet, lon)
        if a and a.get("modifier_suggestion"):
            assert a["modifier_suggestion"] != "Strength amplified."
