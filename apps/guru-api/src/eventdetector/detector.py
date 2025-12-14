"""
Phase 17: Astro Event Detector Engine

Detects good and bad astrological periods and events.
"""

from typing import Dict, List
from src.eventdetector.rules import BAD_EVENT_RULES, GOOD_EVENT_RULES
from src.jyotish.panchang import get_nakshatra
from src.utils.converters import degrees_to_sign


def detect_rikta_tithi(tithi_number: int) -> Dict:
    """
    Phase 17: Detect Rikta Tithi (4, 9, 14).
    
    Args:
        tithi_number: Tithi number (1-15)
    
    Returns:
        Event dictionary if detected, None otherwise
    """
    if tithi_number in [4, 9, 14]:
        rule = next((r for r in BAD_EVENT_RULES if r["name"] == "Rikta Tithi"), None)
        if rule:
            return {
                "event_name": rule["name"],
                "severity": rule["severity"],
                "description": rule["reason"],
                "reason": f"Today is {tithi_number}th Tithi (Rikta) - considered empty and inauspicious",
                "how_it_affects": "Weakens focus, stability, and new beginnings. May bring delays and obstacles.",
                "what_to_do": "Focus on completion of pending tasks, meditation, and inner reflection.",
                "what_to_avoid": "Avoid major decisions, new ventures, confrontations, and starting new projects.",
                "remedies": rule.get("remedies", []),
                "send_alert": True
            }
    return None


def detect_vishti_karana(karana_name: str) -> Dict:
    """
    Phase 17: Detect Vishti Karana (Bhadra).
    
    Args:
        karana_name: Name of the Karana
    
    Returns:
        Event dictionary if detected, None otherwise
    """
    if karana_name in ["Vishti", "Bhadra"]:
        rule = next((r for r in BAD_EVENT_RULES if r["name"] == "Vishti Karana (Bhadra)"), None)
        if rule:
            return {
                "event_name": rule["name"],
                "severity": rule["severity"],
                "description": rule["reason"],
                "reason": f"Today's Karana is {karana_name} - considered inauspicious",
                "how_it_affects": "Brings obstacles, delays, and challenges to new activities.",
                "what_to_do": "Complete pending tasks, avoid new beginnings, practice patience.",
                "what_to_avoid": "Avoid starting new activities, travel, and important decisions.",
                "remedies": rule.get("remedies", []),
                "send_alert": True
            }
    return None


def detect_moon_house_transit(kundli: Dict, current_moon_deg: float, ascendant_deg: float) -> Dict:
    """
    Phase 17: Detect Moon in 8th house transit.
    
    Args:
        kundli: Birth chart
        current_moon_deg: Current Moon degree
        ascendant_deg: Current Ascendant degree
    
    Returns:
        Event dictionary if detected, None otherwise
    """
    # Calculate relative position from ascendant
    rel_pos = (current_moon_deg - ascendant_deg) % 360
    moon_house = int(rel_pos / 30) + 1
    if moon_house > 12:
        moon_house = 1
    
    if moon_house == 8:
        rule = next((r for r in BAD_EVENT_RULES if r["name"] == "Moon in 8th House Transit"), None)
        if rule:
            return {
                "event_name": rule["name"],
                "severity": rule["severity"],
                "description": rule["reason"],
                "reason": f"Moon is transiting 8th house (Ayur Bhava) - house of longevity and transformation",
                "how_it_affects": "Brings emotional turbulence, stress, health concerns, and transformation challenges.",
                "what_to_do": "Stay calm, take care of health, practice meditation, avoid stress.",
                "what_to_avoid": "Avoid risky decisions, emotional conflicts, and stressful situations.",
                "remedies": rule.get("remedies", []),
                "send_alert": True
            }
    
    # Check for Moon in 6th or 12th from natal Moon
    natal_moon_deg = kundli.get("Planets", {}).get("Moon", {}).get("degree", 0)
    moon_distance = abs(current_moon_deg - natal_moon_deg)
    if moon_distance > 180:
        moon_distance = 360 - moon_distance
    
    # Convert to house difference
    sign_diff = abs(int(current_moon_deg / 30) - int(natal_moon_deg / 30))
    if sign_diff > 6:
        sign_diff = 12 - sign_diff
    
    if sign_diff in [6, 12]:
        rule = next((r for r in BAD_EVENT_RULES if r["name"] == "Moon in 6th/12th from Natal Moon"), None)
        if rule:
            return {
                "event_name": rule["name"],
                "severity": rule["severity"],
                "description": rule["reason"],
                "reason": f"Moon is {sign_diff} signs away from your natal Moon - creates challenging energies",
                "how_it_affects": "Brings challenges related to health (6th) or losses (12th).",
                "what_to_do": "Be cautious with health and finances, practice peace, avoid conflicts.",
                "what_to_avoid": "Avoid stress, conflicts, and risky financial decisions.",
                "remedies": rule.get("remedies", []),
                "send_alert": True
            }
    
    return None


def detect_planet_conjunctions(current_planets: Dict, kundli: Dict) -> List[Dict]:
    """
    Phase 17: Detect planet conjunctions (Rahu-Moon, Ketu-Moon, Mars-Moon).
    
    Args:
        current_planets: Current planetary positions
        kundli: Birth chart
    
    Returns:
        List of detected conjunction events
    """
    events = []
    
    # Get current positions
    current_moon = current_planets.get("Moon", 0)
    current_rahu = current_planets.get("Rahu", 0)
    current_ketu = current_planets.get("Ketu", 0)
    current_mars = current_planets.get("Mars", 0)
    
    # Check Rahu-Moon conjunction (within 5 degrees)
    if current_rahu and abs(current_rahu - current_moon) % 360 < 5 or abs(current_rahu - current_moon) % 360 > 355:
        rule = next((r for r in BAD_EVENT_RULES if r["name"] == "Rahu-Moon Conjunction"), None)
        if rule:
            events.append({
                "event_name": rule["name"],
                "severity": rule["severity"],
                "description": rule["reason"],
                "reason": "Rahu and Moon are in close conjunction - creates confusion and illusions",
                "how_it_affects": "Brings confusion, emotional instability, and illusions. May cloud judgment.",
                "what_to_do": "Be clear in communication, trust intuition carefully, practice meditation.",
                "what_to_avoid": "Avoid hasty decisions, illusions, and unclear situations.",
                "remedies": rule.get("remedies", []),
                "send_alert": True
            })
    
    # Check Ketu-Moon conjunction
    if current_ketu and abs(current_ketu - current_moon) % 360 < 5 or abs(current_ketu - current_moon) % 360 > 355:
        rule = next((r for r in BAD_EVENT_RULES if r["name"] == "Ketu-Moon Conjunction"), None)
        if rule:
            events.append({
                "event_name": rule["name"],
                "severity": rule["severity"],
                "description": rule["reason"],
                "reason": "Ketu and Moon are in close conjunction - brings detachment and spiritual confusion",
                "how_it_affects": "Brings detachment, isolation, and spiritual confusion.",
                "what_to_do": "Focus on spiritual practices, seek clarity, avoid isolation.",
                "what_to_avoid": "Avoid isolation, confusion, and hasty spiritual decisions.",
                "remedies": rule.get("remedies", []),
                "send_alert": True
            })
    
    # Check Mars-Moon conjunction (Angaraka)
    if current_mars and abs(current_mars - current_moon) % 360 < 5 or abs(current_mars - current_moon) % 360 > 355:
        rule = next((r for r in BAD_EVENT_RULES if r["name"] == "Mars-Moon Angaraka"), None)
        if rule:
            events.append({
                "event_name": rule["name"],
                "severity": rule["severity"],
                "description": rule["reason"],
                "reason": "Mars and Moon are in close conjunction (Angaraka Yoga) - creates anger and impulsiveness",
                "how_it_affects": "Brings anger, impulsiveness, and conflicts.",
                "what_to_do": "Control anger, practice patience, engage in cooling activities.",
                "what_to_avoid": "Avoid arguments, conflicts, and impulsive decisions.",
                "remedies": rule.get("remedies", []),
                "send_alert": True
            })
    
    return events


def detect_good_events(context: Dict) -> List[Dict]:
    """
    Phase 17: Detect good/auspicious events.
    
    Args:
        context: Complete astrological context
    
    Returns:
        List of good events
    """
    events = []
    panchang = context.get("panchang", {})
    dasha = context.get("dasha", {})
    kundli = context.get("kundli", {})
    
    # Check for Siddhi/Amrita Yoga
    yoga = panchang.get("yoga", {})
    yoga_name = yoga.get("name", "")
    
    if "Siddhi" in yoga_name:
        rule = next((r for r in GOOD_EVENT_RULES if r["name"] == "Siddhi Yoga"), None)
        if rule:
            events.append({
                "event_name": rule["name"],
                "severity": "low",  # Low = good
                "description": rule["reason"],
                "reason": f"Today's Yoga is {yoga_name} - brings success and achievement",
                "how_it_affects": "Brings success, achievement, and fulfillment of desires.",
                "what_to_do": "Excellent time for important activities, new ventures, and goal achievement.",
                "what_to_avoid": "Don't waste this auspicious time - take action on important matters.",
                "remedies": [],
                "send_alert": False  # Good events don't need alerts
            })
    
    if "Amrita" in yoga_name:
        rule = next((r for r in GOOD_EVENT_RULES if r["name"] == "Amrita Yoga"), None)
        if rule:
            events.append({
                "event_name": rule["name"],
                "severity": "low",
                "description": rule["reason"],
                "reason": f"Today's Yoga is {yoga_name} - brings nectar-like positive energies",
                "how_it_affects": "Brings auspiciousness, positive energy, and success.",
                "what_to_do": "Highly favorable for all activities, especially spiritual and creative.",
                "what_to_avoid": "Don't waste this auspicious time.",
                "remedies": [],
                "send_alert": False
            })
    
    # Check if Moon in natal Nakshatra
    current_nakshatra = panchang.get("nakshatra", {}).get("name", "")
    natal_moon_deg = kundli.get("Planets", {}).get("Moon", {}).get("degree", 0)
    from src.jyotish.panchang import get_nakshatra
    natal_nakshatra_name, _ = get_nakshatra(natal_moon_deg)
    
    if current_nakshatra == natal_nakshatra_name:
        rule = next((r for r in GOOD_EVENT_RULES if r["name"] == "Shubha Nakshatra Matching Birth"), None)
        if rule:
            events.append({
                "event_name": rule["name"],
                "severity": "low",
                "description": rule["reason"],
                "reason": f"Moon is in your natal Nakshatra ({current_nakshatra}) - highly auspicious",
                "how_it_affects": "Brings alignment with natural tendencies and auspiciousness.",
                "what_to_do": "Highly favorable day. Trust your intuition and natural inclinations.",
                "what_to_avoid": "Don't waste this auspicious time.",
                "remedies": [],
                "send_alert": False
            })
    
    # Check for benefic Dasha start
    current_dasha = dasha.get("current_dasha", {})
    dasha_lord = current_dasha.get("dasha_lord", "")
    if dasha_lord in ["Jupiter", "Venus", "Mercury"]:
        # Check if recently started (within last 30 days)
        events.append({
            "event_name": "Dasha Beginning of Benefic Planet",
            "severity": "low",
            "description": f"You are in {dasha_lord} Dasha - a benefic period",
            "reason": f"Beginning of benefic Dasha ({dasha_lord}) brings positive changes",
            "how_it_affects": "Brings new opportunities, growth, and positive changes.",
            "what_to_do": "Excellent time for new beginnings, growth, and positive activities.",
            "what_to_avoid": "Don't waste this positive period.",
            "remedies": [],
            "send_alert": False
        })
    
    return events


def detect_events(context: Dict) -> Dict:
    """
    Phase 17: Main event detection function.
    
    Detects all astrological events (good and bad) for the user.
    
    Args:
        context: Complete astrological context dictionary
    
    Returns:
        Dictionary with detected events categorized
    """
    bad_events = []
    good_events = []
    
    panchang = context.get("panchang", {})
    kundli = context.get("kundli", {})
    daily = context.get("daily", {})
    transits = context.get("transits", {})
    
    # Get current planetary positions
    from src.jyotish.kundli_engine import get_planet_positions
    from datetime import datetime
    today = datetime.now()
    import swisseph as swe
    today_jd = swe.julday(today.year, today.month, today.day, today.hour + today.minute / 60.0, swe.GREG_CAL)
    current_planets = get_planet_positions(today_jd)
    
    # 1. Detect Rikta Tithi
    tithi = panchang.get("tithi", {})
    tithi_number = tithi.get("number", 0)
    rikta_event = detect_rikta_tithi(tithi_number)
    if rikta_event:
        bad_events.append(rikta_event)
    
    # 2. Detect Vishti Karana
    karana = panchang.get("karana", {})
    karana_name = karana.get("name", "")
    vishti_event = detect_vishti_karana(karana_name)
    if vishti_event:
        bad_events.append(vishti_event)
    
    # 3. Detect Moon house transits
    ascendant_deg = kundli.get("Ascendant", {}).get("degree", 0)
    current_moon_deg = current_planets.get("Moon", 0)
    moon_house_event = detect_moon_house_transit(kundli, current_moon_deg, ascendant_deg)
    if moon_house_event:
        bad_events.append(moon_house_event)
    
    # 4. Detect planet conjunctions
    conjunction_events = detect_planet_conjunctions(current_planets, kundli)
    bad_events.extend(conjunction_events)
    
    # 5. Detect good events
    good_events = detect_good_events(context)
    
    # Calculate overall day status
    if bad_events:
        high_severity = sum(1 for e in bad_events if e.get("severity") == "high")
        if high_severity > 0:
            day_status = "challenging"
        else:
            day_status = "moderate"
    elif good_events:
        day_status = "auspicious"
    else:
        day_status = "normal"
    
    return {
        "bad_events": bad_events,
        "good_events": good_events,
        "total_bad": len(bad_events),
        "total_good": len(good_events),
        "day_status": day_status,
        "alerts_needed": [e for e in bad_events if e.get("send_alert", False)],
        "summary": f"Detected {len(bad_events)} challenging events and {len(good_events)} auspicious events"
    }

