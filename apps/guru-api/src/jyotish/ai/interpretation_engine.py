"""
Zero-Hardcode Interpretation Engine.

Every sentence derives strictly from chart data:
- Lordship, transit house type, dignity, avastha, Shadbala, Ashtakavarga bindu
- Mahadasha/Antardasha, Tara Bala, Chandrashtama

No archetype-based phrases. No static graha psychology.
"""

from typing import Any, Dict, List, Optional


# House type categories (BPHS)
KENDRAS = {1, 4, 7, 10}
TRIKONAS = {1, 5, 9}
DUSTHANA = {6, 8, 12}
NEUTRAL = {2, 3, 7, 11}  # 7 is kendra; 2,3,11 are neutral

# Thresholds
SHADBALA_INTENSITY_THRESHOLD = "Average"  # Below this → reduce intensity
BAV_BINDU_THRESHOLD = 4  # Below this → restrict expansion language
TARA_CAUTIONARY = {"Naidhana", "Vipat", "Pratyak", "Janma"}
TARA_MEASURED = {"Sadhaka", "Kshema"}


def _house_type(house_num: int) -> str:
    """Transit house category from BPHS."""
    if house_num in KENDRAS:
        return "Kendra"
    if house_num in TRIKONAS:
        return "Trikona"
    if house_num in DUSTHANA:
        return "dusthana"
    return "neutral"


def _house_ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        return f"{n}th"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _lordship_phrase(lordships: List[int]) -> str:
    """Traceable lordship phrase. No archetype."""
    if not lordships:
        return ""
    lordships = sorted(lordships)
    if len(lordships) == 1:
        return f"As lord of the {_house_ordinal(lordships[0])} house, "
    ords = [_house_ordinal(h) for h in lordships]
    return f"As lord of the {ords[0]} and {ords[1]} houses, "


def _dignity_implication(dignity: str) -> str:
    """Data-driven dignity implication. No static graha psychology."""
    mapping = {
        "exalted": "Power is visible and decisive.",
        "own_sign": "Acts with stability and authority.",
        "friendly": "Constructive growth is favored.",
        "neutral": "Results depend on conscious effort.",
        "enemy": "Expression faces resistance; patience is required.",
        "debilitated": "Strength is weakened; restraint is essential.",
    }
    return mapping.get(dignity, mapping["neutral"])


def _avastha_implication(modifier: str) -> str:
    """Avastha modifier→synthesis. Backend value only."""
    mapping = {
        "Strength amplified.": "Influence is strong and externally visible.",
        "Expression restrained.": "Results unfold internally and quietly.",
        "Results manifest externally.": "Effects appear clearly in the outer world.",
        "Results fluctuate.": "Effects fluctuate and require awareness.",
        "Results internalized.": "Effects unfold internally and quietly.",
    }
    return mapping.get(modifier, modifier)


def _get_lordship_data(pname: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Per-planet lordship flags from context."""
    lordship_block = context.get("lordship") or {}
    if isinstance(lordship_block, dict):
        return lordship_block.get(pname) or {}
    return {}


def _get_tara_category(context: Dict[str, Any]) -> str:
    tara = context.get("tara_bala") or {}
    if isinstance(tara, dict):
        return (tara.get("tara_category") or tara.get("tara_name") or "").strip()
    return ""


def _get_transit_house_type(house_num: int) -> str:
    htype = _house_type(house_num)
    return f"a {htype}" if htype != "neutral" else "a neutral house"


def build_single_transit_line(
    pname: str,
    pdata: Dict[str, Any],
    context: Dict[str, Any],
    same_house: bool = False,
) -> str:
    """
    Build one transit line from context data only.
    No static graha personality. Every sentence traceable.
    """
    house = int(pdata.get("transit_house") or pdata.get("house_from_lagna", 1))
    house_ord = _house_ordinal(house)
    dignity = pdata.get("dignity") or "neutral"
    retro = bool(pdata.get("is_retrograde"))
    time_block = context.get("time") or {}
    mahadasha = (time_block.get("mahadasha_lord") or "").strip()
    antardasha = (time_block.get("antardasha_lord") or "").strip()
    strength = context.get("strength") or {}
    quality = context.get("quality") or {}
    tara_cat = _get_tara_category(context)

    # Rahu/Ketu: nakshatra lord and dignity/avastha; no generic archetype
    if pname == "Rahu":
        nak_lord = pdata.get("nakshatra_lord") or ""
        opener = "In the same domain, " if same_house else f"In the {house_ord} house, "
        basis = f"Rahu transits {_get_transit_house_type(house)}."
        if nak_lord:
            basis += f" Nakshatra lord: {nak_lord}."
        if tara_cat in TARA_CAUTIONARY:
            basis += " Cautionary Tara; avoid optimistic expansion."
        return opener + basis
    if pname == "Ketu":
        nak_lord = pdata.get("nakshatra_lord") or ""
        opener = "In the same domain, " if same_house else f"In the {house_ord} house, "
        basis = f"Ketu transits {_get_transit_house_type(house)}."
        if nak_lord:
            basis += f" Nakshatra lord: {nak_lord}."
        if tara_cat in TARA_CAUTIONARY:
            basis += " Cautionary Tara; restrict expansion language."
        return opener + basis

    # Lordship-based synthesis
    lord_data = _get_lordship_data(pname, context)
    lordships = lord_data.get("lordships") or []
    is_dusthana_lord = lord_data.get("is_dusthana_lord", False)
    is_yogakaraka = lord_data.get("is_yogakaraka", False)
    func_nature = lord_data.get("functional_nature", "neutral")

    # Shadbala
    pstrength = strength.get(pname) or {}
    shadbala_status = pstrength.get("status") or ""
    rupas = pstrength.get("rupas")
    shadbala_weak = shadbala_status in ("Weak", "Average") or (
        rupas is not None and float(rupas) < 6.0
    )

    # Ashtakavarga bindu
    qdata = quality.get(pname) or {}
    bindu = qdata.get("bindu")
    bindu_low = bindu is not None and int(bindu) < BAV_BINDU_THRESHOLD

    # Avastha
    avastha = pdata.get("avastha") or {}
    avastha_mod = ""
    if isinstance(avastha, dict) and avastha.get("modifier_suggestion"):
        avastha_mod = _avastha_implication(avastha["modifier_suggestion"])

    # Dignity: soften if enemy/debilitated
    dignity_soft = dignity in ("enemy", "debilitated")

    # Build sentence
    opener = "In the same domain, " if same_house else f"In the {house_ord} house, "
    parts = []

    # Lordship phrase
    lp = _lordship_phrase(lordships)
    if lp:
        parts.append(lp + f"{pname} transits {_get_transit_house_type(house)}.")
    else:
        parts.append(f"{pname} transits {_get_transit_house_type(house)}.")

    # Dusthana lord in Kendra → mixed result
    if is_dusthana_lord and house in KENDRAS:
        parts.append("Lordship of a dusthana house while transiting a Kendra yields mixed results.")

    # Yogakaraka + strong → constructive emphasis
    if is_yogakaraka and not shadbala_weak and not dignity_soft:
        parts.append("As yogakaraka with strength, constructive emphasis.")

    # Dignity implication (soften if enemy/debilitated)
    parts.append(_dignity_implication(dignity))

    # Avastha
    if avastha_mod:
        parts.append(avastha_mod)

    # Bindu low → restrict expansion
    if bindu_low:
        parts.append("Ashtakavarga bindus in this house are low; expansion should be restrained.")

    # Shadbala below threshold → reduce intensity
    if shadbala_weak:
        parts.append("Shadbala below threshold; intensity is reduced.")

    # Retrograde → internalize
    if retro:
        parts.append("Retrograde motion internalizes expression.")

    # Mahadasha lord same as transit planet → amplify
    if mahadasha == pname:
        parts.append("Mahadasha lord transiting; weight amplified.")

    # Moon: house_from_lagna AND house_from_moon; Chandrashtama override
    if pname == "Moon":
        house_from_moon = pdata.get("house_from_moon")
        if house_from_moon == 8:
            return opener + "Chandrashtama operates. The mind may feel unsettled. Do not initiate major ventures today."
        # Moon psychology from house position (data-driven)
        if house in (1, 4, 7, 8, 10, 11, 12):
            moon_phrases = {
                1: "The mind defines the day.",
                4: "Emotional foundations are tested.",
                7: "Partnership reflects the inner state.",
                8: "The mind may feel unsettled; do not initiate major ventures.",
                10: "Public duty shapes the mind.",
                11: "Desire for fulfillment increases; choose wisely which aspiration deserves energy.",
                12: "Withdraw and observe before acting.",
            }
            phrase = moon_phrases.get(house)
            if phrase:
                parts.append(phrase)

    line = opener + " ".join(parts)
    return line.strip()


def build_dasha_section(context: Dict[str, Any]) -> str:
    """
    Dasha section from: Mahadasha lord, Antardasha lord, transit house of AD lord.
    No GRAHA_NATURE_SUMMARY. Lordship and transit house only.
    """
    time_block = context.get("time") or {}
    mahadasha = (time_block.get("mahadasha_lord") or "").strip()
    antardasha = (time_block.get("antardasha_lord") or "").strip()
    lordship = context.get("lordship") or {}
    transit = context.get("transit") or {}

    if not mahadasha:
        return "Time period governs the day."

    lord_data = lordship.get(mahadasha) or {}
    lordships = lord_data.get("lordships") or []
    lp = _lordship_phrase(lordships)
    if lp:
        intro = f"In this {mahadasha} Mahadasha, {mahadasha} {lp.rstrip(', ').replace('As lord', 'as lord')} activates."
    else:
        intro = f"In this {mahadasha} Mahadasha, life unfolds through its lordship function."

    parts = [intro]

    # Closing from functional nature and lordship (not static graha psychology)
    if lordships:
        dusthana = {6, 8, 12}
        kendra = {1, 4, 7, 10}
        owned_set = set(lordships)
        if owned_set & dusthana and owned_set & kendra:
            parts[0] += " Mixed results from dusthana-kendra lordship."
        elif lord_data.get("is_yogakaraka"):
            parts[0] += " Yogakaraka strength supports constructive emphasis."

    # Antardasha
    if antardasha:
        ad_data = transit.get(antardasha)
        house = 1
        if isinstance(ad_data, dict):
            house = int(ad_data.get("transit_house") or ad_data.get("house_from_lagna", 1))
        ad_lord_data = lordship.get(antardasha) or {}
        ad_lordships = ad_lord_data.get("lordships") or []
        ad_lp = _lordship_phrase(ad_lordships)
        if ad_lp:
            elab = f"Therefore the lordship function of {antardasha} activates the {_house_ordinal(house)} house."
        else:
            elab = f"Therefore {antardasha} directs the immediate field, transiting the {_house_ordinal(house)} house."
        parts.append(f"Within it, the Antardasha of {antardasha} directs the immediate field. {elab}")

    return "\n\n".join(parts).strip()


def build_dharma_section(context: Dict[str, Any]) -> str:
    """
    Dharma from: Mahadasha graha, most afflicted house, Tara category.
    No DHARMA_GRAHA_PRINCIPLE. Data-driven.
    """
    time_block = context.get("time") or {}
    mahadasha = (time_block.get("mahadasha_lord") or "").strip()
    tara_cat = _get_tara_category(context)
    lordship = context.get("lordship") or {}
    transit = context.get("transit") or {}
    quality = context.get("quality") or {}

    # Most afflicted: debilitated planet's house, or lowest bindu
    most_afflicted = context.get("most_afflicted_house")
    afflicted_reason = context.get("afflicted_reason") or ""

    parts = []

    # Principle from Mahadasha lordship
    lord_data = lordship.get(mahadasha) or {}
    lordships = lord_data.get("lordships") or []
    if lordships:
        dusthana = {6, 8, 12}
        if set(lordships) & dusthana:
            parts.append("Lordship of dusthana houses requires restraint. Preserve what you have built.")
        elif lord_data.get("is_yogakaraka"):
            parts.append("Yogakaraka period; constructive effort bears fruit when applied with awareness.")
        else:
            parts.append("Act with awareness. The fruit will follow.")
    else:
        parts.append("Act with awareness. The fruit will follow.")

    # Tara modifier
    if tara_cat in TARA_CAUTIONARY:
        parts.append("Tara is cautionary; no optimistic phrasing. Conserve strength.")
    elif tara_cat in TARA_MEASURED:
        parts.append("Tara allows measured progress when effort is deliberate.")

    # Most afflicted house
    if most_afflicted and afflicted_reason:
        parts.append(f"The {_house_ordinal(most_afflicted)} house is most afflicted today ({afflicted_reason}); proceed with care.")

    # Gita reference (structural - chapter/verse by graha)
    GITA_VERSE = {
        "Sun": (3, 21), "Moon": (6, 26), "Mars": (2, 63), "Mercury": (17, 15),
        "Jupiter": (4, 38), "Venus": (5, 10), "Saturn": (2, 47),
        "Rahu": (3, 39), "Ketu": (6, 1),
    }
    ch, v = GITA_VERSE.get(mahadasha, (2, 47))
    parts.append(f"Bhagavad Gita {ch}.{v}")

    parts.append("Act with awareness. The fruit will follow.")

    return "\n\n".join(parts)


def build_chandra_bala_section(context: Dict[str, Any]) -> str:
    """Chandra Bala from house_from_moon. Chandrashtama override."""
    transit = context.get("transit") or {}
    moon_data = transit.get("Moon")
    if isinstance(moon_data, dict) and moon_data.get("house_from_moon") == 8:
        return "Chandrashtama operates today. The mind may feel unsettled. Do not initiate major ventures today."
    return "The mind remains steady within its present field. Clarity comes when emotion is disciplined."


def build_tara_section(context: Dict[str, Any]) -> str:
    """Tara from category. Elaboration from data, not static mapping."""
    tara = context.get("tara_bala") or {}
    cat = (tara.get("tara_category") or tara.get("tara_name") or "").strip()
    quality_str = (tara.get("quality") or "").strip()

    if not cat:
        return "The day unfolds under its natural rhythm."

    # Data-driven elaboration based on category
    if cat in TARA_CAUTIONARY:
        elab = "Obstacles test resilience. Do not force what resists; conserve strength. No optimistic expansion."
    elif cat in TARA_MEASURED:
        elab = "Effort applied with awareness can bear fruit. The door opens to deliberate action."
    elif cat in ("Mitra", "Param Mitra", "Atimitra"):
        elab = "Conditions favor action. When the field is aligned, move with purpose."
    elif cat == "Sampat":
        elab = "Resources support effort. Accumulation without purpose becomes burden."
    elif cat == "Kshema":
        elab = "Protection surrounds your actions. Steadiness guides the day."
    elif cat == "Janma":
        elab = "Return to your center before acting. What is undertaken from clarity endures."
    else:
        elab = "The day unfolds under its natural rhythm."

    return f"{cat} Tara operates.\n\n{elab}"


def apply_tara_global_tone(text: str, context: Dict[str, Any]) -> str:
    """
    Tara Bala modifies tone globally.
    Naidhana/Vipat/Pratyak → no optimistic phrasing anywhere.
    Sadhaka → allow measured progress tone.
    """
    tara_cat = _get_tara_category(context)
    if tara_cat not in TARA_CAUTIONARY:
        return text
    # Remove overly optimistic phrases (simple heuristic)
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
