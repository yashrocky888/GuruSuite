"""
Guru Context AI Prediction API.

POST /predict — build Guru Context JSON and get AI guidance (Daily/Monthly/Yearly).
"""

import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import pytz
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.config import settings
from src.jyotish.ai.guru_payload import (
    build_guru_context,
    _monthly_planet_shifts,
    _yearly_planet_shifts,
)
from src.ai.post_processor import (
    validate_and_format_guidance,
    apply_dharma_graha_tone_to_section,
)
from src.ai.llm_client import LLMClient
from src.jyotish.ai.interpretation_engine import apply_tara_global_tone
from src.ai.rishi_prompt import RISHI_PRESENCE_PROMPT, RISHI_NARRATIVE_REFINEMENT_PROMPT
from src.utils.timezone import get_julian_day, local_to_utc


# Backend-authored Moon transition: sign_index (0–11) → display name (matches prompt table)
SIGN_INDEX_TO_DISPLAY = {
    0: "Aries (Mesha)",
    1: "Taurus (Vrishabha)",
    2: "Gemini (Mithuna)",
    3: "Cancer (Karka)",
    4: "Leo (Simha)",
    5: "Virgo (Kanya)",
    6: "Libra (Tula)",
    7: "Scorpio (Vrischika)",
    8: "Sagittarius (Dhanu)",
    9: "Capricorn (Makara)",
    10: "Aquarius (Kumbha)",
    11: "Pisces (Meena)",
}

# Weekday name → day lord (for authority order)
WEEKDAY_NAME_TO_LORD = {
    "Sunday": "Sun",
    "Monday": "Moon",
    "Tuesday": "Mars",
    "Wednesday": "Mercury",
    "Thursday": "Jupiter",
    "Friday": "Venus",
    "Saturday": "Saturn",
}

# Authority order: Mahadasha, Antardasha, Moon, Day Lord, Jupiter, Saturn, then rest (Sun, Mars, Mercury, Venus)
AUTHORITY_ORDER_AFTER_SATURN = ["Sun", "Mars", "Mercury", "Venus"]

# Structured prediction keys (fixed order for assembly)
STRUCTURED_KEYS = [
    "panchanga",
    "dasha",
    "chandra_bala",
    "tara_bala",
    "major_transits",
    "dharmic_guidance",
    "throne",
    "moon_movement",
]

# Canonical section headings — NEVER collapse. Ceremonial structure preserved.
CANONICAL_SECTION_HEADINGS = {
    "greeting": "",
    "declarations": "🪐 CURRENT SKY POSITION",
    "panchanga": "🕉 PANCHANGA OF THE DAY",
    "dasha": "👑 DASHA AUTHORITY",
    "chandra_bala": "🌙 CHANDRA BALA",
    "tara_bala": "⭐ TARA BALA",
    "major_transits": "🪐 MAJOR TRANSITS",
    "dharmic_guidance": "⚖ DHARMA GUIDANCE",
    "throne": "🪔 JANMA NAKSHATRA THRONE",
    "moon_movement": "🔄 MOON MOVEMENT",
}
CANONICAL_SECTION_ORDER = [
    "greeting", "declarations", "panchanga", "dasha", "chandra_bala",
    "tara_bala", "major_transits", "dharmic_guidance", "throne", "moon_movement",
]

# Backend-owned interpretation for same-day Moon house shift (from_house, to_house) only.
MOON_HOUSE_SHIFT_MEANING = {
    (9, 10): "This marks a shift from reflection and belief toward action, responsibility, and professional visibility. Mental energy moves toward execution rather than contemplation.",
    (10, 11): "Attention moves from duty to collaboration, networking, and future planning.",
    (11, 12): "Attention turns inward. What was social becomes solitary. Reflection replaces interaction. Let the mind withdraw before it acts again.",
    (8, 9): "The mind lifts from inner intensity toward learning, guidance, and broader perspective.",
    (6, 7): "Work-related pressure transitions into partnership and negotiation themes.",
    (1, 2): "Focus moves from self-awareness toward resources, stability, and values.",
}
DEFAULT_MEANING = "Attention moves from one life area toward another. What was external becomes internal."

# Backend-owned interpretation for monthly planet house shifts (from_house, to_house) only.
MONTHLY_HOUSE_SHIFT_MEANING = {
    (3, 4): "Focus shifts from communication and initiative toward home, emotional stability, and foundational planning.",
    (4, 5): "Energy moves from domestic concerns toward creativity, expression, and strategic risk.",
    (5, 6): "Attention shifts from creativity toward work discipline and problem-solving.",
    (6, 7): "Work-related pressure transitions into partnership and negotiation themes.",
    (8, 9): "Intensity transforms into learning, guidance, and broader perspective.",
    (9, 10): "Beliefs and reflection convert into action, responsibility, and professional visibility.",
    (10, 11): "Professional focus shifts toward collaboration, networking, and long-term goals.",
    (11, 12): "External gains shift toward rest, retreat, and strategic withdrawal.",
    (1, 2): "Self-focus transitions toward resources, stability, and financial structure.",
}
DEFAULT_MONTHLY_MEANING = (
    "The emphasis of the month gradually moves from one life area to another, "
    "requiring strategic adjustment and flexibility."
)


def _house_from_lagna(sign_index: int, lagna_sign_index: int) -> int:
    """House 1–12 from Lagna using sign-based formula only."""
    return ((sign_index - lagna_sign_index) % 12) + 1


def _house_ordinal(n: int) -> str:
    """e.g. 9 -> '9th', 10 -> '10th', 1 -> '1st'."""
    if 10 <= n % 100 <= 20:
        return f"{n}th"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _normalize_declaration_block(block: str) -> str:
    """Ensure one planet per line. No inline stacking or concatenation."""
    if not block or not block.strip():
        return block.strip()
    # Split by declaration start: "Planet currently transits" (lookahead)
    parts = re.split(
        r"(?=(Mercury|Venus|Mars|Jupiter|Saturn|Sun|Moon|Rahu|Ketu)\s+currently\s+transits)",
        block,
        flags=re.IGNORECASE,
    )
    lines = []
    if parts[0].strip():
        lines.append(parts[0].strip())
    # parts[i]=planet name, parts[i+1]=full declaration (lookahead doesn't consume)
    for i in range(1, len(parts) - 1, 2):
        decl = parts[i + 1].strip()
        if decl:
            lines.append(decl)
    if not lines:
        return block.strip()
    return "\n".join(lines).strip()


def _format_declarations_for_display(declarations_block: str) -> str:
    """Format backend declarations as 'Planet — Sign — Nth House' for structured display."""
    if not declarations_block:
        return ""
    lines = []
    for line in declarations_block.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        # Match "Planet currently transits Sign in your Nth house. (Retrograde)?"
        m = re.match(
            r"^(Mercury|Venus|Mars|Jupiter|Saturn|Sun|Moon|Rahu|Ketu)\s+currently\s+transits\s+(.+?)\s+in\s+your\s+(\d+(?:st|nd|rd|th))\s+house\.(?:\s*\(Retrograde\))?$",
            line,
            re.IGNORECASE,
        )
        if m:
            planet, sign, house = m.group(1), m.group(2).strip(), m.group(3)
            lines.append(f"{planet} — {sign} — {house} House")
    if not lines:
        return declarations_block
    # Header only from frontend (🪐 Current Sky Position). No duplicate.
    return "\n".join(lines)


def _safe_str(val: Any) -> str:
    """Coerce JSON value to string; handle dict (model sometimes returns nested object)."""
    if val is None:
        return ""
    if isinstance(val, dict):
        return " ".join(str(v) for v in val.values() if v).strip()
    if isinstance(val, str):
        return val.strip()
    return str(val).strip()


REQUIRED_STRUCTURED_SECTIONS = [
    "panchanga", "dasha", "chandra_bala", "tara_bala",
    "major_transits", "dharmic_guidance", "throne", "moon_movement",
]


def _get_transit_planet_order(context: Dict[str, Any]) -> List[str]:
    """Return transit planets in declaration order: Mahadasha, Antardasha, classical, Rahu, Ketu."""
    transit = context.get("transit") or {}
    if not transit:
        return []
    time_block = context.get("time") or {}
    mahadasha = (time_block.get("mahadasha_lord") or "").strip()
    antardasha = (time_block.get("antardasha_lord") or "").strip()
    panchanga_raw = context.get("panchanga") or {}
    if isinstance(panchanga_raw, dict) and panchanga_raw.get("panchanga"):
        panchanga_raw = panchanga_raw.get("panchanga") or panchanga_raw
    vara = panchanga_raw.get("vara") if isinstance(panchanga_raw, dict) else {}
    day_lord = (vara.get("lord") if isinstance(vara, dict) else None) or ""
    weekday_name = panchanga_raw.get("weekday") if isinstance(panchanga_raw, dict) else ""
    if not day_lord and weekday_name:
        day_lord = WEEKDAY_NAME_TO_LORD.get(weekday_name, "")
    order = []
    if mahadasha and mahadasha in transit:
        order.append(mahadasha)
    if antardasha and antardasha in transit and antardasha not in order:
        order.append(antardasha)
    if "Moon" in transit and "Moon" not in order:
        order.append("Moon")
    if day_lord and day_lord in transit and day_lord not in order:
        order.append(day_lord)
    if "Jupiter" in transit and "Jupiter" not in order:
        order.append("Jupiter")
    if "Saturn" in transit and "Saturn" not in order:
        order.append("Saturn")
    for p in AUTHORITY_ORDER_AFTER_SATURN:
        if p in transit and p not in order:
            order.append(p)
    if "Rahu" in transit and "Rahu" not in order:
        order.append("Rahu")
    if "Ketu" in transit and "Ketu" not in order:
        order.append("Ketu")
    for p, _ in transit.items():
        if p not in order:
            order.append(p)
    return order


def _build_guidance_with_structure(structured: Dict[str, str]) -> str:
    """
    Rebuild final guidance from structured sections WITH canonical headings.
    NEVER output raw body. Always preserve ceremonial structure.
    All sections with headings appear; content may be empty.
    """
    parts = []
    for key in CANONICAL_SECTION_ORDER:
        content = (structured.get(key) or "").strip()
        heading = CANONICAL_SECTION_HEADINGS.get(key, "")
        if key == "greeting":
            if content:
                parts.append(content)
        elif heading:
            parts.append(heading)
            if content:
                parts.append(content)
        elif content:
            parts.append(content)
    return "\n\n".join(parts).strip()


# Panchanga vara-lord closing (Guru presence — one line per day lord)
PANCHANGA_VARA_CLOSING = {
    "Sun": "The current of authority runs strong; let it serve righteousness.",
    "Moon": "The current of emotion flows; steadiness must guide it.",
    "Mars": "The current of action is keen; discipline must temper it.",
    "Mercury": "The current of speech is active; clarity must govern it.",
    "Jupiter": "The current of expansion favors growth; wisdom must direct it.",
    "Venus": "The current of relationship and value flows; harmony must guide it.",
    "Saturn": "The current of effort runs strong, but steadiness must guide it.",
}

def _build_backend_panchanga(context: Dict[str, Any]) -> str:
    """
    Build Panchanga text ONLY from backend JSON. One flowing sentence. No LLM. No hallucination.
    Format: "On this {tithi} of the {paksha}, under {nakshatra}, with {yoga} Yoga prevailing and {karana} active, the day unfolds under the governance of {vara lord}."
    """
    panchanga_raw = context.get("panchanga") or {}
    if isinstance(panchanga_raw, dict) and panchanga_raw.get("panchanga"):
        panchanga_raw = panchanga_raw.get("panchanga") or panchanga_raw
    if not isinstance(panchanga_raw, dict):
        return ""
    tithi_obj = panchanga_raw.get("tithi") or {}
    tithi_cur = (tithi_obj.get("current") or {}) if isinstance(tithi_obj, dict) else {}
    tithi_name = (tithi_cur.get("name") or "").strip() if isinstance(tithi_cur, dict) else ""
    paksha = ((tithi_cur or {}).get("paksha") or panchanga_raw.get("paksha") or "").strip()
    if paksha and "Paksha" not in paksha:
        paksha = f"{paksha} Paksha"
    nak_obj = panchanga_raw.get("nakshatra") or {}
    nak_cur = nak_obj.get("current") if isinstance(nak_obj, dict) else nak_obj
    nakshatra = (nak_cur.get("name") or "").strip() if isinstance(nak_cur, dict) else ""
    vara = panchanga_raw.get("vara") or {}
    vara_lord = (vara.get("lord") or vara.get("name") or panchanga_raw.get("weekday") or "").strip() if isinstance(vara, dict) else ""
    yoga_obj = panchanga_raw.get("yoga") or {}
    yoga_cur = yoga_obj.get("current") if isinstance(yoga_obj, dict) else yoga_obj
    yoga_name = (yoga_cur.get("name") or "").strip() if isinstance(yoga_cur, dict) else ""
    karana_raw = panchanga_raw.get("karana")
    karana_name = ""
    if isinstance(karana_raw, list) and karana_raw:
        first_k = karana_raw[0]
        karana_name = (first_k.get("name") or "").strip() if isinstance(first_k, dict) else ""
    elif isinstance(karana_raw, dict):
        karana_name = (karana_raw.get("name") or "").strip()
    if tithi_name and paksha and nakshatra and vara_lord and yoga_name and karana_name:
        base = f"On this {tithi_name} of the {paksha}, under {nakshatra}, with {yoga_name} Yoga prevailing and {karana_name} active, the day unfolds under the governance of {vara_lord}."
        closing = PANCHANGA_VARA_CLOSING.get(vara_lord, "")
        if closing:
            return base + " " + closing
        return base
    # Fallback: build from available parts
    parts = []
    if tithi_name and paksha:
        parts.append(f"On this {tithi_name} of the {paksha}")
    if nakshatra:
        parts.append(f"under {nakshatra}")
    if yoga_name:
        parts.append(f"with {yoga_name} Yoga prevailing")
    if karana_name:
        parts.append(f"and {karana_name} active")
    if vara_lord:
        parts.append(f"the day unfolds under the governance of {vara_lord}")
    if parts:
        base = ", ".join(parts) + "."
        closing = PANCHANGA_VARA_CLOSING.get(vara_lord, "")
        if closing:
            return base + " " + closing
        return base
    return ""


def _build_greeting(seeker_name: str, context: Dict[str, Any]) -> str:
    """
    One sentence only. No praise. No motivational exaggeration. Classical tone.
    Format: "{Name}, on this {tithi} of the {paksha}, the wheel of Time turns thus:"
    Name is title-cased for personal presence.
    """
    raw = (seeker_name or "Seeker").strip()
    name = " ".join(w.capitalize() for w in raw.split()) if raw else "Seeker"
    panchanga_raw = context.get("panchanga") or {}
    if isinstance(panchanga_raw, dict) and panchanga_raw.get("panchanga"):
        panchanga_raw = panchanga_raw.get("panchanga") or panchanga_raw
    tithi_name = ""
    paksha = ""
    if isinstance(panchanga_raw, dict):
        tithi_obj = panchanga_raw.get("tithi") or {}
        tithi_cur = tithi_obj.get("current") if isinstance(tithi_obj, dict) else {}
        tithi_name = (tithi_cur.get("name") or "").strip() if isinstance(tithi_cur, dict) else ""
        paksha = (tithi_cur.get("paksha") or panchanga_raw.get("paksha") or "").strip() if isinstance(tithi_cur, dict) else ""
        if not paksha and isinstance(panchanga_raw.get("paksha"), str):
            paksha = panchanga_raw.get("paksha", "").strip()
        if paksha and "Paksha" not in paksha:
            paksha = f"{paksha} Paksha"
    if not tithi_name or not paksha:
        return f"{name}, the wheel of Time turns thus:"
    return f"{name}, on this {tithi_name} of the {paksha}, the wheel of Time turns thus:"


def _fill_missing_section(key: str, val: str, context: Dict[str, Any]) -> str:
    """If val is empty, use placeholder. Full LLM synthesis — no deterministic prose."""
    if val and val.strip():
        return val.strip()
    return "Interpretation unavailable for this section."


def _assemble_structured_output(
    declarations_block: str,
    parsed: Dict[str, str],
    context: Dict[str, Any],
    seeker_name: str = "",
) -> tuple:
    """
    Assemble structured dict and concatenated guidance string.
    Full LLM synthesis — no deterministic prose. LLM generates all sections.
    """
    structured: Dict[str, str] = {
        "declarations": _format_declarations_for_display(declarations_block),
    }
    for key in REQUIRED_STRUCTURED_SECTIONS:
        val = _safe_str(parsed.get(key))
        val = _fill_missing_section(key, val, context)
        structured[key] = val
    major_transits = structured.get("major_transits") or ""
    major_transits = apply_tara_global_tone(major_transits, context)
    structured["major_transits"] = major_transits
    # Greeting from LLM (with Guru self-introduction)
    name = (seeker_name or "Seeker").strip()
    greeting = _safe_str(parsed.get("greeting"))
    if not greeting or not greeting.strip():
        greeting = f"{name}, the wheel of Time turns thus:"
    structured["greeting"] = greeting
    parts = []
    parts.append(greeting)
    if declarations_block:
        parts.append(_normalize_declaration_block(declarations_block))
    for key in STRUCTURED_KEYS:
        val = structured.get(key) or ""
        if key == "declarations":
            continue
        if val:
            parts.append(val)
    guidance_str = "\n\n".join(parts).strip()
    return guidance_str, structured


def _build_transit_declarations_and_retro(context: Dict[str, Any]) -> tuple:
    """
    Backend-enforced transit declarations and allowed-retrograde set.
    Returns (declarations_block: str, allowed_retrograde: set of lowercase planet names).
    Deterministic: no LLM dependence for structure.
    """
    transit = context.get("transit") or {}
    if not transit:
        return "", set()

    time_block = context.get("time") or {}
    mahadasha = (time_block.get("mahadasha_lord") or "").strip()
    antardasha = (time_block.get("antardasha_lord") or "").strip()

    panchanga_raw = context.get("panchanga") or {}
    if isinstance(panchanga_raw, dict) and panchanga_raw.get("panchanga"):
        panchanga_raw = panchanga_raw.get("panchanga") or panchanga_raw
    vara = panchanga_raw.get("vara") if isinstance(panchanga_raw, dict) else {}
    day_lord = (vara.get("lord") if isinstance(vara, dict) else None) or ""
    weekday_name = panchanga_raw.get("weekday") if isinstance(panchanga_raw, dict) else ""
    if not day_lord and weekday_name:
        day_lord = WEEKDAY_NAME_TO_LORD.get(weekday_name, "")

    # Build allowed retrograde from transit, natal, shifts
    allowed_retrograde = set()
    for pname, pdata in transit.items():
        if isinstance(pdata, dict) and pdata.get("is_retrograde") is True:
            allowed_retrograde.add((pname or "").lower())
    natal = context.get("natal") or {}
    natal_planets = natal.get("planets") or natal.get("planets_d1") or {}
    for pname, pdata in natal_planets.items():
        if isinstance(pdata, dict) and pdata.get("is_retrograde") is True:
            allowed_retrograde.add((pname or "").lower())
    for shift in context.get("yearly_transits", []) + context.get("monthly_transits", []):
        if shift.get("is_retrograde"):
            allowed_retrograde.add((shift.get("planet") or "").lower())

    # Ordered list: Mahadasha, Antardasha, Moon, Day Lord, Jupiter, Saturn, then Sun, Mars, Mercury, Venus
    order = []
    if mahadasha and mahadasha in transit:
        order.append(mahadasha)
    if antardasha and antardasha in transit and antardasha not in order:
        order.append(antardasha)
    if "Moon" in transit and "Moon" not in order:
        order.append("Moon")
    if day_lord and day_lord in transit and day_lord not in order:
        order.append(day_lord)
    if "Jupiter" in transit and "Jupiter" not in order:
        order.append("Jupiter")
    if "Saturn" in transit and "Saturn" not in order:
        order.append("Saturn")
    for p in AUTHORITY_ORDER_AFTER_SATURN:
        if p in transit and p not in order:
            order.append(p)
    # Rahu, Ketu after Saturn (classical order per MAHABHARATA DAIVA-JÑA lock)
    if "Rahu" in transit and "Rahu" not in order:
        order.append("Rahu")
    if "Ketu" in transit and "Ketu" not in order:
        order.append("Ketu")

    lines = []
    for planet in order:
        pdata = transit.get(planet)
        if not isinstance(pdata, dict):
            continue
        sign_index = pdata.get("sign_index")
        house = pdata.get("transit_house") or pdata.get("house_from_lagna")
        if sign_index is None or house is None:
            continue
        sign_display = SIGN_INDEX_TO_DISPLAY.get(sign_index % 12, "")
        if not sign_display:
            continue
        house_ord = _house_ordinal(house)
        if (planet or "").lower() in allowed_retrograde:
            line = f"{planet} currently transits {sign_display} in your {house_ord} house. (Retrograde)"
        else:
            line = f"{planet} currently transits {sign_display} in your {house_ord} house."
        lines.append(line)

    # Any transit planet not yet in order (e.g. Rahu/Ketu not in payload; defensive)
    for planet, pdata in transit.items():
        if planet in order:
            continue
        if not isinstance(pdata, dict):
            continue
        sign_index = pdata.get("sign_index")
        house = pdata.get("transit_house") or pdata.get("house_from_lagna")
        if sign_index is None or house is None:
            continue
        sign_display = SIGN_INDEX_TO_DISPLAY.get(sign_index % 12, "")
        if not sign_display:
            continue
        house_ord = _house_ordinal(house)
        if (planet or "").lower() in allowed_retrograde:
            lines.append(f"{planet} currently transits {sign_display} in your {house_ord} house. (Retrograde)")
        else:
            lines.append(f"{planet} currently transits {sign_display} in your {house_ord} house.")

    block = "\n".join(lines) if lines else ""
    return block, allowed_retrograde


def _strip_disallowed_retrograde(guidance: str, allowed_retrograde: set) -> str:
    """
    Remove only sentences that mention retrograde/vakri for a planet not in allowed_retrograde.
    Never touch backend declaration lines (X currently transits ... in your N house.).
    """
    if not guidance or not guidance.strip():
        return guidance
    allowed = {p.lower() for p in allowed_retrograde}
    planet_names = ["mercury", "venus", "mars", "jupiter", "saturn", "sun", "moon"]
    retro_keywords = ["retrograde", "vakri", "revisitation", "reversal", "karmic return", "return cycle", "internalized", "reprocessing"]
    # Backend declaration pattern: do not strip these (allow leading ws/newline)
    # Includes Rahu, Ketu per MAHABHARATA DAIVA-JÑA full planet lock
    declaration_re = re.compile(
        r"^\s*(?:\s*\(Retrograde\)\s*\n?)?"
        r"(Mercury|Venus|Mars|Jupiter|Saturn|Sun|Moon|Rahu|Ketu)\s+currently\s+transits\s+.+?\s+in\s+your\s+\d+(?:st|nd|rd|th)\s+house\.(?:\s*\(Retrograde\))?\s*$",
        re.IGNORECASE | re.DOTALL,
    )
    # Do not split after ". " when followed by " (Retrograde)" so declaration stays one segment
    parts = re.split(r"(?<=[.!?])\s+(?!\s*\(Retrograde\))", guidance)
    out = []
    for part in parts:
        part_stripped = part.strip()
        if not part_stripped:
            continue
        if declaration_re.match(part_stripped):
            out.append(part_stripped)
            continue
        lower = part_stripped.lower()
        has_retro = any(kw in lower for kw in retro_keywords)
        if not has_retro:
            out.append(part_stripped)
            continue
        remove = False
        for planet in planet_names:
            if planet in allowed:
                continue
            if re.search(rf"\b{planet}\b", lower):
                remove = True
                break
        if not remove:
            out.append(part_stripped)
    return " ".join(out).strip()


def _strip_ai_later_today_moon(guidance: str) -> str:
    """Remove any sentence that starts with 'Later today, the Moon' (AI-authored)."""
    if not guidance or "Later today, the Moon" not in guidance:
        return guidance
    # Remove block from "Later today, the Moon" to next \n\n or end (may be multi-line)
    pattern = r"\s*Later today, the Moon[\s\S]*?(?=\n\n|$)"
    return re.sub(pattern, "", guidance, count=1).strip()


def _backend_moon_transit_sentence(
    from_sign_index: int,
    from_house: int,
    to_sign_index: int,
    to_house: int,
) -> str:
    """Deterministic sentence from transit_events payload only."""
    from_name = SIGN_INDEX_TO_DISPLAY.get(from_sign_index % 12, "")
    to_name = SIGN_INDEX_TO_DISPLAY.get(to_sign_index % 12, "")
    from_ord = _house_ordinal(from_house)
    to_ord = _house_ordinal(to_house)
    return (
        f"Later today, the Moon moves from\n"
        f"{from_name} in your {from_ord} house\n"
        f"to\n"
        f"{to_name} in your {to_ord} house."
    )


def _apply_daily_moon_transit_override(
    context: Dict[str, Any],
    timescale: str,
    guidance: str,
) -> str:
    """
    DAILY only: replace AI Moon transition sentence with backend-authored one.
    If from_house == to_house, strip AI sentence and do not narrate (fail-safe).
    """
    if timescale != "daily" or not guidance:
        return guidance

    events: List[Dict[str, Any]] = context.get("transit_events") or []
    moon_event = None
    for ev in events:
        if (
            ev.get("event") == "sign_change"
            and ev.get("planet") == "Moon"
            and ev.get("from_sign_index") != ev.get("to_sign_index")
        ):
            moon_event = ev
            break

    if not moon_event:
        return guidance

    from_house = moon_event.get("from_house")
    to_house = moon_event.get("to_house")
    if from_house is None or to_house is None:
        return guidance
    if from_house == to_house:
        return _strip_ai_later_today_moon(guidance)

    guidance_stripped = _strip_ai_later_today_moon(guidance)
    backend_sentence = _backend_moon_transit_sentence(
        moon_event.get("from_sign_index", 0),
        from_house,
        moon_event.get("to_sign_index", 0),
        to_house,
    )
    meaning = MOON_HOUSE_SHIFT_MEANING.get(
        (from_house, to_house),
        DEFAULT_MEANING,
    )
    moon_block = backend_sentence + "\n\n" + meaning
    if not guidance_stripped:
        return moon_block
    return guidance_stripped.rstrip() + "\n\n" + moon_block


def _apply_monthly_transit_override(
    context: Dict[str, Any],
    timescale: str,
    guidance: str,
) -> str:
    """
    MONTHLY only: append deterministic future sign→house transitions from monthly_transits.
    Backend-owned; no AI interpretation of future shifts.
    """
    if timescale != "monthly":
        return guidance

    monthly_transits = context.get("monthly_transits") or []
    if not monthly_transits:
        return guidance

    asc = context.get("natal", {}).get("ascendant", {}).get("degree", 0)
    lagna_sign_index = int(asc // 30) % 12

    sentences: List[str] = []

    for shift in monthly_transits:
        planet = shift.get("planet")
        from_idx = shift.get("from_sign_index")
        to_idx = shift.get("to_sign_index")

        if from_idx is None or to_idx is None:
            continue
        if from_idx == to_idx:
            continue

        from_house = _house_from_lagna(from_idx, lagna_sign_index)
        to_house = _house_from_lagna(to_idx, lagna_sign_index)

        meaning = MONTHLY_HOUSE_SHIFT_MEANING.get(
            (from_house, to_house),
            DEFAULT_MONTHLY_MEANING,
        )

        from_name = SIGN_INDEX_TO_DISPLAY.get(from_idx % 12, "")
        to_name = SIGN_INDEX_TO_DISPLAY.get(to_idx % 12, "")
        from_ord = _house_ordinal(from_house)
        to_ord = _house_ordinal(to_house)

        sentence = (
            f"Later this month, {planet} moves from "
            f"{from_name} in your {from_ord} house "
            f"to "
            f"{to_name} in your {to_ord} house.\n\n"
            f"{meaning}"
        )
        sentences.append(sentence)

    if sentences:
        guidance = guidance.rstrip() + "\n\n" + "\n\n".join(sentences)

    return guidance


# LOCKED — MASTER GURU SYSTEM PROMPT (DO NOT MODIFY per task)
GURU_SYSTEM_PROMPT = """You are an ancient Vedic Rishi (Guru). Use the provided JSON data only. RULE 1: Only predict what the Dasha permits. RULE 2: Use Shadbala to determine the 'power' of the advice. RULE 3: Use Ashtakavarga to determine 'comfort' or 'stress'. Speak technically but practically. Name the planets and the reasons. Truth over appearance.

""" + RISHI_PRESENCE_PROMPT + """

==================================================
CLASSICAL JYOTISHA DOCTRINE (AUTHORITATIVE LAYER)
==================================================

You are not a modern motivational speaker.
You are a classical Vedic Jyotishi.

Your interpretation must follow these timeless principles:

1. KARMA FIRST PRINCIPLE
   - No event happens randomly.
   - Transit activates natal karma.
   - Dasha grants permission.
   - Transit triggers manifestation.
   - Ashtakavarga determines comfort.
   - Strength (Shadbala) determines capacity.

2. DASHA OVERRIDES TRANSIT
   - If Dasha lord is weak, transit results are limited.
   - If Dasha lord is strong, transit becomes powerful.
   - Always interpret transit through Mahadasha lens.

3. HOUSE IS FIELD OF EXPERIENCE
   - 1: Self
   - 2: Wealth & speech
   - 3: Courage & effort
   - 4: Home & emotional base
   - 5: Creativity & intelligence
   - 6: Conflict & service
   - 7: Partnership
   - 8: Transformation
   - 9: Dharma & wisdom
   - 10: Karma & profession
   - 11: Gains
   - 12: Loss & liberation

4. RETROGRADE (VAKRI) DOCTRINE
   - Retrograde increases internal force.
   - Retrograde is karmic revisitation.
   - Retrograde intensifies psychological dimension.
   - Retrograde delays external results but deepens inner transformation.
   - Retrograde often gives results of the previous house revisited.

5. ASHTAKAVARGA RULE
   - 0–1 bindu → discomfort, effort required.
   - 2–3 bindu → moderate support.
   - 4+ bindu → strong support.
   - Low bindu does not deny results; it increases struggle.

6. TRANSIT CYCLE RULE
   - First forward movement = activation.
   - Retrograde return = correction.
   - Final forward movement = consolidation and delivery.

7. PLANETARY NATURE MUST BE HONORED
   - Jupiter expands and protects.
   - Saturn restricts and disciplines.
   - Mars energizes and confronts.
   - Mercury intellectualizes.
   - Venus harmonizes.
   - Sun centralizes authority.
   - Moon governs mind.

8. NEVER SPEAK GENERICALLY
   - Always link planet + house + dasha + bindu.
   - Always explain WHY, not just WHAT.

9. TONE
   - Speak like a teacher of dharma.
   - Calm, precise, classical.
   - No modern slang.
   - No psychological fluff.
   - No exaggerated positivity.
   - No fear-based language.

10. RESULT PHILOSOPHY
   - Even stress has purpose.
   - Even delay has design.
   - Even retrograde has refinement.

You interpret according to timeless Jyotisha.
You do not invent mythology.
You do not quote texts.
You apply principles.

==================================================
END OF CLASSICAL DOCTRINE
==================================================

==================================================
TIME-BINDING (SANKALPA) INVOCATION RULE
==================================================

Before giving prediction, you MUST invoke Kala (Sacred Time) using the "panchanga" block in the JSON — IF AND ONLY IF that data exists.

You are forbidden from inventing Panchanga elements.

You may only use:
- tithi
- paksha
- nakshatra
- lunar_month (masa)
- samvatsara (vedic year name)
- weekday (if provided)

--------------------------------------------------
DAILY HORIZON – SANKALPA OPENING
--------------------------------------------------

IF TARGET TIMESCALE = DAILY
AND JSON contains panchanga.tithi AND panchanga.paksha:

You MUST open with a classical Sankalpa invocation.

Format example:

"On this sacred [Tithi Name] of the [Paksha Name], under the guiding star of [Nakshatra], the wheel of Time turns with a specific intention."

Then briefly describe:
- Whether it is Shukla (waxing) or Krishna (waning)
- Psychological quality of the Tithi
- Spiritual quality of the Nakshatra

Tone:
- Temple-like
- Calm
- Scriptural
- Not theatrical
- Not exaggerated

Do NOT invent deity stories.
Do NOT exaggerate auspiciousness.
Do NOT exceed 3–4 sentences.

--------------------------------------------------
MONTHLY HORIZON – MASA INVOCATION
--------------------------------------------------

IF TARGET TIMESCALE = MONTHLY
AND JSON contains panchanga.lunar_month:

You MUST open with the Vedic lunar month (Masa).

Example structure:

"As the sacred month of [Masa Name] unfolds, Time carries the signature of its ancient purpose."

Then briefly explain:
- Spiritual quality of this month
- Whether it is aligned with purification, discipline, harvest, austerity, or expansion
- Link Sun's current transit sign

Maximum 4 sentences.
No mythology storytelling.
No invented legends.
Remain philosophical and grounded.

--------------------------------------------------
YEARLY HORIZON – SAMVATSARA INVOCATION
--------------------------------------------------

IF TARGET TIMESCALE = YEARLY
AND JSON contains panchanga.samvatsara:

You MUST open with the Vedic Year name (Samvatsara).

Structure:

"We stand within the cycle of the [Samvatsara Name] Samvatsara, a year governed by a distinct karmic rhythm."

Then briefly explain:
- Whether the year indicates discipline, restructuring, expansion, purification, karmic testing, consolidation, or renewal.
- Keep interpretation philosophical, not predictive.
- Maximum 4 sentences.

Do NOT fabricate scriptural verses.
Do NOT claim authority from specific texts.
Speak from principle only.

--------------------------------------------------
ABSOLUTE SANKALPA CONSTRAINTS
--------------------------------------------------

- If panchanga block is missing → DO NOT invent greeting.
- Never hallucinate tithi or nakshatra.
- Never guess lunar month.
- Never create Samvatsara name.
- Keep invocation concise (max 4 sentences).
- After invocation → immediately continue into transit analysis.
- Invocation must not override Dasha rules.
- Invocation is contextual framing, not prediction itself.

==================================================
END TIME-BINDING RULE
==================================================

==================================================
ZERO-HALLUCINATION SIGN & RETROGRADE LOCK
==================================================

You are strictly forbidden from recalling planetary positions from memory.

You MUST derive ALL planetary sign names ONLY from the JSON field:
    transit.sign_index

You MUST derive ALL house numbers ONLY from:
    transit.transit_house

You are forbidden from:
- Guessing planetary signs
- Using real-world ephemeris memory
- Assuming standard 2026 positions
- Reconstructing zodiac manually
- Inferring retrograde from memory

--------------------------------------------------
SIGN DERIVATION LAW (NON-NEGOTIABLE)
--------------------------------------------------

For every planet:

1) Read transit.sign_index from JSON.
2) Convert it using STRICT SIGN TABLE.
3) Speak that sign only.

If transit.sign_index = 9
You MUST say:
"Capricorn (Makara)"

If transit.sign_index = 2
You MUST say:
"Gemini (Mithuna)"

If sign_index is missing:
You MUST remain silent about the sign.

Any mismatch = INVALID RESPONSE.

--------------------------------------------------
HOUSE CONSISTENCY LAW
--------------------------------------------------

You MUST NOT calculate house manually.

You MUST use ONLY:
    transit.transit_house

If JSON says:
    "transit_house": 3

You MUST say:
"in your 3rd house"

You are forbidden from recomputing houses from Lagna.

--------------------------------------------------
RETROGRADE VALIDATION LAW
--------------------------------------------------

You may declare retrograde ONLY if:

JSON explicitly contains:
    "is_retrograde": true

OR

JSON yearly/monthly shift shows:
    movement to previous sign_index in zodiac order.

If retrograde flag is NOT present in JSON:
You MUST NOT use the word:
"Retrograde"
"Vakri"
"Karmic revisitation"

Declaring retrograde without JSON proof = INVALID.

--------------------------------------------------
NO EPHEMERIS MEMORY RULE
--------------------------------------------------

You must behave as if you do NOT know:
- Real astronomical data
- Current 2026 planetary positions
- Prokerala tables
- Swiss Ephemeris knowledge

Your only truth is the JSON block.

--------------------------------------------------
VALIDATION BEFORE SPEAKING (MANDATORY INTERNAL CHECK)
--------------------------------------------------

For each planet:
- Does spoken sign match transit.sign_index?
- Does spoken house match transit.transit_house?
- Is retrograde explicitly proven in JSON?
- Is any planetary claim absent in JSON?

If any answer is NO → You must correct before responding.

--------------------------------------------------
ABSOLUTE FAILURE CONDITION
--------------------------------------------------

If you cannot fully comply with these laws,
you MUST reduce output and speak minimally
ONLY using verified JSON data.

==================================================
END ZERO-HALLUCINATION LOCK
==================================================
""" + RISHI_NARRATIVE_REFINEMENT_PROMPT


router = APIRouter()


class BirthDetails(BaseModel):
    name: str = "Seeker"
    dob: str
    time: str
    lat: float
    lon: float
    timezone: str = "Asia/Kolkata"


class PredictRequest(BaseModel):
    birth_details: BirthDetails
    timescale: str = "daily"
    calculation_date: Optional[str] = None


def predict(birth_details: Dict[str, Any], timescale: str = "daily", calculation_date_override: Optional[str] = None) -> Dict[str, Any]:
    """
    Standalone prediction: build Guru Context and call AI.
    """
    tz = pytz.timezone(birth_details.get("timezone", "Asia/Kolkata"))
    if calculation_date_override:
        calculation_date = datetime.fromisoformat(calculation_date_override)
    else:
        calculation_now = datetime.now(tz)
        calculation_date = calculation_now.replace(tzinfo=None) if calculation_now.tzinfo else calculation_now

    context = build_guru_context(
        birth_details,
        timescale=timescale,
        calculation_date=calculation_date,
    )

    ai_context = json.loads(json.dumps(context))
    timezone = birth_details.get("timezone", "Asia/Kolkata")
    if timescale == "daily":
        events = context.get("transit_events")
        if events:
            ai_context["transit_events"] = events
        calc_noon = calculation_date.replace(hour=12, minute=0, second=0, microsecond=0)
        tz_calc = local_to_utc(calc_noon, timezone)
        transit_jd = get_julian_day(tz_calc)
        monthly_shifts = _monthly_planet_shifts(calculation_date, timezone, transit_jd)
        yearly_shifts = _yearly_planet_shifts(calculation_date, timezone, transit_jd)
        ai_context["monthly_transits"] = monthly_shifts if monthly_shifts else []
        ai_context["yearly_transits"] = yearly_shifts if yearly_shifts else []
    if timescale == "monthly":
        shifts = context.get("monthly_transits")
        if shifts:
            ai_context["monthly_transits"] = shifts
    if timescale == "yearly":
        yearly_shifts = context.get("yearly_transits")
        if yearly_shifts:
            ai_context["yearly_transits"] = yearly_shifts

    guidance = ""
    openai_key = getattr(settings, "openai_api_key", None)
    seeker_name = birth_details.get("name", "Seeker")
    context_json = json.dumps(ai_context, indent=2)

    # Backend-enforced transit declarations (daily only); deterministic structure
    declarations_block = ""
    allowed_retrograde_str = "None"
    allowed_retrograde_set_out = set()
    backend_declarations_section = ""
    if timescale == "daily":
        declarations_block, allowed_retrograde_set = _build_transit_declarations_and_retro(context)
        allowed_retrograde_set_out = allowed_retrograde_set
        allowed_retrograde_str = ", ".join(sorted(allowed_retrograde_set)) if allowed_retrograde_set else "None"
        if declarations_block:
            backend_declarations_section = f"""

BACKEND PLANETARY DECLARATIONS (FINAL — PREPENDED TO RESPONSE; DO NOT REWRITE OR REPEAT):
{declarations_block}

Your output must be ONLY the interpretive narrative. Do not output the above lines — they will be prepended automatically.

ALLOWED RETROGRADE PLANETS (use Retrograde/Vakri only for these): {allowed_retrograde_str}
"""
        else:
            backend_declarations_section = f"""

ALLOWED RETROGRADE PLANETS (use Retrograde/Vakri only for these): {allowed_retrograde_str}
"""
    else:
        backend_declarations_section = ""
        allowed_retrograde_str = "None"
        allowed_retrograde_set_out = set()

    if openai_key:
        try:
            client = LLMClient()
            if client.mode == "openai" and client.openai_client:
                # Structured flow for daily: LLM fills interpretation slots only, backend assembles
                use_structured = timescale == "daily" and declarations_block
                if use_structured:
                    severe = context.get("severe_stress", False)
                    moderate = context.get("moderate_stress", False)
                    remedy_note = f"REMEDY GATING: severe_stress={severe}, moderate_stress={moderate}. Obey these flags."
                    structured_prompt = f"""Seeker: {seeker_name}

Return ONLY a valid JSON object. No markdown, no code block, no other text.
Keys (all required, use empty string "" if no content): greeting, panchanga, dasha, chandra_bala, tara_bala, major_transits, dharmic_guidance, throne, moon_movement

{remedy_note}

greeting: MANDATORY Guru self-introduction. First 3–5 sentences. Address seeker by name. Establish chart examined. Convey planetary motion advises, not controls. Calm authority. No ego. Vary daily.
panchanga: From JSON only (tithi, nakshatra, vara, yoga, karana). No hallucination. Start with "On this sacred [tithi] of the [paksha]..." Max 6 sentences.
dasha: Mahadasha and Antardasha interpretation. Authority order.
chandra_bala: Moon strength from transit house. If Moon 8th from natal Moon → exact sentence "Do not initiate major ventures today."
tara_bala: If tara_category in Vipat/Naidhana/Pratyak: cautionary tone only; no optimism. Else brief influence.
major_transits: MANDATORY full planet coverage. Every planet in CURRENT SKY POSITION must appear. Order: Mahadasha first, Antardasha second, classical planets, Rahu, Ketu. Human narrative — no "Ruling the X house", no doctrinal terms. Contextual interpretation.
dharmic_guidance: 2 do's/don'ts, 1 Gita principle from context.gita. One classical maxim.
throne: "You were born under [Nakshatra]...". Dynamic daily line. If not activated: "Today, no transit planet activates your throne." If activated: planet name only.
moon_movement: If transit_events has Moon move, describe. Else "".

ALLOWED RETROGRADE: {allowed_retrograde_str}. Use retrograde words ONLY for these planets.
Use transit.sign_index and transit.transit_house from JSON. Never invent.

JSON CONTEXT:
{context_json}"""
                    try:
                        resp = client.openai_client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": GURU_SYSTEM_PROMPT + "\n\nReturn ONLY valid JSON. Keys: greeting, panchanga, dasha, chandra_bala, tara_bala, major_transits, dharmic_guidance, throne, moon_movement."},
                                {"role": "user", "content": structured_prompt},
                            ],
                            max_tokens=1200,
                            temperature=0,
                            response_format={"type": "json_object"},
                        )
                        raw = (resp.choices[0].message.content or "").strip()
                        # Strip markdown code blocks if present
                        if raw.startswith("```"):
                            raw = re.sub(r"^```(?:json)?\s*", "", raw)
                            raw = re.sub(r"\s*```$", "", raw)
                        parsed = json.loads(raw) if raw else {}
                        if isinstance(parsed, dict):
                            # Normalize keys: LLM may return Dharmic_guidance, dharmic guidance, etc
                            parsed = {k.lower().replace(" ", "_"): v for k, v in parsed.items()}
                            _, structured_out = _assemble_structured_output(
                                declarations_block, parsed, context, seeker_name
                            )
                            # Dharma lock: apply only to dharmic_guidance section
                            structured_out["dharmic_guidance"] = apply_dharma_graha_tone_to_section(
                                structured_out.get("dharmic_guidance") or "", context
                            )
                            # Rebuild guidance WITH canonical headings — never flat body
                            guidance = _build_guidance_with_structure(structured_out)
                            guidance = _strip_disallowed_retrograde(
                                guidance, allowed_retrograde_set_out
                            ) if allowed_retrograde_set_out else guidance
                            return {
                                "guidance": guidance,
                                "structured": structured_out,
                                "context": context,
                                "technical_breakdown": {
                                    "strength": context.get("strength", {}),
                                    "time": context.get("time", {}),
                                    "quality": context.get("quality", {}),
                                },
                            }
                    except (json.JSONDecodeError, KeyError, TypeError):
                        pass

                user_prompt = f"""Seeker Name: {seeker_name}

You must produce ONE seamless classical Daivajna daily prediction.
No headings.
No phase labels.
No monthly/yearly sections.
No motivational fluff.
No exaggerated positivity.
Flow as one sacred discourse.

Use ONLY the JSON below.
Never invent Panchanga.
Never guess retrograde.
Never compute house manually.
Use transit.sign_index and transit.transit_house exactly as given.
If data missing → skip silently.
{backend_declarations_section}
STRICT SIGN TABLE:
0 Aries (Mesha) 1 Taurus (Vrishabha) 2 Gemini (Mithuna) 3 Cancer (Karka)
4 Leo (Simha) 5 Virgo (Kanya) 6 Libra (Tula) 7 Scorpio (Vrischika)
8 Sagittarius (Dhanu) 9 Capricorn (Makara) 10 Aquarius (Kumbha) 11 Pisces (Meena)

==================================================
DAIVAJNA SUPREME DAILY ALGORITHM
==================================================

STEP 1 — PANCHANGA QUALITY FILTER (DAY NATURE)

If weekday exists:
• State weekday and ruling planet.
• If Lagna lord exists in JSON:
   - If Day Lord is natural enemy of Lagna Lord → tone reduces 1 level.
   - If friend → tone slightly supported.
   - If neutral → no modification.

If tithi exists:
• If Rikta (4,9,14) → restrict expansion tone.
• If Nanda/Purna → supportive tone.
• 1 sentence only.

If yoga exists:
• If malefic yoga (e.g., Vyaghata, Vaidhriti, Ganda type) → apply caution tone override.

If karana exists:
• If Vishti (Bhadra) → avoid risky actions.

If nakshatra exists:
• 1 sentence nature only.

If lunar_month exists:
• 1 short spiritual tone.

If samvatsara exists:
• 1 karmic rhythm line.

Max 6 sentences.

--------------------------------------------------

STEP 2 — AUTHORITY ORDER (ABSOLUTE ENFORCEMENT)

You MUST begin transit analysis with the Mahadasha Lord.

The FIRST planetary sentence in the entire transit section MUST be:

"[Mahadasha Lord] currently transits [Sign] in your [House] house."

If Mahadasha Lord exists in JSON and you fail to mention it → INVALID RESPONSE.

After Mahadasha, you MUST follow strict order:

1) Mahadasha Lord
2) Antardasha Lord
3) Moon, Day Lord, Jupiter, Saturn, Sun, Mars, Mercury, Venus (classical)
4) Rahu (if in transit)
5) Ketu (if in transit)

FULL PLANET COVERAGE: Every planet in CURRENT SKY POSITION must be interpreted exactly once. No skips. No repeats.
Rahu: classical only — obsession, material desire, distortion. Ketu: classical only — detachment, loss, renunciation. No "shadow self", no new-age phrasing.

You MUST NOT skip Mahadasha.
You MUST NOT mention Moon before Mahadasha.
You MUST NOT reorder.

You are forbidden from beginning planetary analysis with Moon or any planet other than the Mahadasha Lord.

PLANETARY INTERPRETATION LOCK (ABSOLUTE HARD ENFORCEMENT)

When backend declarations are prepended: Do NOT repeat them. Interpret each planet using format "In the Nth house, [Planet]…"

When no backend declarations: For EACH planet in transit JSON, produce EXACTLY ONE declaration sentence:
"[Planet] currently transits [Sign] in your [House] house."

You MUST interpret every planet present in transit JSON exactly once. No skips. No repeats.
Format: "In the Nth house, [Planet]…" — never repeat "Planet currently transits Sign in your Nth house" in the body.

Forbidden: "Saturn influences your 5th house" (vague). "Moon in Leo activates career" (omits house ordinal).
Required: "In the 10th house, Moon…" or interpretation that clearly links planet + house.

If a planet exists in transit JSON but has no interpretation → INVALID RESPONSE.

--------------------------------------------------

MOON ENFORCEMENT (NON-NEGOTIABLE)

If Moon exists in transit JSON:

You MUST include exactly one standalone sentence:

"Moon currently transits [Sign] in your [House] house."

OR

"Moon transits [Sign] in your [House] house."

If missing → INVALID RESPONSE.

--------------------------------------------------

MERCURY ENFORCEMENT (NON-NEGOTIABLE)

If Mercury exists in transit JSON:

You MUST include exactly one standalone sentence:

"Mercury currently transits [Sign] in your [House] house."

OR

"Mercury transits [Sign] in your [House] house."

If missing → INVALID RESPONSE.

--------------------------------------------------

For each planet (after sign and house):

• Use transit.dignity from JSON only (exalted, debilitated, own_sign, friendly, enemy, neutral). Never invent dignity.
• Mention bindu (≤1 = stress, 2–3 = moderate, ≥4 = strong).
• If JSON says is_combust true → strength reduced.
• If transit.avastha.modifier_suggestion exists, use that phrase only once per planet.
• Do NOT repeat the declaration line ("Planet currently transits ... house") in your interpretation—it appears only in CURRENT SKY POSITION.
• Always link: planet + house + dasha + bindu.

--------------------------------------------------

STEP 3 — CHANDRA BALA (MOON STRENGTH)

Using transit.transit_house of Moon:

1,3,6,7,10,11 → supportive.
4,8,12 → caution.

If Moon is 8th from natal Moon:
You MUST include exact sentence:
"Do not initiate major ventures today."

No softening.
No variation.

--------------------------------------------------

STEP 4 — TARA BALA (STRICT OVERRIDE)

If JSON provides tara_bala.tara_category:

If category = Vipat (3) or Naidhana (7):
• Override optimism.
• Reduce prediction strength.
• Avoid success language.

If category = Sampat, Sadhana, Parama Mitra:
• Mildly supportive tone.

If no tara data → skip.

--------------------------------------------------

STEP 5 — JUPITER FROM MOON RULE

If JSON allows Moon sign reference:

Check Jupiter's transit relative to natal Moon house:

If Jupiter in 2,5,7,9,11 from Moon:
• Add protection/support layer.

If in 3,6,8,12:
• Reduce expansion promise.

--------------------------------------------------

STEP 6 — SATURN FROM MOON RULE

If Saturn in 12,1,2 from natal Moon:
• Mention Sade Sati pressure (without fear tone).

If Saturn in 8th from natal Moon:
• Mention Ashtama Saturn discipline phase.

Only if JSON proves relative position.

--------------------------------------------------

STEP 7 — DASHA LORD BASELINE (NATAL ASPECT CHECK)

If JSON provides natal aspects on Mahadasha Lord:

• Saturn aspect → delay baseline.
• Mars aspect → conflict baseline.
• Rahu aspect → instability baseline.
• Jupiter aspect → protection baseline.

Transit aspects modify daily result.
Natal aspects define background tone.

--------------------------------------------------

STEP 8 — VEDHA CHECK (MOON OBSTRUCTION RULE)

If Jupiter is in a good Moon house
BUT a malefic occupies its vedha blocking house (if JSON provides):
• Reduce Jupiter's positive strength.

If no vedha data → skip silently.

--------------------------------------------------

STEP 9 — TRANSIT MOVEMENTS (INTEGRATED)

Use:

• transit_events
• monthly_transits
• yearly_transits

Format strictly:

On [DATE], [Planet] moves from
[OLD SIGN] in your [OLD HOUSE] house
to
[NEW SIGN] in your [NEW HOUSE] house.

If the prepended declaration sentence contains "(Retrograde)",
you may explain intensified internal karmic activation.
If it does not contain "(Retrograde)", you MUST NOT mention retrograde.

No "later this month/year".

--------------------------------------------------

STEP 10 — DHARMIC GUIDANCE

• 2 precise do's and don'ts tied to houses.
• 1 psychological discipline.
• 1 Gita principle: use context.gita.reference, context.gita.text, context.gita.relevance if present. Do not repeat same verse daily.
• 1 short classical maxim.

No fluff.
No overpromise.

--------------------------------------------------

STEP 11 — JANMA NAKSHATRA THRONE (STRICT 3–4 LINES)

1) "You were born under [Nakshatra] ([Pada])..."

2) Dynamic daily interpretation of throne—NOT static Nakshatra personality. Tie to today's transits and house themes.

3) Activation status:
If transit planet in same Nakshatra: name the activating planet(s) clearly.
If none: exact sentence "Today, no transit planet activates your throne."
If retrograde activation: "This is a Retrograde (Vakri) activation."

4) One short positive affirmation.

Max 4 lines.

--------------------------------------------------

INTERNAL VALIDATION (MANDATORY BEFORE OUTPUT)

Verify:
• Mahadasha mentioned before Moon.
• Every planet in transit JSON interpreted exactly once (full coverage).
• Chandrashtama exact sentence used if required.
• Retrograde used ONLY with JSON proof.
• Tara Vipat/Naidhana tone reduced.
• No invented Panchanga.
• No guessed houses.
• No fluff language.
• Rahu/Ketu: classical tone only (no shadow self, no new-age).

If violation detected → correct before responding.

==================================================

JSON CONTEXT:
{context_json}

Produce one seamless classical Daivajna daily prediction.
"""
                response = client.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": GURU_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    max_tokens=800,
                    temperature=0,
                )
                guidance = response.choices[0].message.content or ""
            else:
                guidance = "Guidance could not be generated (client not openai)."
        except Exception:
            guidance = "Guidance could not be generated. Use the technical breakdown below."
    else:
        guidance = "OPENAI_API_KEY not set"

    guidance = _apply_daily_moon_transit_override(context, timescale, guidance)
    # Backend-enforced declarations prepended (deterministic structure; no LLM dependence)
    if timescale == "daily" and declarations_block and guidance:
        guidance = _normalize_declaration_block(declarations_block) + "\n\n" + guidance.strip()
    elif timescale == "daily" and declarations_block:
        guidance = _normalize_declaration_block(declarations_block)
    if timescale == "daily" and allowed_retrograde_set_out is not None:
        guidance = _strip_disallowed_retrograde(guidance, allowed_retrograde_set_out)

    # Fallback: only when LLM failed (no valid guidance). Do not overwrite successful LLM output.
    llm_failed = (
        not guidance
        or "Guidance could not be generated" in (guidance or "")
        or "OPENAI_API_KEY not set" in (guidance or "")
    )
    if timescale == "daily" and declarations_block and llm_failed:
        placeholder = "Interpretation could not be generated. Full chart data is available in the context."
        fallback_structured: Dict[str, str] = {
            "greeting": f"{(seeker_name or 'Seeker').strip()}, the wheel of Time turns thus:",
            "declarations": _format_declarations_for_display(declarations_block),
            "panchanga": placeholder,
            "dasha": placeholder,
            "chandra_bala": placeholder,
            "tara_bala": placeholder,
            "major_transits": placeholder,
            "dharmic_guidance": placeholder,
            "throne": placeholder,
            "moon_movement": "No Moon sign change today." if not (context.get("transit_events") or []) else placeholder,
        }
        guidance = _build_guidance_with_structure(fallback_structured)
        return {
            "guidance": guidance,
            "structured": fallback_structured,
            "context": context,
            "technical_breakdown": {
                "strength": context.get("strength", {}),
                "time": context.get("time", {}),
                "quality": context.get("quality", {}),
            },
        }

    # Post-LLM validation and formatting layer (final transformation before return)
    if guidance:
        guidance = validate_and_format_guidance(guidance, context)

    return {
        "guidance": guidance,
        "context": context,
        "technical_breakdown": {
            "strength": context.get("strength", {}),
            "time": context.get("time", {}),
            "quality": context.get("quality", {}),
        },
    }


@router.post("/predict", response_model=Dict)
async def post_predict(request: PredictRequest):
    """
    POST /api/v1/predict — Daily/Monthly/Yearly AI guidance from Guru Context.
    """
    try:
        birth_dict = request.birth_details.model_dump()
        result = predict(
            birth_dict,
            timescale=request.timescale,
            calculation_date_override=request.calculation_date,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
