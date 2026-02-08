"""
Contextual Bhagavad Gita engine for daily dharmic guidance.

Maps dominant transit theme (house focus + Mahadasha lord + retrograde if any)
to a curated verse pool. Rotates verses by date to avoid repetition.
Provides one-line relevance mapping.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Curated verse pool: (chapter, verse, text, theme_keys)
# theme_keys: house numbers (1-12), planet names, "retrograde"
_GITA_POOL: List[Tuple[int, int, str, List[str]]] = [
    (2, 47, "Karmanyevadhikaraste ma phaleshu kadachana.", [1, 10]),  # Action, duty
    (2, 50, "Buddhiyukto jahatiha ubhe sukritadushkrite.", [8, 12]),  # Detachment
    (3, 19, "Tasmadasaktah satatam karyam karma samachara.", [10, 6]),  # Duty without attachment
    (4, 7, "Yada yada hi dharmasya glanirbhavati bharata.", [9]),  # Dharma restoration
    (4, 18, "Karmanyakarma yah pasyedakarmani cha karma yah.", [8]),  # Wisdom in action
    (5, 10, "Brahmanyadhaya karmani sangam tyaktva karoti yah.", [12]),  # Renunciation
    (6, 5, "Uddharedatmanatmanam natmanamavasadayet.", [1]),  # Self-elevation
    (6, 6, "Bandhuratmatmanastasya yenatmaivatmana jitah.", [1, 3]),  # Self-mastery
    (9, 22, "Ananyashchintayanto mam ye janah paryupasate.", [9, 12]),  # Single-pointed devotion
    (12, 13, "Adveshta sarvabhutanam maitrah karuna eva cha.", [7]),  # Compassion
    (12, 15, "Yasmannodvijate loko lokannodvijate cha yah.", [1]),  # Equanimity
    (18, 46, "Yatah pravrittirbhutanam yena sarvamidam tatam.", [10]),  # Swadharma
    (2, 14, "Matrasparshastu kaunteya shitoshna sukhaduhkhadah.", [1]),  # Endurance
    (2, 62, "Dhyayato vishayanpumsah sangasteshupajayate.", [5, 12]),  # Desire chain
    (3, 35, "Shreyan svadharmo vigunah paradharmat svanushthitat.", [9, 10]),  # Own duty
    (6, 26, "Yato yato nishcharati manashchanchalamasthiram.", [1]),  # Mind control
    (11, 33, "Tasmattvamuttishtha yasho labhasva.", [3, 10]),  # Arise and act
    (18, 65, "Manmana bhava madbhakto madyaji mam namaskuru.", [9, 12]),  # Surrender
    (2, 38, "Sukhaduhkhe same kritva labhalabhau jayajayau.", [2, 11]),  # Equanimity in gain/loss
    (5, 29, "Bhoktaram yajnatapasam sarvam lokamaheshwaram.", [9]),  # Cosmic order
    (2, 63, "Krodhad bhavati sammohah sammohat smritivibhramah.", [5, 12]),  # Desire → delusion
    (3, 39, "Avritam jnanam etena jnanino nityavairina.", [5, 12]),  # Desire covers knowledge
    (6, 1, "Anashritah karmaphalam karyam karma karoti yah.", [12]),  # Renunciation of fruits
]

# Theme mapping: house/planet/retro → pool indices (multiple verses per theme)
_THEME_TO_INDICES: Dict[str, List[int]] = {
    "1": [5, 6, 10, 12, 15],   # self, identity
    "2": [17],                  # wealth, speech
    "3": [6, 16],               # courage, communication
    "4": [2, 9],                # home, mother
    "5": [13],                  # creativity
    "6": [2, 3],                # service
    "7": [9],                   # partnership
    "8": [1, 2, 4],             # transformation
    "9": [3, 4, 7, 14, 16, 18], # dharma, fortune
    "10": [0, 2, 3, 11, 14, 16], # career, duty
    "11": [17],                 # gains
    "12": [1, 8, 9, 10, 13, 16], # loss, moksha
    "retrograde": [1, 2, 4, 13], # introspection
    "Sun": [0, 3, 11],
    "Moon": [2, 9],
    "Mars": [16],
    "Mercury": [2, 6],
    "Jupiter": [3, 4, 7, 14],
    "Venus": [9],
    "Saturn": [1, 2, 10, 13],  # Saturn heavy → detachment verses
    "Rahu": [13, 18, 19],     # control of desire: 2.62, 2.63, 3.39
    "Ketu": [5, 20],          # renunciation, detachment: 5.10, 6.1
}


def _dominant_theme(context: Dict[str, Any]) -> Tuple[List[str], Optional[datetime]]:
    """
    Extract dominant theme keys from context.
    Returns (theme_keys, calculation_date).
    """
    themes: List[str] = []
    calc_date: Optional[datetime] = None

    cd_str = context.get("calculation_date")
    if cd_str:
        try:
            calc_date = datetime.fromisoformat(cd_str.replace("Z", "+00:00"))
            if calc_date.tzinfo:
                calc_date = calc_date.replace(tzinfo=None)
        except Exception:
            pass

    time_block = context.get("time") or {}
    mahadasha = (time_block.get("mahadasha_lord") or "").strip()
    if mahadasha and mahadasha in _THEME_TO_INDICES:
        themes.append(mahadasha)

    transit = context.get("transit") or {}
    house_counts: Dict[int, int] = {}
    has_retro = False
    for pname, pdata in transit.items():
        if not isinstance(pdata, dict):
            continue
        if pdata.get("is_retrograde"):
            has_retro = True
        h = pdata.get("house_from_lagna") or pdata.get("transit_house")
        if h is not None:
            house_counts[int(h)] = house_counts.get(int(h), 0) + 1

    if has_retro:
        themes.append("retrograde")

    # Focus houses: Mahadasha lord's transit house + most transited houses
    focus_houses: List[int] = []
    for pname, pdata in transit.items():
        if not isinstance(pdata, dict):
            continue
        if (pname or "").strip() == mahadasha:
            h = pdata.get("house_from_lagna") or pdata.get("transit_house")
            if h is not None:
                focus_houses.append(int(h))
    for h, cnt in sorted(house_counts.items(), key=lambda x: -x[1])[:3]:
        if h not in focus_houses:
            focus_houses.append(h)

    for h in focus_houses[:3]:
        themes.append(str(h))

    if not themes:
        themes = ["9", "10"]

    return themes, calc_date


def get_contextual_gita(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Select one Gita verse based on dominant transit theme.
    Rotates by date. Returns dict with verse, chapter, verse_num, relevance.
    """
    themes, calc_date = _dominant_theme(context)
    candidate_indices: List[int] = []
    for t in themes:
        candidate_indices.extend(_THEME_TO_INDICES.get(t, []))
    if not candidate_indices:
        candidate_indices = list(range(len(_GITA_POOL)))

    # Deduplicate while preserving order
    seen = set()
    unique_indices = []
    for i in candidate_indices:
        if i not in seen and 0 <= i < len(_GITA_POOL):
            seen.add(i)
            unique_indices.append(i)

    if not unique_indices:
        unique_indices = [0]

    # Date-based rotation
    day_ord = calc_date.toordinal() if calc_date else 0
    idx = unique_indices[day_ord % len(unique_indices)]
    ch, v, text, theme_keys = _GITA_POOL[idx]

    # One-line relevance
    relevance_map = {
        1: "Self and identity",
        2: "Wealth and speech",
        3: "Courage and initiative",
        4: "Home and roots",
        5: "Creativity and learning",
        6: "Service and discipline",
        7: "Partnership and harmony",
        8: "Transformation",
        9: "Dharma and fortune",
        10: "Duty and career",
        11: "Gains and aspirations",
        12: "Release and inner peace",
    }
    relevance = "Universal dharma"
    for k in theme_keys:
        if k in relevance_map:
            relevance = relevance_map[k]
            break

    return {
        "chapter": ch,
        "verse": v,
        "text": text,
        "reference": f"Bhagavad Gita {ch}.{v}",
        "relevance": relevance,
    }
