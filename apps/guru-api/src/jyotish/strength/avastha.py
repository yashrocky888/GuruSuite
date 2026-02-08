"""
Planetary Avastha (state) calculation for transit interpretation.

Used as tone modifier only — never overrides Shadbala, retrograde, or Dasha authority.
Deeptadi: sign-based (exaltation, own, friendly, neutral, enemy).
Sayanadi: degree-in-sign based (Jagrat/Swapna/Sushupti).
"""

import math
from datetime import datetime
from typing import Dict, Any, Optional

# Exaltation signs (0-11)
EXALTATION_SIGNS = {
    "Sun": 0,      # Aries
    "Moon": 1,     # Taurus
    "Mars": 9,     # Capricorn
    "Mercury": 5,  # Virgo
    "Jupiter": 3,  # Cancer
    "Venus": 11,   # Pisces
    "Saturn": 6,   # Libra
}

# Debilitation signs
DEBILITATION_SIGNS = {
    "Sun": 6,      # Libra
    "Moon": 7,     # Scorpio
    "Mars": 3,     # Cancer
    "Mercury": 11, # Pisces
    "Jupiter": 9,  # Capricorn
    "Venus": 5,    # Virgo
    "Saturn": 0,   # Aries
}

# Own signs
OWN_SIGNS = {
    "Sun": [4],
    "Moon": [3],
    "Mars": [0, 7],
    "Mercury": [2, 5],
    "Jupiter": [8, 11],
    "Venus": [1, 6],
    "Saturn": [9, 10],
}

# Sign lords for friendship
SIGN_LORDS = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun",
    5: "Mercury", 6: "Venus", 7: "Mars", 8: "Jupiter", 9: "Saturn",
    10: "Saturn", 11: "Jupiter",
}

NATURAL_FRIENDS = {
    "Sun": ["Moon", "Mars", "Jupiter"],
    "Moon": ["Sun", "Mercury"],
    "Mars": ["Sun", "Moon", "Jupiter"],
    "Mercury": ["Sun", "Venus"],
    "Jupiter": ["Sun", "Moon", "Mars"],
    "Venus": ["Mercury", "Saturn"],
    "Saturn": ["Mercury", "Venus"],
}

NATURAL_ENEMIES = {
    "Sun": ["Venus", "Saturn"],
    "Moon": [],
    "Mars": ["Mercury"],
    "Mercury": ["Mars"],
    "Jupiter": ["Venus", "Mercury"],
    "Venus": ["Sun", "Moon"],
    "Saturn": ["Sun", "Moon"],
}


def get_transit_dignity(planet: str, sign_index: int) -> str:
    """
    Strict Jyotisha sign-dignity for a transit planet.
    Returns: exalted | debilitated | own_sign | friendly | enemy | neutral.
    Used by prediction context so dignity text reflects backend authority only.
    """
    if planet not in EXALTATION_SIGNS:
        return "neutral"
    if sign_index == EXALTATION_SIGNS.get(planet):
        return "exalted"
    if sign_index == DEBILITATION_SIGNS.get(planet):
        return "debilitated"
    if sign_index in OWN_SIGNS.get(planet, []):
        return "own_sign"
    sign_lord = SIGN_LORDS.get(sign_index, "")
    if sign_lord in NATURAL_FRIENDS.get(planet, []):
        return "friendly"
    if sign_lord in NATURAL_ENEMIES.get(planet, []):
        return "enemy"
    return "neutral"


def _deeptadi(planet: str, sign_index: int) -> Optional[str]:
    """
    Deeptadi avastha from sign placement.
    Returns: Deepta, Svakshetra, Mudita, Shanta, or Lajjita.
    """
    if planet not in EXALTATION_SIGNS:
        return None
    if sign_index == EXALTATION_SIGNS.get(planet):
        return "Deepta"
    if sign_index in OWN_SIGNS.get(planet, []):
        return "Svakshetra"
    if sign_index == DEBILITATION_SIGNS.get(planet):
        return "Lajjita"
    sign_lord = SIGN_LORDS.get(sign_index, "")
    if sign_lord in NATURAL_FRIENDS.get(planet, []):
        return "Mudita"
    if sign_lord in NATURAL_ENEMIES.get(planet, []):
        return "Lajjita"
    return "Shanta"


def _sayanadi(degree_in_sign: float, sign_index: int) -> Optional[str]:
    """
    Sayanadi avastha from degree in sign (drekkana).
    Odd signs: 0-10° Jagrat, 10-20° Swapna, 20-30° Sushupti.
    Even signs: reversed (20-30° Jagrat, 10-20° Swapna, 0-10° Sushupti).
    LOCK: Clamp deg to prevent 30.0 falling into next band.
    """
    deg = min(max(degree_in_sign % 30.0, 0.0), 29.999999)
    is_odd = (sign_index % 2) == 0
    if is_odd:
        if deg < 10:
            return "Jagrat"
        if deg < 20:
            return "Swapna"
        return "Sushupti"
    else:
        if deg < 10:
            return "Sushupti"
        if deg < 20:
            return "Swapna"
        return "Jagrat"


# LOCK: One canonical modifier per avastha type. Never contradict dignity. One per planet.
# Deepta/Svakshetra/Mudita → Strength amplified.; Lajjita → Expression restrained.;
# Jagrat → Results manifest externally.; Swapna → Results fluctuate.; Sushupti → Results internalized.
_AVASTHA_MODIFIER = {
    "strong": "Strength amplified.",
    "lajjita": "Expression restrained.",
    "jagrat": "Results manifest externally.",
    "swapna": "Results fluctuate.",
    "sushupti": "Results internalized.",
}


def get_transit_avastha(
    planet: str,
    longitude: float,
    calculation_date: Optional[datetime] = None,
) -> Optional[Dict[str, Any]]:
    """
    Compute avastha for a transit planet.
    Returns dict with deeptadi, sayanadi, and modifier_suggestion.
    LOCK: One modifier per planet. Deeptadi takes precedence; else Sayanadi.
    Never contradict dignity. Modifier text is canonical only.
    """
    if planet not in EXALTATION_SIGNS:
        return None
    lon = float(longitude)
    if lon >= 360.0:
        lon = lon % 360.0
    lon = lon % 360.0
    if lon < 0:
        lon += 360.0
    sign_index = int(math.floor(lon / 30.0)) % 12
    degree_in_sign = lon % 30.0

    deeptadi = _deeptadi(planet, sign_index)
    sayanadi = _sayanadi(degree_in_sign, sign_index)

    modifier = None
    if deeptadi in ("Deepta", "Mudita", "Svakshetra"):
        modifier = _AVASTHA_MODIFIER.get("strong")
    elif deeptadi == "Lajjita":
        modifier = _AVASTHA_MODIFIER.get("lajjita")
    elif sayanadi == "Jagrat":
        modifier = _AVASTHA_MODIFIER.get("jagrat")
    elif sayanadi == "Swapna":
        modifier = _AVASTHA_MODIFIER.get("swapna")
    elif sayanadi == "Sushupti":
        modifier = _AVASTHA_MODIFIER.get("sushupti")

    return {
        "deeptadi": deeptadi,
        "sayanadi": sayanadi,
        "modifier_suggestion": modifier,
    }
