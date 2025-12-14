"""
Phase 16: Planetary Karakatva (Natural Significations)

Deep shastra-level meanings of each planet.
"""

# Phase 16: Complete Karakatva (Natural Significations)
KARAKATVA = {
    "Sun": {
        "primary": ["Soul", "Vitality", "Authority", "Ego"],
        "secondary": ["Father", "Government", "Power", "Leadership", "Health", "Eyes"],
        "nature": "Sattvic, Masculine, Royal",
        "element": "Fire",
        "direction": "East",
        "color": "Red, Gold",
        "gemstone": "Ruby",
        "day": "Sunday",
        "shastra_meaning": "Represents the Atma (soul), self-confidence, and authority. Strong Sun gives leadership, weak Sun indicates lack of confidence."
    },
    
    "Moon": {
        "primary": ["Mind", "Emotions", "Mother", "Fluids"],
        "secondary": ["Intuition", "Popularity", "Travel", "Water", "Milk", "Silver"],
        "nature": "Sattvic, Feminine, Cool",
        "element": "Water",
        "direction": "North-West",
        "color": "White, Silver",
        "gemstone": "Pearl",
        "day": "Monday",
        "shastra_meaning": "Represents Manas (mind), emotions, and mother. Strong Moon gives emotional stability, weak Moon indicates mood swings."
    },
    
    "Mars": {
        "primary": ["Courage", "Energy", "Siblings", "Aggression"],
        "secondary": ["Land", "Property", "Weapons", "Fire", "Red", "Copper"],
        "nature": "Tamasic, Masculine, Fiery",
        "element": "Fire",
        "direction": "South",
        "color": "Red",
        "gemstone": "Coral",
        "day": "Tuesday",
        "shastra_meaning": "Represents Shakti (power), courage, and determination. Strong Mars gives leadership in action, weak Mars indicates lack of courage."
    },
    
    "Mercury": {
        "primary": ["Speech", "Intellect", "Business", "Logic"],
        "secondary": ["Communication", "Mathematics", "Writing", "Trade", "Green"],
        "nature": "Rajasic, Neutral, Intellectual",
        "element": "Earth",
        "direction": "North",
        "color": "Green",
        "gemstone": "Emerald",
        "day": "Wednesday",
        "shastra_meaning": "Represents Buddhi (intellect), communication, and commerce. Strong Mercury gives sharp intellect, weak Mercury indicates communication issues."
    },
    
    "Jupiter": {
        "primary": ["Wisdom", "Children", "Fortune", "Teachers"],
        "secondary": ["Guru", "Religion", "Philosophy", "Wealth", "Yellow", "Gold"],
        "nature": "Sattvic, Masculine, Benefic",
        "element": "Ether",
        "direction": "North-East",
        "color": "Yellow, Gold",
        "gemstone": "Yellow Sapphire",
        "day": "Thursday",
        "shastra_meaning": "Represents Jnana (wisdom), dharma, and fortune. Strong Jupiter gives wisdom and prosperity, weak Jupiter indicates lack of wisdom."
    },
    
    "Venus": {
        "primary": ["Love", "Comfort", "Beauty", "Relationships"],
        "secondary": ["Marriage", "Art", "Music", "Luxury", "Vehicles", "White"],
        "nature": "Rajasic, Feminine, Benefic",
        "element": "Water",
        "direction": "South-East",
        "color": "White, Pink",
        "gemstone": "Diamond",
        "day": "Friday",
        "shastra_meaning": "Represents Kama (desire), beauty, and relationships. Strong Venus gives love and luxury, weak Venus indicates relationship issues."
    },
    
    "Saturn": {
        "primary": ["Karma", "Delay", "Service", "Work"],
        "secondary": ["Discipline", "Longevity", "Old Age", "Iron", "Black", "Blue"],
        "nature": "Tamasic, Neutral, Malefic",
        "element": "Air",
        "direction": "West",
        "color": "Black, Blue",
        "gemstone": "Blue Sapphire",
        "day": "Saturday",
        "shastra_meaning": "Represents Karma, discipline, and delays. Strong Saturn gives discipline and longevity, weak Saturn indicates delays and obstacles."
    },
    
    "Rahu": {
        "primary": ["Ambition", "Foreign", "Illusion", "Desires"],
        "secondary": ["Materialism", "Technology", "Smoke", "Snake", "Grey"],
        "nature": "Tamasic, Neutral, Malefic",
        "element": "Air",
        "direction": "South-West",
        "color": "Grey, Black",
        "gemstone": "Gomedh (Hessonite)",
        "day": "None (Shadow planet)",
        "shastra_meaning": "Represents material desires, illusions, and foreign connections. Strong Rahu gives material success, weak Rahu indicates confusion."
    },
    
    "Ketu": {
        "primary": ["Detachment", "Spiritual", "Past-Life", "Moksha"],
        "secondary": ["Mysticism", "Intuition", "Isolation", "Fire", "Brown"],
        "nature": "Tamasic, Neutral, Spiritual",
        "element": "Fire",
        "direction": "North-West",
        "color": "Brown, Grey",
        "gemstone": "Cat's Eye",
        "day": "None (Shadow planet)",
        "shastra_meaning": "Represents detachment, spirituality, and moksha. Strong Ketu gives spiritual insight, weak Ketu indicates confusion about purpose."
    }
}


def get_karakatva(planet_name: str) -> dict:
    """
    Phase 16: Get karakatva (natural significations) for a planet.
    
    Args:
        planet_name: Name of the planet
    
    Returns:
        Dictionary with karakatva details
    """
    return KARAKATVA.get(planet_name, {
        "primary": [],
        "secondary": [],
        "nature": "Unknown",
        "shastra_meaning": "Planet significations not available"
    })


def format_karakatva_for_message(planet_name: str) -> str:
    """
    Phase 16: Format karakatva for message inclusion.
    
    Args:
        planet_name: Name of the planet
    
    Returns:
        Formatted string with karakatva
    """
    karakatva = get_karakatva(planet_name)
    
    if not karakatva:
        return f"{planet_name}: Planetary significations available"
    
    primary = ", ".join(karakatva.get("primary", []))
    secondary = ", ".join(karakatva.get("secondary", [])[:5])  # Limit to 5
    
    return f"""
{planet_name} (Natural Significations):
• Primary: {primary}
• Secondary: {secondary}
• Nature: {karakatva.get('nature', 'N/A')}
• Shastra Meaning: {karakatva.get('shastra_meaning', 'N/A')}
"""

