"""
Phase-2: Suitability math — Tara Bala & Chandra Bala.

Pure math only. Accepts numeric indices, returns deterministic dicts.
No dependency on AI, prompts, or routes.
"""

from typing import Dict


# 9 Taras (1–9) for Tara Bala
TARA_NAMES = [
    "Janma", "Sampat", "Vipat", "Kshema", "Pratyak",
    "Sadhaka", "Naidhana", "Mitra", "Atimitra",
]


def calculate_tara_bala(
    birth_nakshatra_idx: int,
    transit_nakshatra_idx: int,
) -> Dict[str, str]:
    """
    Tara Bala: transit Moon nakshatra vs birth Moon nakshatra.
    Indices 0–26 (27 nakshatras).

    Formula: ((transit - birth + 1) % 9); if 0 → 9.
    Returns tara index 1–9, quality, and travel_advice.
    """
    t = transit_nakshatra_idx % 27
    b = birth_nakshatra_idx % 27
    raw = ((t - b + 1) % 9)
    tara_num = 9 if raw == 0 else raw  # 1–9

    tara_name = TARA_NAMES[tara_num - 1]

    # Quality: Good / Neutral / Risk / Danger (standard mapping)
    if tara_num == 1:
        quality = "Neutral"
        travel_advice = "Focus on personal stability; avoid new outward ventures."
    elif tara_num in (2, 4, 6, 8, 9):
        quality = "Good"
        travel_advice = "Favorable for travel and new ventures."
    elif tara_num in (3,):
        quality = "Risk"
        travel_advice = "Caution advised for long travel."
    else:  # 5, 7
        quality = "Danger"
        travel_advice = "Avoid non-essential travel if possible."

    return {
        "tara_name": tara_name,
        "quality": quality,
        "travel_advice": travel_advice,
    }


def calculate_chandra_bala(
    birth_moon_sign_idx: int,
    transit_moon_sign_idx: int,
) -> Dict:
    """
    Chandra Bala: house position of transit Moon from natal Moon.
    Sign indices 0–11.

    Counts houses from natal Moon to transit Moon (1–12).
    Energy: High / Medium / Low. Favorable houses from Moon (e.g. 1,2,5,9,10,11).
    """
    b = birth_moon_sign_idx % 12
    t = transit_moon_sign_idx % 12
    # 1-based house from Moon: 1st = natal sign, 9th = 8 signs ahead
    house_position = ((t - b + 12) % 12) + 1  # 1–12

    # Favorable from Moon: 1,2,5,9,10,11 (strength/comfort)
    favorable_houses = {1, 2, 5, 9, 10, 11}
    is_favorable = house_position in favorable_houses

    # Energy: High in favorable; Medium in 3,4,6,7; Low in 8,12
    if house_position in favorable_houses:
        energy_level = "High"
    elif house_position in (3, 4, 6, 7):
        energy_level = "Medium"
    else:
        energy_level = "Low"

    return {
        "house_position": house_position,
        "is_favorable": is_favorable,
        "energy_level": energy_level,
    }
