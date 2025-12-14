"""
Phase 17: Astro Event Detection Rules

Defines all astrological events (good and bad) with their detection logic.
"""

# Phase 17: Bad/Danger Period Rules
BAD_EVENT_RULES = [
    {
        "name": "Rikta Tithi",
        "type": "tithi",
        "tithis": [4, 9, 14],  # Chaturthi, Navami, Chaturdashi
        "severity": "high",
        "reason": "Rikta Tithis (4th, 9th, 14th) are considered empty and inauspicious. They weaken focus, stability, and new beginnings.",
        "advice": "Avoid major decisions, new ventures, and confrontations. Focus on completion rather than initiation.",
        "remedies": ["Chant 'Om Namah Shivaya'", "Light a lamp", "Donate to charity", "Avoid arguments"]
    },
    {
        "name": "Vishti Karana (Bhadra)",
        "type": "karana",
        "karanas": ["Vishti", "Bhadra"],
        "severity": "high",
        "reason": "Vishti Karana is considered inauspicious. It brings obstacles and delays.",
        "advice": "Avoid starting new activities, travel, and important decisions.",
        "remedies": ["Pray to Lord Ganesha", "Avoid new beginnings", "Complete pending tasks"]
    },
    {
        "name": "Panchaka Days",
        "type": "panchaka",
        "severity": "medium",
        "reason": "Panchaka days (5 specific days) are considered inauspicious for certain activities.",
        "advice": "Be cautious with travel and new ventures.",
        "remedies": ["Perform prayers", "Avoid unnecessary travel"]
    },
    {
        "name": "Moon in 8th House Transit",
        "type": "transit",
        "condition": "moon_house == 8",
        "severity": "high",
        "reason": "Moon in 8th house (Ayur Bhava) transit brings emotional turbulence, stress, and health concerns.",
        "advice": "Stay calm, avoid risky decisions, take care of health.",
        "remedies": ["Meditation", "Moon mantra: 'Om Chandraya Namah'", "Avoid emotional conflicts"]
    },
    {
        "name": "Moon in 6th/12th from Natal Moon",
        "type": "transit",
        "condition": "moon_distance in [6, 12]",
        "severity": "medium",
        "reason": "Moon transiting 6th or 12th from natal Moon creates challenging energies.",
        "advice": "Be cautious with health and finances. Avoid conflicts.",
        "remedies": ["Moon remedies", "Peaceful activities", "Avoid stress"]
    },
    {
        "name": "Moon in Ashtama Shani",
        "type": "transit",
        "condition": "moon_ashtama_shani",
        "severity": "high",
        "reason": "Moon in 8th from Saturn creates stress and obstacles.",
        "advice": "Be patient, avoid confrontations, focus on inner work.",
        "remedies": ["Saturn remedies", "Chant 'Om Shani Devaya Namah'", "Service to others"]
    },
    {
        "name": "Rahu-Moon Conjunction",
        "type": "conjunction",
        "planets": ["Rahu", "Moon"],
        "severity": "high",
        "reason": "Rahu-Moon conjunction creates confusion, illusions, and emotional instability.",
        "advice": "Avoid hasty decisions, be clear in communication, trust your intuition carefully.",
        "remedies": ["Rahu mantra: 'Om Raam Rahave Namah'", "Meditation", "Avoid illusions"]
    },
    {
        "name": "Ketu-Moon Conjunction",
        "type": "conjunction",
        "planets": ["Ketu", "Moon"],
        "severity": "medium",
        "reason": "Ketu-Moon conjunction brings detachment, isolation, and spiritual confusion.",
        "advice": "Focus on spiritual practices, avoid isolation, seek clarity.",
        "remedies": ["Ketu mantra: 'Om Kem Ketave Namah'", "Spiritual practices", "Seek guidance"]
    },
    {
        "name": "Mars-Moon Angaraka",
        "type": "conjunction",
        "planets": ["Mars", "Moon"],
        "severity": "medium",
        "reason": "Mars-Moon conjunction (Angaraka Yoga) creates anger, impulsiveness, and conflicts.",
        "advice": "Control anger, avoid arguments, practice patience.",
        "remedies": ["Mars mantra: 'Om Kram Kreem Krom Sah Bhaumaya Namah'", "Cooling foods", "Meditation"]
    },
    {
        "name": "Bad Gandanta Days",
        "type": "gandanta",
        "severity": "high",
        "reason": "Gandanta (junction of water and fire signs) creates critical transitions and challenges.",
        "advice": "Be extremely cautious, avoid major decisions, focus on safety.",
        "remedies": ["Special prayers", "Avoid travel", "Seek astrological guidance"]
    },
    {
        "name": "Retrograde Malefics Affecting Lagna",
        "type": "retrograde",
        "severity": "medium",
        "reason": "Retrograde malefic planets (Saturn, Mars, Rahu, Ketu) affecting Ascendant create delays and obstacles.",
        "advice": "Be patient with delays, avoid forcing outcomes, work on inner strength.",
        "remedies": ["Planet-specific remedies", "Patience", "Inner work"]
    },
    {
        "name": "Malefics in 1, 7, 8, 12 from Lagna Transit",
        "type": "transit",
        "condition": "malefics_in_kendra_dusthana",
        "severity": "high",
        "reason": "Malefic planets in Kendra (1, 4, 7, 10) or Dusthana (6, 8, 12) houses create challenges.",
        "advice": "Be cautious, avoid risks, focus on protection and remedies.",
        "remedies": ["Planet-specific remedies", "Protection prayers", "Avoid risky activities"]
    }
]

# Phase 17: Good/Auspicious Period Rules
GOOD_EVENT_RULES = [
    {
        "name": "Pushkara Days",
        "type": "pushkara",
        "severity": "low",  # Low severity = good event
        "reason": "Pushkara days are highly auspicious for water-related activities and spiritual practices.",
        "advice": "Excellent time for spiritual activities, charity, and positive actions.",
        "benefits": ["Spiritual growth", "Positive outcomes", "Favorable for water activities"]
    },
    {
        "name": "Siddhi Yoga",
        "type": "yoga",
        "severity": "low",
        "reason": "Siddhi Yoga brings success, achievement, and fulfillment of desires.",
        "advice": "Excellent time for important activities, new ventures, and goal achievement.",
        "benefits": ["Success", "Achievement", "Fulfillment"]
    },
    {
        "name": "Amrita Yoga",
        "type": "yoga",
        "severity": "low",
        "reason": "Amrita Yoga brings nectar-like positive energies and auspiciousness.",
        "advice": "Highly favorable for all activities, especially spiritual and creative pursuits.",
        "benefits": ["Auspiciousness", "Positive energy", "Success"]
    },
    {
        "name": "Guru-Moon Combination",
        "type": "combination",
        "planets": ["Jupiter", "Moon"],
        "severity": "low",
        "reason": "Jupiter-Moon combination (Gaja Kesari Yoga) brings wisdom, prosperity, and emotional stability.",
        "advice": "Excellent time for learning, teaching, relationships, and spiritual growth.",
        "benefits": ["Wisdom", "Prosperity", "Emotional stability"]
    },
    {
        "name": "Shubha Nakshatra Matching Birth",
        "type": "nakshatra",
        "condition": "current_nakshatra == natal_nakshatra",
        "severity": "low",
        "reason": "Moon in natal Nakshatra brings alignment with natural tendencies and auspiciousness.",
        "advice": "Highly favorable day. Trust your intuition and natural inclinations.",
        "benefits": ["Natural alignment", "Intuition", "Auspiciousness"]
    },
    {
        "name": "Dasha Beginning of Benefic Planet",
        "type": "dasha",
        "condition": "benefic_dasha_start",
        "severity": "low",
        "reason": "Beginning of benefic Dasha (Jupiter, Venus, Mercury) brings positive changes.",
        "advice": "Excellent time for new beginnings, growth, and positive changes.",
        "benefits": ["New opportunities", "Growth", "Positive changes"]
    },
    {
        "name": "Tara Strength Favorable",
        "type": "tara",
        "severity": "low",
        "reason": "Favorable Tara (star) position brings support and positive outcomes.",
        "advice": "Good time for important activities and decisions.",
        "benefits": ["Support", "Positive outcomes", "Favorable timing"]
    },
    {
        "name": "Lagna Rising with Yoga-Karaka Strength",
        "type": "lagna",
        "severity": "low",
        "reason": "Strong Ascendant with Yoga-Karaka planets brings auspiciousness and success.",
        "advice": "Excellent time for leadership, new ventures, and important activities.",
        "benefits": ["Leadership", "Success", "Auspiciousness"]
    },
    {
        "name": "Moon in Trine (1-5-9) or Kendra (4-7-10)",
        "type": "transit",
        "condition": "moon_in_trine_or_kendra",
        "severity": "low",
        "reason": "Moon in trine or kendra from Ascendant brings favorable energies.",
        "advice": "Good time for important activities and decisions.",
        "benefits": ["Favorable energies", "Support", "Positive outcomes"]
    },
    {
        "name": "Jupiter or Venus Aspecting Moon",
        "type": "aspect",
        "planets": ["Jupiter", "Venus"],
        "severity": "low",
        "reason": "Benefic planets (Jupiter/Venus) aspecting Moon brings wisdom, love, and prosperity.",
        "advice": "Excellent time for relationships, learning, and positive activities.",
        "benefits": ["Wisdom", "Love", "Prosperity"]
    },
    {
        "name": "Strong Panchang of the Day",
        "type": "panchang",
        "condition": "strong_panchang",
        "severity": "low",
        "reason": "Strong combination of Tithi, Nakshatra, Yoga, and Karana brings auspiciousness.",
        "advice": "Highly favorable day for all important activities.",
        "benefits": ["Auspiciousness", "Success", "Positive outcomes"]
    }
]


def get_event_rules():
    """
    Phase 17: Get all event rules.
    
    Returns:
        Dictionary with bad and good event rules
    """
    return {
        "bad_events": BAD_EVENT_RULES,
        "good_events": GOOD_EVENT_RULES
    }

