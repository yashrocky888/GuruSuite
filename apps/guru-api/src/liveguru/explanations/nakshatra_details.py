"""
Phase 16: Nakshatra Deep Details

Complete nakshatra information with symbol, lord, guna, qualities, and shastra meaning.
"""

from src.jyotish.panchang import NAKSHATRA_LIST

# Phase 16: Complete Nakshatra Details
NAKSHATRA_DETAILS = {
    "Ashwini": {
        "symbol": "Horse head",
        "lord": "Ketu",
        "guna": "Deva",
        "qualities": "Quick healing, new beginnings, speed, vitality",
        "shadow": "Impulsiveness, restlessness",
        "shastra_meaning": "Represents healing energy, quick action, and new starts. Good for initiating activities.",
        "pada_1": "Quick action, healing, new ventures",
        "pada_2": "Speed, movement, transportation",
        "pada_3": "Vitality, energy, physical strength",
        "pada_4": "Completing tasks, finishing projects"
    },
    
    "Bharani": {
        "symbol": "Yoni (female organ)",
        "lord": "Venus",
        "guna": "Manushya",
        "qualities": "Creativity, fertility, passion, transformation",
        "shadow": "Excessive desire, attachment",
        "shastra_meaning": "Represents creation, fertility, and transformation. Good for creative pursuits.",
        "pada_1": "Creative expression, arts",
        "pada_2": "Relationships, partnerships",
        "pada_3": "Transformation, change",
        "pada_4": "Completion, fulfillment"
    },
    
    "Krittika": {
        "symbol": "Razor, flame",
        "lord": "Sun",
        "guna": "Rakshasa",
        "qualities": "Sharpness, cutting through obstacles, purification",
        "shadow": "Criticism, cutting words",
        "shastra_meaning": "Represents sharpness, purification, and cutting through illusions. Good for decisive action.",
        "pada_1": "Sharp intellect, cutting through problems",
        "pada_2": "Purification, cleansing",
        "pada_3": "Fire energy, transformation",
        "pada_4": "Completion, finishing"
    },
    
    "Rohini": {
        "symbol": "Cart, chariot",
        "lord": "Moon",
        "guna": "Manushya",
        "qualities": "Growth, fertility, material prosperity, beauty",
        "shadow": "Material attachment, possessiveness",
        "shastra_meaning": "Represents growth, fertility, and material abundance. Most auspicious for material pursuits.",
        "pada_1": "Material growth, prosperity",
        "pada_2": "Fertility, creativity",
        "pada_3": "Beauty, aesthetics",
        "pada_4": "Abundance, fulfillment"
    },
    
    "Mrigashira": {
        "symbol": "Deer head",
        "lord": "Mars",
        "guna": "Deva",
        "qualities": "Curiosity, searching, wandering, exploration",
        "shadow": "Restlessness, indecision",
        "shastra_meaning": "Represents searching, exploration, and curiosity. Good for research and learning.",
        "pada_1": "Curiosity, exploration",
        "pada_2": "Searching, research",
        "pada_3": "Wandering, travel",
        "pada_4": "Finding answers, discovery"
    },
    
    "Ardra": {
        "symbol": "Tear drop, diamond",
        "lord": "Rahu",
        "guna": "Manushya",
        "qualities": "Transformation, destruction for creation, intensity",
        "shadow": "Destruction, sorrow, pain",
        "shastra_meaning": "Represents transformation through destruction. Good for breaking old patterns.",
        "pada_1": "Breaking patterns, transformation",
        "pada_2": "Intensity, deep work",
        "pada_3": "Destruction for creation",
        "pada_4": "New beginning after destruction"
    },
    
    "Punarvasu": {
        "symbol": "Bow, quiver",
        "lord": "Jupiter",
        "guna": "Deva",
        "qualities": "Renewal, return, restoration, prosperity",
        "shadow": "Indecision, returning to old patterns",
        "shastra_meaning": "Represents renewal and return. Good for restoration and recovery.",
        "pada_1": "Renewal, fresh start",
        "pada_2": "Return, restoration",
        "pada_3": "Prosperity, abundance",
        "pada_4": "Completion, fulfillment"
    },
    
    "Pushya": {
        "symbol": "Flower, arrow",
        "lord": "Saturn",
        "guna": "Deva",
        "qualities": "Nourishment, protection, auspiciousness, growth",
        "shadow": "Over-protection, dependency",
        "shastra_meaning": "Most auspicious nakshatra. Represents nourishment and protection. Excellent for all activities.",
        "pada_1": "Nourishment, care",
        "pada_2": "Protection, security",
        "pada_3": "Growth, expansion",
        "pada_4": "Auspicious completion"
    },
    
    "Ashlesha": {
        "symbol": "Serpent, coiled",
        "lord": "Mercury",
        "guna": "Rakshasa",
        "qualities": "Intensity, transformation, healing, mysticism",
        "shadow": "Deception, poison, manipulation",
        "shastra_meaning": "Represents serpent energy, transformation, and mysticism. Good for deep healing work.",
        "pada_1": "Intensity, deep work",
        "pada_2": "Transformation, healing",
        "pada_3": "Mysticism, hidden knowledge",
        "pada_4": "Completion, integration"
    },
    
    "Magha": {
        "symbol": "Throne, palanquin",
        "lord": "Ketu",
        "guna": "Rakshasa",
        "qualities": "Royalty, authority, ancestors, power",
        "shadow": "Arrogance, ego, pride",
        "shastra_meaning": "Represents royalty and authority. Good for leadership and honoring ancestors.",
        "pada_1": "Royalty, authority",
        "pada_2": "Ancestors, lineage",
        "pada_3": "Power, leadership",
        "pada_4": "Legacy, completion"
    },
    
    "Purva Phalguni": {
        "symbol": "Hammock, swing",
        "lord": "Venus",
        "guna": "Manushya",
        "qualities": "Enjoyment, pleasure, creativity, relationships",
        "shadow": "Laziness, indulgence, excess",
        "shastra_meaning": "Represents enjoyment and pleasure. Good for creative and relationship activities.",
        "pada_1": "Enjoyment, pleasure",
        "pada_2": "Creativity, arts",
        "pada_3": "Relationships, partnerships",
        "pada_4": "Fulfillment, satisfaction"
    },
    
    "Uttara Phalguni": {
        "symbol": "Fig tree, bed",
        "lord": "Sun",
        "guna": "Manushya",
        "qualities": "Philanthropy, service, relationships, healing",
        "shadow": "Over-giving, self-neglect",
        "shastra_meaning": "Represents service and philanthropy. Good for helping others and relationships.",
        "pada_1": "Service, helping others",
        "pada_2": "Relationships, partnerships",
        "pada_3": "Healing, care",
        "pada_4": "Fulfillment through service"
    },
    
    "Hasta": {
        "symbol": "Hand, fist",
        "lord": "Moon",
        "guna": "Deva",
        "qualities": "Skill, dexterity, craftsmanship, healing",
        "shadow": "Theft, manipulation, trickery",
        "shastra_meaning": "Represents skill and craftsmanship. Good for detailed work and healing.",
        "pada_1": "Skill, craftsmanship",
        "pada_2": "Dexterity, precision",
        "pada_3": "Healing, service",
        "pada_4": "Mastery, completion"
    },
    
    "Chitra": {
        "symbol": "Pearl, gem",
        "lord": "Mars",
        "guna": "Rakshasa",
        "qualities": "Beauty, creativity, artistry, brilliance",
        "shadow": "Perfectionism, criticism",
        "shastra_meaning": "Represents beauty and creativity. Good for artistic and creative pursuits.",
        "pada_1": "Beauty, aesthetics",
        "pada_2": "Creativity, artistry",
        "pada_3": "Brilliance, excellence",
        "pada_4": "Perfection, completion"
    },
    
    "Swati": {
        "symbol": "Sword, coral",
        "lord": "Rahu",
        "guna": "Deva",
        "qualities": "Independence, movement, change, flexibility",
        "shadow": "Instability, restlessness",
        "shastra_meaning": "Represents independence and movement. Good for change and new directions.",
        "pada_1": "Independence, freedom",
        "pada_2": "Movement, change",
        "pada_3": "Flexibility, adaptation",
        "pada_4": "New direction, completion"
    },
    
    "Vishakha": {
        "symbol": "Archway, potter's wheel",
        "lord": "Jupiter",
        "guna": "Rakshasa",
        "qualities": "Determination, achievement, success, ambition",
        "shadow": "Competitiveness, conflict",
        "shastra_meaning": "Represents determination and achievement. Good for goal-oriented activities.",
        "pada_1": "Determination, willpower",
        "pada_2": "Achievement, success",
        "pada_3": "Ambition, goals",
        "pada_4": "Completion, victory"
    },
    
    "Anuradha": {
        "symbol": "Lotus, staff",
        "lord": "Saturn",
        "guna": "Deva",
        "qualities": "Devotion, friendship, loyalty, success through others",
        "shadow": "Dependency, lack of independence",
        "shastra_meaning": "Represents devotion and friendship. Good for partnerships and collaborative work.",
        "pada_1": "Devotion, dedication",
        "pada_2": "Friendship, partnerships",
        "pada_3": "Loyalty, commitment",
        "pada_4": "Success through collaboration"
    },
    
    "Jyeshtha": {
        "symbol": "Earring, umbrella",
        "lord": "Mercury",
        "guna": "Rakshasa",
        "qualities": "Eldership, authority, protection, seniority",
        "shadow": "Jealousy, possessiveness, control",
        "shastra_meaning": "Represents authority and protection. Good for leadership and protecting others.",
        "pada_1": "Authority, leadership",
        "pada_2": "Protection, care",
        "pada_3": "Seniority, wisdom",
        "pada_4": "Completion, fulfillment"
    },
    
    "Mula": {
        "symbol": "Root, bundle of roots",
        "lord": "Ketu",
        "guna": "Rakshasa",
        "qualities": "Root cause, foundation, destruction for renewal",
        "shadow": "Destruction, uprooting, loss",
        "shastra_meaning": "Represents roots and foundation. Good for going to the root cause and deep work.",
        "pada_1": "Root cause, foundation",
        "pada_2": "Deep work, investigation",
        "pada_3": "Destruction for renewal",
        "pada_4": "New foundation, completion"
    },
    
    "Purva Ashadha": {
        "symbol": "Fan, winnowing basket",
        "lord": "Venus",
        "guna": "Manushya",
        "qualities": "Invincibility, victory, success, purification",
        "shadow": "Arrogance, overconfidence",
        "shastra_meaning": "Represents invincibility and victory. Good for competitive activities.",
        "pada_1": "Invincibility, strength",
        "pada_2": "Victory, success",
        "pada_3": "Purification, cleansing",
        "pada_4": "Complete victory"
    },
    
    "Uttara Ashadha": {
        "symbol": "Elephant tusk, planks",
        "lord": "Sun",
        "guna": "Manushya",
        "qualities": "Universal victory, leadership, determination",
        "shadow": "Rigidity, stubbornness",
        "shastra_meaning": "Represents universal victory. Good for leadership and achieving goals.",
        "pada_1": "Universal victory",
        "pada_2": "Leadership, authority",
        "pada_3": "Determination, persistence",
        "pada_4": "Complete success"
    },
    
    "Shravana": {
        "symbol": "Ear, three footprints",
        "lord": "Moon",
        "guna": "Deva",
        "qualities": "Listening, learning, knowledge, travel",
        "shadow": "Gossip, hearing problems",
        "shastra_meaning": "Represents listening and learning. Good for education and acquiring knowledge.",
        "pada_1": "Listening, learning",
        "pada_2": "Education, knowledge",
        "pada_3": "Travel, movement",
        "pada_4": "Wisdom, completion"
    },
    
    "Dhanishtha": {
        "symbol": "Drum, flute",
        "lord": "Mars",
        "guna": "Rakshasa",
        "qualities": "Wealth, music, rhythm, abundance",
        "shadow": "Materialism, greed",
        "shastra_meaning": "Represents wealth and abundance. Good for financial activities and music.",
        "pada_1": "Wealth, abundance",
        "pada_2": "Music, rhythm",
        "pada_3": "Prosperity, success",
        "pada_4": "Complete fulfillment"
    },
    
    "Shatabhisha": {
        "symbol": "Hundred stars, circle",
        "lord": "Rahu",
        "guna": "Rakshasa",
        "qualities": "Healing, medicine, mysticism, secrets",
        "shadow": "Isolation, secrets, hidden problems",
        "shastra_meaning": "Represents healing and mysticism. Good for medical and spiritual work.",
        "pada_1": "Healing, medicine",
        "pada_2": "Mysticism, secrets",
        "pada_3": "Hidden knowledge",
        "pada_4": "Revelation, completion"
    },
    
    "Purva Bhadrapada": {
        "symbol": "Sword, two legs",
        "lord": "Jupiter",
        "guna": "Manushya",
        "qualities": "Transformation, purification, spiritual fire",
        "shadow": "Destruction, fire, accidents",
        "shastra_meaning": "Represents transformation through fire. Good for purification and spiritual work.",
        "pada_1": "Transformation, change",
        "pada_2": "Purification, cleansing",
        "pada_3": "Spiritual fire, intensity",
        "pada_4": "Complete transformation"
    },
    
    "Uttara Bhadrapada": {
        "symbol": "Snake, two legs",
        "lord": "Saturn",
        "guna": "Manushya",
        "qualities": "Stability, protection, completion, moksha",
        "shadow": "Stagnation, delay",
        "shastra_meaning": "Represents stability and completion. Good for finishing projects and spiritual completion.",
        "pada_1": "Stability, foundation",
        "pada_2": "Protection, security",
        "pada_3": "Completion, fulfillment",
        "pada_4": "Moksha, liberation"
    },
    
    "Revati": {
        "symbol": "Fish, drum",
        "lord": "Mercury",
        "guna": "Deva",
        "qualities": "Nourishment, protection, completion, abundance",
        "shadow": "Over-protection, dependency",
        "shastra_meaning": "Represents nourishment and completion. Most auspicious for endings and new beginnings.",
        "pada_1": "Nourishment, care",
        "pada_2": "Protection, security",
        "pada_3": "Abundance, fulfillment",
        "pada_4": "Complete completion, new cycle"
    }
}


def get_nakshatra_details(nakshatra_name: str) -> dict:
    """
    Phase 16: Get detailed nakshatra information.
    
    Args:
        nakshatra_name: Name of the nakshatra
    
    Returns:
        Dictionary with nakshatra details
    """
    return NAKSHATRA_DETAILS.get(nakshatra_name, {
        "symbol": "Unknown",
        "lord": "Unknown",
        "guna": "Unknown",
        "qualities": "Nakshatra details not available",
        "shadow": "Unknown",
        "shastra_meaning": "Nakshatra information not available"
    })


def format_nakshatra_for_message(nakshatra_name: str, pada: int = None) -> str:
    """
    Phase 16: Format nakshatra details for message inclusion.
    
    Args:
        nakshatra_name: Name of the nakshatra
        pada: Pada number (1-4), optional
    
    Returns:
        Formatted string with nakshatra details
    """
    details = get_nakshatra_details(nakshatra_name)
    
    if not details:
        return f"{nakshatra_name}: Nakshatra details available"
    
    pada_key = f"pada_{pada}" if pada else None
    pada_info = details.get(pada_key, "") if pada_key else ""
    
    return f"""
Nakshatra: {nakshatra_name}
• Symbol: {details.get('symbol', 'N/A')}
• Lord: {details.get('lord', 'N/A')}
• Guna: {details.get('guna', 'N/A')}
• Qualities: {details.get('qualities', 'N/A')}
• Shadow: {details.get('shadow', 'N/A')}
• Shastra Meaning: {details.get('shastra_meaning', 'N/A')}
{f'• Pada {pada} Meaning: {pada_info}' if pada_info else ''}
"""

