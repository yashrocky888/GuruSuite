import re
from typing import Dict, Any, List, Tuple

# Nakshatra span: 13°20' = 360/27 degrees
NAKSHATRA_SPAN = 360.0 / 27.0

STRICT_DECL_RE = re.compile(
    r"^(Mercury|Venus|Mars|Jupiter|Saturn|Sun|Moon|Rahu|Ketu)\s+currently\s+transits\s+.+?\s+in\s+your\s+\d+(?:st|nd|rd|th)\s+house\.(?:\s+\(Retrograde\))?$"
)
# Greeting: "Name, on this X of the Y Paksha, the wheel of Time turns thus:" or "Name, the wheel of Time turns thus:"
GREETING_RE = re.compile(
    r"^(.+,\s*(?:on this \S+ of the \S+ Paksha,\s*)?the wheel of Time turns thus:)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
PLANET_DECL_START = re.compile(
    r"(?=(Mercury|Venus|Mars|Jupiter|Saturn|Sun|Moon|Rahu|Ketu)\s+currently\s+transits)",
    re.IGNORECASE,
)


def _normalize_declaration_block(block: str) -> str:
    """Ensure one planet per line. No inline stacking."""
    if not block or not block.strip():
        return block.strip()
    parts = PLANET_DECL_START.split(block)
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


def split_sections(guidance: str) -> Tuple[str, str]:
    """
    Split declaration block from body.
    Declaration block = strict transit lines only.
    """
    lines = guidance.strip().splitlines()
    decl_lines = []
    body_lines = []

    for line in lines:
        stripped = line.strip()
        if STRICT_DECL_RE.match(stripped):
            decl_lines.append(stripped)
        else:
            body_lines.append(line)

    return "\n".join(decl_lines), "\n".join(body_lines).strip()


def normalize_whitespace(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def ensure_closed_quotes(text: str) -> str:
    if text.count('"') % 2 != 0:
        text += '"'
    return text


# Layer 11 — Anti-Leak Sanitizer: remove doctrinal vocabulary from output
DOCTRINAL_LEAK_PATTERNS = [
    (r"\bdusthana\b", "challenging house"),
    (r"\bkendra\b", "prominent house"),
    (r"\btrikona\b", "auspicious house"),
    (r"\bbindu\b", "planetary support"),
    (r"\blow_bindu\b", "limited support"),
    (r"\bstructural support\b", "support"),
    (r"\bexpansion language\b", "optimistic phrasing"),
    (r"\blordship function\b", "influence"),
    (r"\byields mixed results\b", "carries both benefit and cost"),
    (r"\brestrict expansion\b", "measure growth"),
    (r"\bshadbala\b", "planetary strength"),
    (r"[Aa]s lord of\b", "Governing"),
]


def apply_anti_leak_sanitizer(text: str) -> str:
    """
    Layer 11 — Remove doctrinal vocabulary before output.
    Rewrites engine language into humanized equivalents.
    """
    if not text or not text.strip():
        return text
    result = text
    for pattern, replacement in DOCTRINAL_LEAK_PATTERNS:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result


def enforce_section_order(body: str, context: Dict[str, Any]) -> str:
    """
    Ensure strict section order:
    1) Panchanga invocation
    2) Mahadasha/Dasha block
    3) Transit interpretation (Mahadasha lord first)
    4) Chandrashtama warning (if present)
    5) Dharmic guidance (ULTRA-TIGHT: replaced with canonical block)
    6) Throne section
    7) Backend Moon movement block
    """
    sections: Dict[str, str] = {
        "invocation": "",
        "dasha": "",
        "transit": "",
        "chandra": "",
        "guidance": "",
        "throne": "",
        "moon_move": "",
    }

    paragraphs = body.split("\n\n") if body else []

    for p in paragraphs:
        if not p.strip():
            continue
        lower = p.lower()
        if lower.startswith("later today, the moon moves"):
            sections["moon_move"] = p
        elif "on this sacred" in lower:
            sections["invocation"] = p
        elif "you were born under" in lower:
            sections["throne"] = p
        elif "do not initiate major ventures today" in lower:
            sections["chandra"] += p + "\n\n"
        elif "mahadasha" in lower or "antardasha" in lower:
            sections["dasha"] += p + "\n\n"
        elif "currently transits" in lower:
            sections["transit"] += p + "\n\n"
        else:
            sections["guidance"] += p + "\n\n"

    # ULTRA-TIGHT DHARMA: Replace guidance section with canonical block
    sections["guidance"] = _enforce_dharma_authority(sections["guidance"], context)

    ordered: list[str] = []
    if sections["invocation"]:
        ordered.append(sections["invocation"])
    if sections["dasha"]:
        ordered.append(sections["dasha"].strip())
    if sections["transit"]:
        # Within transit section, ensure Mahadasha lord interpretation appears first if present
        transit_paragraphs = [p for p in sections["transit"].split("\n\n") if p.strip()]
        mahadasha_lord = (context.get("time", {}) or {}).get("mahadasha_lord", "")
        mahadasha_lower = str(mahadasha_lord).strip().lower()
        md_paras = []
        other_paras = []
        for p in transit_paragraphs:
            if mahadasha_lower and mahadasha_lower in p.lower():
                md_paras.append(p)
            else:
                other_paras.append(p)
        ordered_transit = md_paras + other_paras
        if ordered_transit:
            ordered.append("\n\n".join(ordered_transit))
    if sections["chandra"]:
        ordered.append(sections["chandra"].strip())
    if sections["guidance"]:
        ordered.append(sections["guidance"].strip())
    if sections["throne"]:
        ordered.append(sections["throne"])
    if sections["moon_move"]:
        ordered.append(sections["moon_move"])

    return "\n\n".join(ordered)


def _nakshatra_index(longitude: float) -> int:
    """Nakshatra index 0-26 from longitude (0-360)."""
    lon = longitude % 360.0
    return int(lon / NAKSHATRA_SPAN) % 27


def is_throne_activated(context: Dict[str, Any]) -> bool:
    """
    Janma Nakshatra is activated ONLY IF:
    1. Any transit planet longitude lies inside the Janma Nakshatra span (13°20' block), OR
    2. The Mahadasha lord is transiting inside that same Nakshatra span.
    No symbolic, poetic, or soft activation.
    """
    return len(get_activating_planets(context)) > 0


def get_activating_planets(context: Dict[str, Any]) -> List[str]:
    """
    Return list of planet names that activate the throne (in Janma Nakshatra).
    Empty if not activated.
    """
    janma = context.get("janma_nakshatra") or {}
    janma_deg = janma.get("degree")
    if janma_deg is None:
        return []
    janma_idx = _nakshatra_index(float(janma_deg))

    transit = context.get("transit") or {}
    time_block = context.get("time") or {}
    md_lord = (time_block.get("mahadasha_lord") or "").strip()
    activating: List[str] = []

    for pname, pdata in transit.items():
        if not isinstance(pdata, dict):
            continue
        deg = pdata.get("degree")
        if deg is None:
            continue
        if _nakshatra_index(float(deg)) == janma_idx:
            activating.append(pname)

    if md_lord and md_lord in transit and md_lord not in activating:
        pdata = transit.get(md_lord, {})
        if isinstance(pdata, dict):
            deg = pdata.get("degree")
            if deg is not None and _nakshatra_index(float(deg)) == janma_idx:
                activating.append(md_lord)

    return activating


# Patterns that indicate false throne activation (replace with correct sentence)
# Match: "X is currently activated", "X is activated", "X activates your throne", etc.
_THRONE_FALSE_ACTIVATION_RE = re.compile(
    r"[^.]*(?:\b[A-Za-z]+\s+is\s+(?:currently\s+)?activated\b|\b(?:Your\s+throne\s+is\s+activated|[A-Za-z]+\s+activates\s+your\s+throne|Throne\s+activated)\b)[^.]*\.?",
    re.IGNORECASE,
)

_NO_ACTIVATION_SENTENCE = "Today, no transit planet activates your throne."
_NO_ACTIVATION_FULL = "Today, no transit planet activates your throne. Preserve your natal strength. Do not spend your authority where it is not required."


def get_canonical_throne(context: Dict[str, Any]) -> str:
    """
    Return canonical throne text for structured output. Always includes Nakshatra intro.
    """
    activating = get_activating_planets(context)
    janma = context.get("janma_nakshatra") or {}
    nak_name = (janma.get("name") or "").strip() or "your birth star"
    pada = janma.get("pada", 1)
    intro = f"You were born under {nak_name} (Pada {pada}). "
    if not activating:
        return intro + _NO_ACTIVATION_FULL
    planet_names = ", ".join(activating)
    return intro + f"Today, {planet_names} activates your throne."


def enforce_throne_activation(body: str, context: Dict[str, Any]) -> str:
    """
    Full LLM synthesis — no deterministic throne replacement.
    LLM generates throne section.
    """
    return body


# Tara override: Vipat, Naidhana, Pratyak → prohibit optimistic language.
TARA_CAUTION_CATEGORIES = ("Vipat", "Naidhana", "Pratyak")
FLUFF_POSITIVE = re.compile(
    r"\b(great opportunity|excellent day|success likely|amazing|fantastic|incredible|wonderful day|perfect time|highly favorable)\b",
    re.IGNORECASE,
)
CHANDRA_MANDATORY = "Do not initiate major ventures today."
MALEFIC_MAHADASHA = ("Saturn", "Mars", "Sun", "Rahu")


def _apply_tara_override(body: str, context: Dict[str, Any]) -> str:
    """If tara_category in Vipat/Naidhana/Pratyak: force cautionary tone; strip optimistic phrases."""
    tara = context.get("tara_bala") or {}
    if isinstance(tara, dict):
        cat = (tara.get("tara_category") or "").strip()
    else:
        cat = ""
    if cat not in TARA_CAUTION_CATEGORIES:
        return body
    body = FLUFF_POSITIVE.sub("", body)
    return normalize_whitespace(body)


def _enforce_chandra_bala(body: str, context: Dict[str, Any]) -> str:
    """Chandra Bala authority lock: If Moon in 8th from natal Moon, mandatory exact sentence. No variation."""
    transit = context.get("transit") or {}
    moon_data = transit.get("Moon")
    if not isinstance(moon_data, dict):
        return body
    house_from_moon = moon_data.get("house_from_moon")
    if house_from_moon != 8:
        return body
    if CHANDRA_MANDATORY.lower() in body.lower():
        return body
    paragraphs = body.split("\n\n")
    for i, p in enumerate(paragraphs):
        if "mahadasha" in p.lower() or "antardasha" in p.lower():
            paragraphs.insert(i, CHANDRA_MANDATORY)
            break
        if "on this sacred" in p.lower():
            paragraphs.insert(i + 1, CHANDRA_MANDATORY)
            break
    else:
        paragraphs.insert(0, CHANDRA_MANDATORY)
    return "\n\n".join(paragraphs)


def _fix_avastha_grammar(body: str) -> str:
    """Canonical grammar: 'Planet modifier' → 'Planet. Modifier' (complete sentences)."""
    planets = r"(Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn)"
    for raw, canonical in [
        ("strength amplified", "Strength amplified."),
        ("expression restrained", "Expression restrained."),
        ("results manifest externally", "Results manifest externally."),
        ("results fluctuate", "Results fluctuate."),
        ("results internalized", "Results internalized."),
    ]:
        # Match optional trailing period to avoid double period
        body = re.sub(
            rf"(\b{planets})\s+{re.escape(raw)}\.?",
            rf"\1. {canonical}",
            body,
            flags=re.IGNORECASE,
        )
    return body


# Dharma tone: one contextual line per dominant graha (Mahadasha lord)
DHARMA_GRAHA_LINES = {
    "Saturn": "Restraint preserves power.",
    "Mars": "Control action before action controls you.",
    "Rahu": "Desire must be mastered.",
    "Ketu": "Detachment clarifies destiny.",
    "Jupiter": "Wisdom governs action.",
    "Venus": "Harmony requires discipline.",
    "Mercury": "Speech must be precise.",
    "Sun": "Authority must be righteous.",
    "Moon": "Emotion must be steady.",
}

# Ultra-tight Dharma: deterministic graha principle (Guru cadence)
DHARMA_GRAHA_PRINCIPLE = {
    "Sun": "Authority must serve righteousness.",
    "Moon": "Emotion must remain steady.",
    "Mars": "Control action before action controls you.",
    "Mercury": "Speech shapes destiny; choose words carefully.",
    "Jupiter": "Wisdom must guide expansion.",
    "Venus": "Harmony without discipline collapses. Discipline without compassion hardens.",
    "Saturn": "Restraint preserves power; impatience weakens it.",
    "Rahu": "Desire must be mastered before it masters you.",
    "Ketu": "Detachment reveals what attachment hides.",
}

# Gita verse by graha: (chapter, verse) — never random
DHARMA_GITA_VERSE = {
    "Sun": (3, 21),
    "Moon": (6, 26),
    "Mars": (2, 63),
    "Mercury": (17, 15),
    "Jupiter": (4, 38),
    "Venus": (5, 10),
    "Saturn": (2, 47),
    "Rahu": (3, 39),
    "Ketu": (6, 1),
}

DHARMA_CLOSING = "Act with awareness. The fruit will follow."


def _enforce_dharma_authority(section_text: str, context: Dict[str, Any]) -> str:
    """
    Full LLM synthesis — no deterministic dharma replacement.
    Return section as-is. LLM generates dharma.
    """
    return section_text


def _replace_dharma_paragraphs_in_body(body: str, context: Dict[str, Any]) -> str:
    """
    After Tara override, before Throne: replace dharma-like paragraphs with canonical block.
    """
    if not body or not body.strip():
        return body
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    if not paragraphs:
        return body
    canonical = _enforce_dharma_authority("", context)
    result = []
    dharmas_replaced = False
    for p in paragraphs:
        lower = p.lower()
        is_dharma = (
            re.match(r"^Do\s", p) or re.match(r"^Don'?t\s", p)
            or lower.startswith("remember")
            or "patience" in lower
            or "classical maxim" in lower
            or "the gita advises" in lower
        )
        if is_dharma:
            if not dharmas_replaced:
                result.append(canonical)
                dharmas_replaced = True
        else:
            result.append(p)
    return "\n\n".join(result) if result else body


def _apply_dharma_graha_tone(body: str, context: Dict[str, Any]) -> str:
    """Replace motivational proverbs with one graha-based classical line. Hard lock: no generic Dharma."""
    time_block = context.get("time") or {}
    mahadasha = (time_block.get("mahadasha_lord") or "").strip()
    repl_line = DHARMA_GRAHA_LINES.get(mahadasha, "Restraint preserves power.")
    # Remove generic phrases; replace with graha-based line
    for pat in [
        r"Patience is a virtue\.?",
        r"Patience is the key to joy\.?",
        r"Patience is the companion of wisdom\.?",
    ]:
        body = re.sub(pat, repl_line, body, flags=re.IGNORECASE)
    # Strip motivational filler; replace with classical alternatives
    body = re.sub(r"\bRemember,?\s+[^.]*\.", repl_line, body, flags=re.IGNORECASE)
    body = re.sub(r"The Gita advises:?\s*[^.]*\.", repl_line, body, flags=re.IGNORECASE)
    body = re.sub(r"Do focus on\s+[^.]*\.", "Act after reflection.", body, flags=re.IGNORECASE)
    body = re.sub(r"Do not engage in\s+[^.]*\.", "Avoid haste.", body, flags=re.IGNORECASE)
    return body


def apply_dharma_graha_tone_to_section(text: str, context: Dict[str, Any]) -> str:
    """
    ULTRA-TIGHT: Replace entire Dharma section with canonical block.
    Used for structured dharmic_guidance. Ignores input; returns deterministic 3-line block.
    """
    return _enforce_dharma_authority(text or "", context)


def _apply_mahabharata_cadence(body: str, context: Dict[str, Any]) -> str:
    """Classical gravity. Ancient Daiva-Jña tone. No drama, no motivation."""
    replacements = [
        (r"Focus on clear communication\.\s*Don't rush into new partnerships\.", "Guard your speech. Act after reflection, not impulse."),
        (r"Avoid taking unnecessary risks\.", "Step carefully where destiny tests resolve."),
        # Dasha openings: Rahu/Ketu first (specific), then Mercury+Venus, then generic
        (r"Under the influence of Rahu Mahadasha[^.]*\.", "In this Rahu Mahadasha, destiny accelerates through desire and ambition."),
        (r"Under the influence of Ketu Mahadasha[^.]*\.", "In this Ketu Mahadasha, destiny withdraws through detachment and inner severance."),
        (r"Under the influence of Mercury Mahadasha and Venus Antardasha[^.]*\.", "In this period of Mercury Mahadasha and Venus Antardasha, the current of destiny flows through intellect and relationship."),
        (r"Under the influence of (\w+) Mahadasha and (\w+) Antardasha[^.]*\.", r"In this period of \1 Mahadasha and \2 Antardasha, the current of destiny flows through the planetary influences of this period."),
    ]
    for pat, repl in replacements:
        body = re.sub(pat, repl, body, flags=re.IGNORECASE)
    return body


def _apply_rahu_ketu_dasha_authority(body: str, context: Dict[str, Any]) -> str:
    """Rahu/Ketu Mahadasha tone override. Deterministic. No poetic exaggeration."""
    time_block = context.get("time") or {}
    mahadasha = (time_block.get("mahadasha_lord") or "").strip()
    if mahadasha == "Rahu":
        body = body.replace("Mahadasha", "Mahadasha (shadow amplification phase)")
        body += "\n\nRahu intensifies desire, ambition, and karmic acceleration. Obsession must be controlled; illusion must be pierced."
    if mahadasha == "Ketu":
        body = body.replace("Mahadasha", "Mahadasha (detachment and karmic severance phase)")
        body += "\n\nKetu dissolves attachment and forces inner clarity. Loss becomes purification; separation becomes liberation."
    if mahadasha in ("Rahu", "Ketu"):
        transit = context.get("transit") or {}
        md_data = transit.get(mahadasha)
        if isinstance(md_data, dict):
            nl = md_data.get("nakshatra_lord")
            if nl:
                body += f"\n\nThe Dasha operates through the influence of {nl}, whose nature colors the karmic unfolding."
    return body


def _strip_fluff_tone(body: str, context: Dict[str, Any]) -> str:
    """No motivational fluff, no exaggerated positivity, no fear-mongering. Balanced classical tone."""
    fluff = re.compile(
        r"\b(amazing|fantastic|incredible|life.?changing|great opportunity|positive vibes|fear not|do not fear|terrible|disaster|catastrophe)\b",
        re.IGNORECASE,
    )
    body = fluff.sub("", body)
    time_block = context.get("time") or {}
    md = (time_block.get("mahadasha_lord") or "").strip()
    if md in MALEFIC_MAHADASHA:
        body = FLUFF_POSITIVE.sub("", body)
    return normalize_whitespace(body)


def validate_shadbala_usage(body: str, context: Dict[str, Any]) -> str:
    """
    Ensure strength statements align with actual Shadbala ranking.
    If planet marked weak in text but strong in context → remove that sentence.
    """
    strength = context.get("strength", {}) or {}
    for planet, pdata in strength.items():
        if isinstance(pdata, dict):
            virupas = pdata.get("virupas", 0)
            if virupas >= 450:
                # Remove sentences that explicitly call this planet "weak"
                body = re.sub(
                    rf"{re.escape(planet)}.*weak.*?\.",
                    "",
                    body,
                    flags=re.IGNORECASE | re.DOTALL,
                )
    return body


def _extract_greeting(text: str) -> Tuple[str, str]:
    """Extract greeting line if present. Return (greeting, rest)."""
    if not text or not text.strip():
        return "", text
    paragraphs = text.split("\n\n")
    for i, p in enumerate(paragraphs):
        stripped = p.strip()
        if GREETING_RE.match(stripped):
            rest = "\n\n".join(paragraphs[i + 1 :]).strip()
            return stripped, rest
    return "", text


def validate_and_format_guidance(guidance: str, context: Dict[str, Any]) -> str:
    """
    Post-LLM validation and formatting:
    - Preserve greeting FIRST, then declarations, then body
    - Force post-processor on full guidance (no early return bypass)
    - Dharma graha override, throne intro, remove motivational filler
    """
    if not guidance:
        return guidance

    decl_block, body = split_sections(guidance)

    # Extract greeting so it stays FIRST in final output
    greeting, body_no_greeting = _extract_greeting(body)

    # Remove only exact duplicate declaration lines (strict match)
    body_lines = []
    for line in body_no_greeting.splitlines():
        stripped = line.strip()
        if stripped and STRICT_DECL_RE.match(stripped):
            continue
        body_lines.append(line)
    body = "\n".join(body_lines).strip()
    body = normalize_whitespace(body)

    body = ensure_closed_quotes(body)
    body = validate_shadbala_usage(body, context)
    body = _fix_avastha_grammar(body)
    body = _apply_tara_override(body, context)
    body = _replace_dharma_paragraphs_in_body(body, context)  # ULTRA-TIGHT: after Tara, before Throne
    body = _enforce_chandra_bala(body, context)
    body = _apply_rahu_ketu_dasha_authority(body, context)
    body = _apply_mahabharata_cadence(body, context)
    body = enforce_throne_activation(body, context)
    body = enforce_section_order(body, context)
    body = _strip_fluff_tone(body, context)
    body = normalize_whitespace(body)

    # Final order: greeting → declarations → body (SYNC LOCK)
    parts = []
    if greeting:
        parts.append(greeting)
    if decl_block:
        parts.append(_normalize_declaration_block(decl_block))
    if body:
        parts.append(body)
    final = "\n\n".join(parts).strip()

    # Layer 11 — Anti-Leak Sanitizer (final pass)
    final = apply_anti_leak_sanitizer(final)

    return final.strip()

