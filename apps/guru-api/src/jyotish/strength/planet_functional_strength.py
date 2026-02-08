"""
Planet Functional Strength Engine - Ancient Jyotish Logic

Phase 1 + Phase 2 (Extension):
- Phase 1: Core functional strength (SIGN DIGNITY, HOUSE TYPE, ASSOCIATION, FUNCTIONAL STRENGTH, CAN_DELIVER)
- Phase 2: Debilitated Friend Awareness + Neecha Bhanga Awareness (support flags ONLY)

This module determines whether a planet is capable of delivering results
based strictly on classical rules used by ancient gurus.

This is NOT prediction. This is a foundational eligibility layer used by:
- Dasha gating
- Transit triggering
- Divisional chart permission
- AI interpretation filtering

Architecture:
- Backend ONLY (Guru API)
- NO frontend calculations
- NO UI logic
- NO modification to existing D1–D60 calculations
- NO Shadbala numeric computation

Input: D1 chart data (already calculated)
Output: Structured flags for each planet
"""

from typing import Dict, List, Optional, Any

from src.jyotish.kundli_engine import SIGN_LORDS


# Sign indices (0-11): Aries=0, Taurus=1, Gemini=2, Cancer=3, Leo=4, Virgo=5,
#                       Libra=6, Scorpio=7, Sagittarius=8, Capricorn=9, Aquarius=10, Pisces=11

# Sanskrit sign names for reference
SIGNS_SANSKRIT = [
    "Mesha",      # 0 - Aries
    "Vrishabha",  # 1 - Taurus
    "Mithuna",    # 2 - Gemini
    "Karka",      # 3 - Cancer
    "Simha",      # 4 - Leo
    "Kanya",      # 5 - Virgo
    "Tula",       # 6 - Libra
    "Vrishchika", # 7 - Scorpio
    "Dhanu",      # 8 - Sagittarius
    "Makara",     # 9 - Capricorn
    "Kumbha",     # 10 - Aquarius
    "Meena"       # 11 - Pisces
]

# English sign names for reference
SIGNS_ENGLISH = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]


# ═══════════════════════════════════════════════════════════════════════════
# 1️⃣ SIGN DIGNITY (STATIC TABLES — NO MATH)
# ═══════════════════════════════════════════════════════════════════════════

# Exaltation signs (Uccha)
EXALTATION_SIGNS = {
    "Sun": 0,      # Mesha (Aries)
    "Moon": 1,     # Vrishabha (Taurus)
    "Mars": 9,     # Makara (Capricorn)
    "Mercury": 5,  # Kanya (Virgo)
    "Jupiter": 3,  # Karka (Cancer)
    "Venus": 11,   # Meena (Pisces)
    "Saturn": 6,   # Tula (Libra)
    # Node dignity kept as implemented in Phase 1
    "Rahu": 4,     # Simha (Leo)
    "Ketu": 10,    # Kumbha (Aquarius)
}

# Debilitation signs (Neecha)
DEBILITATION_SIGNS = {
    "Sun": 6,      # Tula (Libra)
    "Moon": 7,     # Vrishchika (Scorpio)
    "Mars": 3,     # Karka (Cancer)
    "Mercury": 11, # Meena (Pisces)
    "Jupiter": 9,  # Makara (Capricorn)
    "Venus": 5,    # Kanya (Virgo)
    "Saturn": 0,   # Mesha (Aries)
    # Node dignity kept as implemented in Phase 1
    "Rahu": 10,    # Kumbha (Aquarius)
    "Ketu": 4,     # Simha (Leo)
}

# Own signs (Swa Rashi) - planets can have multiple own signs
OWN_SIGNS = {
    "Sun": [4],           # Simha (Leo)
    "Moon": [3],          # Karka (Cancer)
    "Mars": [0, 7],       # Mesha (Aries), Vrishchika (Scorpio)
    "Mercury": [2, 5],    # Mithuna (Gemini), Kanya (Virgo)
    "Jupiter": [8, 11],   # Dhanu (Sagittarius), Meena (Pisces)
    "Venus": [1, 6],      # Vrishabha (Taurus), Tula (Libra)
    "Saturn": [9, 10],    # Makara (Capricorn), Kumbha (Aquarius)
    "Rahu": [],           # Rahu has no own sign (shadow planet)
    "Ketu": [],           # Ketu has no own sign (shadow planet)
}


# ═══════════════════════════════════════════════════════════════════════════
# 2️⃣ HOUSE TYPE (ANCIENT CLASSIFICATION)
# ═══════════════════════════════════════════════════════════════════════════

def get_house_type(house: int) -> str:
    """
    Classify house type according to ancient Jyotish rules.
    
    Args:
        house: House number (1-12)
    
    Returns:
        House type: "kendra", "trikona", "dusthana", or "neutral"
    """
    if house in [1, 4, 7, 10]:
        return "kendra"
    elif house in [5, 9]:
        return "trikona"
    elif house in [6, 8, 12]:
        return "dusthana"
    else:
        return "neutral"


# ═══════════════════════════════════════════════════════════════════════════
# 3️⃣ ASSOCIATION (CONJUNCTIONS - PHASE-1 ONLY)
# ═══════════════════════════════════════════════════════════════════════════

# Benefic planets (natural)
# Note: Mercury is benefic when unafflicted, Moon is benefic when waxing
# Phase-1: Simplified - treat Mercury and Moon as benefic always
# Future phases can add affliction/waxing logic
BENEFIC_PLANETS = {"Jupiter", "Venus", "Mercury", "Moon"}

# Malefic planets (natural)
# Note: Sun is contextual (can be benefic in some contexts)
# Phase-1: Simplified - treat Sun as malefic for association detection
MALEFIC_PLANETS = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}


def detect_associations(planet_name: str, planet_house: int, all_planets: Dict[str, Any]) -> List[str]:
    """
    Detect conjunctions (planets in same house).
    
    Phase-1: Only conjunctions, NO aspect logic.
    
    Args:
        planet_name: Name of the planet being analyzed
        planet_house: House number of the planet
        all_planets: Dictionary of all planets with their house positions
    
    Returns:
        List of association types: ["with_benefic", "with_malefic"]
        Empty list if no conjunctions
    """
    associations: List[str] = []
    
    # Check all other planets for same house
    for other_planet_name, other_planet_data in all_planets.items():
        if other_planet_name == planet_name:
            continue
        
        other_house = other_planet_data.get("house")
        if other_house is None:
            continue
        
        # Same house = conjunction
        if other_house == planet_house:
            if other_planet_name in BENEFIC_PLANETS:
                associations.append("with_benefic")
            elif other_planet_name in MALEFIC_PLANETS:
                associations.append("with_malefic")
    
    # Remove duplicates and return
    return list(set(associations))


# ═══════════════════════════════════════════════════════════════════════════
# 4️⃣ FUNCTIONAL STRENGTH (QUALITATIVE - ANCIENT RULES)
# ═══════════════════════════════════════════════════════════════════════════

def calculate_functional_strength(
    planet_name: str,
    sign_index: int,
    house_type: str,
    is_exalted: bool,
    is_debilitated: bool,
    is_own_sign: bool
) -> str:
    """
    Calculate functional strength based on ancient rule-based logic.
    
    Ancient rules:
    - Debilitated + Dusthana → very_weak
    - Exalted OR Own Sign → strong
    - Kendra / Trikona → moderate
    - Else → weak
    
    Args:
        planet_name: Planet name
        sign_index: Sign index (0-11)
        house_type: House type ("kendra", "trikona", "dusthana", "neutral")
        is_exalted: Whether planet is exalted
        is_debilitated: Whether planet is debilitated
        is_own_sign: Whether planet is in own sign
    
    Returns:
        Functional strength: "very_weak", "weak", "moderate", or "strong"
    """
    # Rule 1: Debilitated + Dusthana → very_weak
    if is_debilitated and house_type == "dusthana":
        return "very_weak"
    
    # Rule 2: Exalted OR Own Sign → strong
    if is_exalted or is_own_sign:
        return "strong"
    
    # Rule 3: Kendra / Trikona → moderate
    if house_type in ["kendra", "trikona"]:
        return "moderate"
    
    # Rule 4: Else → weak
    return "weak"


# ═══════════════════════════════════════════════════════════════════════════
# 5️⃣ CAN DELIVER (SPEAK / SILENCE GATE)
# ═══════════════════════════════════════════════════════════════════════════

def can_planet_deliver(
    is_debilitated: bool,
    house_type: str,
    is_combust: bool
) -> bool:
    """
    Determine if planet can deliver results (speak/silence gate).
    
    Ancient wisdom encoded:
    If:
    - debilitated
    - AND dusthana
    - AND combust
    → can_deliver = false
    
    Else:
    → can_deliver = true
    
    Args:
        is_debilitated: Whether planet is debilitated
        house_type: House type
        is_combust: Whether planet is combust
    
    Returns:
        True if planet can deliver, False otherwise
    """
    # Ancient rule: Triple affliction = silence
    if is_debilitated and house_type == "dusthana" and is_combust:
        return False
    
    return True


# ═══════════════════════════════════════════════════════════════════════════
# 6️⃣ NATURAL FRIENDSHIP TABLES (NAISARGIKA MAITRI)
# ═══════════════════════════════════════════════════════════════════════════

NATURAL_FRIENDS: Dict[str, set] = {
    "Sun": {"Moon", "Mars", "Jupiter"},
    "Moon": {"Sun", "Mercury"},
    "Mars": {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus": {"Mercury", "Saturn"},
    "Saturn": {"Mercury", "Venus"},
    "Rahu": {"Venus", "Saturn"},
    "Ketu": {"Mars", "Jupiter"},
}

NATURAL_ENEMIES: Dict[str, set] = {
    "Sun": {"Venus", "Saturn"},
    "Moon": set(),
    "Mars": {"Mercury"},
    "Mercury": {"Moon"},
    "Jupiter": {"Venus", "Mercury"},
    "Venus": {"Sun", "Moon"},
    "Saturn": {"Sun", "Moon", "Mars"},
    "Rahu": {"Sun", "Moon", "Mars"},
    "Ketu": {"Sun", "Moon"},
}


# ═══════════════════════════════════════════════════════════════════════════
# 7️⃣ FUNCTIONAL NATURE (BPHS/JHORA - HOUSE LORDSHIP ONLY)
# ═══════════════════════════════════════════════════════════════════════════

def calculate_functional_nature(planet_name: str, ascendant_sign_index: int) -> str:
    """
    Functional Nature calculation (BPHS / JHora / Prokerala compliant)
    STANDARD MODE (2026 accuracy) - JHora Standard Mode Lock.
    
    Includes Rahu (Aquarius) and Ketu (Scorpio) co-lordship logic.
    
    CRITICAL RULE:
    Functional Nature depends ONLY on house lordship from Lagna.
    Placement, dignity, conjunctions, retrograde, aspects, strength are IGNORED.
    
    CORE LOGIC: Mooltrikona House is PRIMARY DECIDER
    - When a planet owns two houses, the house containing its Mooltrikona sign
      ALONE decides functional nature.
    - No mixed rules, no Gemini heuristics, no over-engineering.
    """
    
    # Mooltrikona signs (sign indices where planet has strongest ownership)
    MOOLTRIKONA_SIGNS = {
        "Sun": 4,      # Leo
        "Moon": 1,     # Taurus
        "Mars": 0,     # Aries
        "Mercury": 5,  # Virgo
        "Jupiter": 8,  # Sagittarius
        "Venus": 6,    # Libra
        "Saturn": 10,  # Aquarius
        # Nodes have no Mooltrikona (shadow planets)
    }
    
    # Natural nature classification
    NATURAL_BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
    NATURAL_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}
    
    # House categories (BPHS)
    TRIKONAS = {1, 5, 9}          # Always auspicious
    KENDRAS = {1, 4, 7, 10}       # Power houses
    TRISHADAYA = {3, 6, 11}       # Functional malefic houses
    
    owned_houses = []
    
    # Identify houses owned by the planet
    for house_num in range(1, 13):
        house_sign_index = (ascendant_sign_index + house_num - 1) % 12
        
        # Standard sign lords (Sun–Saturn)
        sign_lord = SIGN_LORDS.get(house_sign_index)
        if sign_lord == planet_name:
            owned_houses.append(house_num)
        
        # Rahu co-lords Aquarius (11th sign, index 10)
        if planet_name == "Rahu" and house_sign_index == 10:
            owned_houses.append(house_num)
        
        # Ketu co-lords Scorpio (8th sign, index 7)
        if planet_name == "Ketu" and house_sign_index == 7:
            owned_houses.append(house_num)
    
    owned_set = set(owned_houses)
    
    # Safety: No ownership
    if not owned_set:
        return "neutral"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 1️⃣ LAGNA LORD (ABSOLUTE)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # If planet owns House 1 → return "benefic"
    # No exceptions. Overrides everything.
    if 1 in owned_set:
        return "benefic"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 2️⃣ FIND MOOLTRIKONA HOUSE (PRIMARY DECIDER)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Use MOOLTRIKONA_SIGNS.
    # If planet owns two houses, the house containing its Mooltrikona sign
    # ALONE decides functional nature.
    mooltrikona_sign_index = MOOLTRIKONA_SIGNS.get(planet_name)
    mooltrikona_house = None
    
    if mooltrikona_sign_index is not None:
        # Find which house contains the Mooltrikona sign
        for house_num in range(1, 13):
            house_sign_index = (ascendant_sign_index + house_num - 1) % 12
            if house_sign_index == mooltrikona_sign_index and house_num in owned_set:
                mooltrikona_house = house_num
                break
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 3️⃣ MOOLTRIKONA → FUNCTIONAL NATURE MAP
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # If Mooltrikona house is:
    # - 1, 5, 9 → "benefic"
    # - 3, 6, 11 → "malefic"
    # - 2, 7, 12 → "neutral"
    # - 8 → "malefic"
    #   EXCEPTION: Sun or Moon owning ONLY 8 → "neutral"
    if mooltrikona_house is not None:
        if mooltrikona_house in {1, 5, 9}:
            return "benefic"
        elif mooltrikona_house in {3, 6, 11}:
            return "malefic"
        elif mooltrikona_house in {2, 7, 12}:
            return "neutral"
        elif mooltrikona_house == 8:
            # EXCEPTION: Sun or Moon owning ONLY 8 → "neutral"
            if planet_name in {"Sun", "Moon"} and owned_set == {8}:
                return "neutral"
            return "malefic"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 4️⃣ YOGAKARAKA (SECONDARY CHECK)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # If planet owns BOTH:
    # - any Kendra (1,4,7,10)
    # - AND any Trikona (5,9)
    # → return "benefic"
    owns_kendra = bool(owned_set & KENDRAS)
    owns_trikona = bool(owned_set & TRIKONAS)
    if owns_kendra and owns_trikona:
        return "benefic"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 5️⃣ KENDRADHIPATI DOSHA (STRICT)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Apply ONLY if:
    # - Planet is a NATURAL BENEFIC (Jupiter, Venus, Mercury, Moon)
    # - Planet owns ONLY Kendras (subset of {4,7,10})
    # - Planet owns MORE THAN ONE Kendra
    # → return "malefic"
    # Natural malefics owning only Kendras → "neutral"
    if owns_kendra and not owns_trikona:
        # Check if owns ONLY Kendras (4, 7, 10) and nothing else
        if owned_set <= {4, 7, 10}:
            if planet_name in NATURAL_BENEFICS:
                # Only MULTIPLE Kendras → Malefic (Kendradhipati Dosha)
                if len(owned_set) > 1:
                    return "malefic"
            elif planet_name in NATURAL_MALEFICS:
                return "neutral"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 6️⃣ TRISHADAYA DOMINANCE (ONLY IF NO MOOLTRIKONA FOUND)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # If planet owns any of {3,6,11} → "malefic"
    # Only apply if Mooltrikona was not found (nodes, or Mooltrikona not owned)
    if mooltrikona_house is None:
        owns_trishadaya = bool(owned_set & TRISHADAYA)
        if owns_trishadaya:
            return "malefic"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 7️⃣ 8TH LORD RULE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 8th lord is MALEFIC
    # EXCEPTION: Sun or Moon owning ONLY 8 → "neutral"
    if 8 in owned_set:
        if planet_name in {"Sun", "Moon"} and owned_set == {8}:
            return "neutral"
        return "malefic"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 8️⃣ MARAKA RULE (CORRECTED)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # - 2 + 7 together → "neutral" (Maraka ≠ Malefic)
    # - 2 alone → neutral (Moon may be malefic - handled by Mooltrikona)
    # - 7 alone → neutral
    if 2 in owned_set and 7 in owned_set:
        return "neutral"
    if owned_set == {2} or owned_set == {7}:
        return "neutral"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 9️⃣ DEFAULT
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    return "neutral"


# ═══════════════════════════════════════════════════════════════════════════
# 8️⃣ SIGN INDEX HELPER
# ═══════════════════════════════════════════════════════════════════════════

def get_sign_index_from_data(planet_data: Dict[str, Any]) -> Optional[int]:
    """
    Extract sign_index from planet data, handling multiple possible field formats.
    
    Args:
        planet_data: Planet data dictionary
    
    Returns:
        Sign index (0-11) or None if not found
    """
    # Try sign_index first (most common)
    sign_index = planet_data.get("sign_index")
    if sign_index is not None:
        return int(sign_index) % 12
    
    # Try sign_sanskrit (convert to index)
    sign_sanskrit = planet_data.get("sign_sanskrit")
    if sign_sanskrit:
        try:
            return SIGNS_SANSKRIT.index(sign_sanskrit)
        except ValueError:
            pass
    
    # Try sign (English name)
    sign_english = planet_data.get("sign")
    if sign_english:
        try:
            return SIGNS_ENGLISH.index(sign_english)
        except ValueError:
            pass
    
    return None


# ═══════════════════════════════════════════════════════════════════════════
# 8️⃣ SIGN DIGNITY HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def get_sign_dignity(planet_name: str, sign_index: int) -> Dict[str, Any]:
    """
    Determine sign dignity for a planet.
    
    Args:
        planet_name: Planet name
        sign_index: Sign index (0-11)
    
    Returns:
        Dictionary with dignity flags:
        {
            "dignity": "exalted" | "debilitated" | "own_sign" | "neutral",
            "exaltation": bool,
            "debilitation": bool,
            "own_sign": bool
        }
    """
    is_exalted = EXALTATION_SIGNS.get(planet_name) == sign_index
    is_debilitated = DEBILITATION_SIGNS.get(planet_name) == sign_index
    is_own_sign = sign_index in OWN_SIGNS.get(planet_name, [])
    
    # Determine dignity status
    if is_exalted:
        dignity = "exalted"
    elif is_debilitated:
        dignity = "debilitated"
    elif is_own_sign:
        dignity = "own_sign"
    else:
        dignity = "neutral"
    
    return {
        "dignity": dignity,
        "exaltation": is_exalted,
        "debilitation": is_debilitated,
        "own_sign": is_own_sign
    }


# ═══════════════════════════════════════════════════════════════════════════
# 9️⃣ MASTER FUNCTION
# ═══════════════════════════════════════════════════════════════════════════

def calculate_planet_functional_strength(d1_chart: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate planet functional strength for all planets in D1 chart.
    
    This function receives ONLY already-calculated API data.
    
    Input example:
    {
      "chart_type": "D1",
      "Ascendant": {...},
      "Planets": {
        "Sun": {
          "sign": "Makara",
          "sign_index": 9,
          "house": 6,
          "degree": 20.78,
          "retrograde": False,
          "combust": False
        },
        ...
      }
    }
    
    Output structure (CANONICAL — DO NOT CHANGE):
    {
      "planet_functional_strength": {
        "Sun": {
          "dignity": "neutral",
          "exaltation": False,
          "debilitation": False,
          "own_sign": False,
          "retrograde": False,
          "combust": False,
          "house_type": "dusthana",
          "association": ["with_malefic"],
          "functional_strength": "weak",
          "can_deliver": True,
          "debilitated_friend": null | true | false | "neutral",
          "neecha_bhanga_possible": false | true,
          "neecha_bhanga_reason": "friendly_dispositor" | null
        },
        ...
      }
    }
    
    Args:
        d1_chart: D1 chart data with Ascendant and Planets
    
    Returns:
        Dictionary with planet functional strength flags for all planets
    """
    result: Dict[str, Any] = {
        "planet_functional_strength": {}
    }
    
    # Extract planets from D1 chart
    planets = d1_chart.get("Planets", {})
    if not planets:
        return result
    
    # Extract Ascendant sign_index for functional nature calculation
    ascendant_data = d1_chart.get("Ascendant", {})
    ascendant_sign_index = get_sign_index_from_data(ascendant_data)
    if ascendant_sign_index is None:
        # Try to get from degree if sign_index not available
        ascendant_degree = ascendant_data.get("degree")
        if ascendant_degree is not None:
            ascendant_sign_index = int(ascendant_degree // 30) % 12
        else:
            # Cannot calculate functional nature without Ascendant
            ascendant_sign_index = None
    
    # Process each planet
    for planet_name, planet_data in planets.items():
        # Extract planet data
        sign_index = get_sign_index_from_data(planet_data)
        house = planet_data.get("house")
        # Handle both "retro" and "retrograde" field names for compatibility
        retrograde = planet_data.get("retrograde", planet_data.get("retro", False))
        # Combust may not be in current API response, default to False
        combust = planet_data.get("combust", False)
        
        # Validate required fields
        if sign_index is None or house is None:
            # Skip planets without required data
            continue
        
        # 1. Get sign dignity
        dignity_info = get_sign_dignity(planet_name, sign_index)
        
        # 2. Get house type
        house_type = get_house_type(house)
        
        # 3. Detect associations (conjunctions)
        associations = detect_associations(planet_name, house, planets)
        
        # 4. Calculate functional strength (PHASE-1: DO NOT MODIFY)
        functional_strength = calculate_functional_strength(
            planet_name=planet_name,
            sign_index=sign_index,
            house_type=house_type,
            is_exalted=dignity_info["exaltation"],
            is_debilitated=dignity_info["debilitation"],
            is_own_sign=dignity_info["own_sign"]
        )
        
        # 5. Determine can_deliver flag (PHASE-1: DO NOT MODIFY)
        can_deliver = can_planet_deliver(
            is_debilitated=dignity_info["debilitation"],
            house_type=house_type,
            is_combust=combust
        )
        
        # 6. Calculate Functional Nature (BPHS/JHORA - HOUSE LORDSHIP ONLY)
        functional_nature = "neutral"  # Default
        if ascendant_sign_index is not None:
            functional_nature = calculate_functional_nature(planet_name, ascendant_sign_index)
        
        # 7. Debilitated Friend & Neecha Bhanga Awareness (PHASE-2 EXTENSION)
        debilitated_friend: Optional[Any] = None  # true | false | "neutral" | None
        neecha_bhanga_possible: bool = False
        neecha_bhanga_reason: Optional[str] = None
        
        if dignity_info["debilitation"]:
            # Identify dispositor (sign lord of the debilitation sign)
            dispositor: Optional[str] = SIGN_LORDS.get(sign_index)
            
            if dispositor:
                friends = NATURAL_FRIENDS.get(planet_name, set())
                enemies = NATURAL_ENEMIES.get(planet_name, set())
                
                is_friend = dispositor in friends
                is_enemy = dispositor in enemies
                
                # Special node rules (Parashara + Prokerala standard):
                # Rahu: Debilitated Enemy (Mars is enemy) - already covered via NATURAL_ENEMIES
                # Ketu: Debilitated Friend (Venus is friend) - add explicit awareness
                if planet_name == "Ketu" and dispositor == "Venus":
                    is_friend = True
                    is_enemy = False
                
                if is_friend:
                    debilitated_friend = True
                    neecha_bhanga_possible = True
                    neecha_bhanga_reason = "friendly_dispositor"
                elif is_enemy:
                    debilitated_friend = False
                else:
                    debilitated_friend = "neutral"
            else:
                # No dispositor info → treat as neutral awareness
                debilitated_friend = "neutral"
        
        # Build result for this planet
        result["planet_functional_strength"][planet_name] = {
            "dignity": dignity_info["dignity"],
            "exaltation": dignity_info["exaltation"],
            "debilitation": dignity_info["debilitation"],
            "own_sign": dignity_info["own_sign"],
            "retrograde": retrograde,
            "combust": combust,
            "house_type": house_type,
            "association": associations,
            "functional_nature": functional_nature,                # BPHS/JHORA - HOUSE LORDSHIP ONLY
            "functional_strength": functional_strength,          # PHASE-1 (unchanged)
            "can_deliver": can_deliver,                          # PHASE-1 (unchanged)
            # PHASE-2 EXTENSION (NON-BREAKING)
            # If NOT debilitated → debilitated_friend=None, neecha_bhanga_possible=False, neecha_bhanga_reason=None
            "debilitated_friend": debilitated_friend,
            "neecha_bhanga_possible": neecha_bhanga_possible,
            "neecha_bhanga_reason": neecha_bhanga_reason,
        }
    
    return result
