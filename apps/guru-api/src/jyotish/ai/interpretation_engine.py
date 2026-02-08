"""
Interpretation Engine — DATA ONLY (Full LLM Narrative Synthesis Mode).

Backend computes and returns structured astrological data.
NO prose generation. NO sentence construction.
LLM generates full discourse from this data.

Kept for:
- Stress flags (remedy gating)
- Tara category helpers
- apply_tara_global_tone (post-process LLM output)
"""

from typing import Any, Dict

# House type categories (BPHS) — for internal logic only
KENDRAS = {1, 4, 7, 10}
TRIKONAS = {1, 5, 9}
DUSTHANA = {6, 8, 12}

# Thresholds
BAV_BINDU_THRESHOLD = 4  # Below this → stress indicator
TARA_CAUTIONARY = {"Naidhana", "Vipat", "Pratyak", "Janma"}
TARA_MEASURED = {"Sadhaka", "Kshema"}


def _get_tara_category(context: Dict[str, Any]) -> str:
    tara = context.get("tara_bala") or {}
    if isinstance(tara, dict):
        return (tara.get("tara_category") or tara.get("tara_name") or "").strip()
    return ""


def compute_stress_flags(context: Dict[str, Any]) -> Dict[str, bool]:
    """
    Compute remedy gating flags from chart data.
    Returns: {severe_stress: bool, moderate_stress: bool}
    Used by LLM prompt to gate remedy suggestions.
    """
    severe = False
    moderate = False

    tara_cat = _get_tara_category(context)
    transit = context.get("transit") or {}
    quality = context.get("quality") or {}
    time_block = context.get("time") or {}
    lordship = context.get("lordship") or {}

    # Chandrashtama → severe
    moon_data = transit.get("Moon")
    if isinstance(moon_data, dict) and moon_data.get("house_from_moon") == 8:
        severe = True

    # Naidhana / Vipat Tara + low bindu → severe or moderate
    if tara_cat in ("Naidhana", "Vipat"):
        severe = True
    elif tara_cat in ("Pratyak", "Janma"):
        moderate = True

    # Malefic Mahadasha with weakness
    mahadasha = (time_block.get("mahadasha_lord") or "").strip()
    if mahadasha in ("Saturn", "Mars", "Rahu", "Ketu"):
        lord_data = lordship.get(mahadasha) or {}
        owned = set(lord_data.get("lordships") or [])
        if owned & DUSTHANA:
            if not severe:
                moderate = True

    # Low bindu in multiple houses
    low_bindu_count = 0
    for pname, qdata in quality.items():
        if isinstance(qdata, dict):
            b = qdata.get("bindu")
            if b is not None and int(b) < BAV_BINDU_THRESHOLD:
                low_bindu_count += 1
    if low_bindu_count >= 3 and not severe:
        moderate = True

    return {"severe_stress": severe, "moderate_stress": moderate}


def apply_tara_global_tone(text: str, context: Dict[str, Any]) -> str:
    """
    Tara Bala modifies tone globally (post-process on LLM output).
    Naidhana/Vipat/Pratyak → no optimistic phrasing anywhere.
    """
    tara_cat = _get_tara_category(context)
    if tara_cat not in TARA_CAUTIONARY:
        return text
    for phrase in [
        "strongly favor",
        "excellent",
        "wonderful",
        "great success",
        "highly favorable",
    ]:
        if phrase.lower() in text.lower():
            text = text.replace(phrase, "may support").replace(phrase.title(), "May support")
    return text
