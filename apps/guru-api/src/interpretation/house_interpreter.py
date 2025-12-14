"""
Phase 18: House Interpreter

Interprets house significations, lords, occupants, and aspects.
"""

from typing import Dict, List


def interpret_house(house_number: int, lord: str, occupants: List[str], aspects_in: List[Dict], aspects_out: List[Dict]) -> Dict:
    """
    Phase 18: Interpret a house completely.
    
    Args:
        house_number: House number (1-12)
        lord: House lord planet
        occupants: List of planets in the house
        aspects_in: Aspects received by the house
        aspects_out: Aspects cast by the house lord
    
    Returns:
        Complete house interpretation
    """
    # House significations
    house_significations = {
        1: {
            "name": "Ascendant (Lagna)",
            "significations": ["Self", "Personality", "Physical appearance", "Head", "Overall life"],
            "body_part": "Head",
            "keywords": "Identity, self-expression, vitality"
        },
        2: {
            "name": "Wealth House (Dhana)",
            "significations": ["Wealth", "Family", "Speech", "Food", "Face", "Eyes"],
            "body_part": "Face, eyes",
            "keywords": "Money, resources, family, communication"
        },
        3: {
            "name": "Siblings House (Sahaja)",
            "significations": ["Siblings", "Courage", "Communication", "Short journeys", "Hands"],
            "body_part": "Hands, arms",
            "keywords": "Siblings, courage, communication, travel"
        },
        4: {
            "name": "Mother House (Matru)",
            "significations": ["Mother", "Home", "Education", "Property", "Chest", "Heart"],
            "body_part": "Chest, heart",
            "keywords": "Mother, home, property, education, comfort"
        },
        5: {
            "name": "Children House (Putra)",
            "significations": ["Children", "Education", "Creativity", "Intelligence", "Stomach"],
            "body_part": "Stomach",
            "keywords": "Children, education, creativity, speculation"
        },
        6: {
            "name": "Enemies House (Ari)",
            "significations": ["Health", "Enemies", "Service", "Debts", "Diseases"],
            "body_part": "Lower abdomen",
            "keywords": "Health, enemies, service, obstacles"
        },
        7: {
            "name": "Marriage House (Kalatra)",
            "significations": ["Marriage", "Partnerships", "Spouse", "Business", "Public"],
            "body_part": "Genitals",
            "keywords": "Marriage, partnerships, business, relationships"
        },
        8: {
            "name": "Longevity House (Ayur)",
            "significations": ["Longevity", "Transformation", "Secrets", "Sudden events", "Occult"],
            "body_part": "Anus",
            "keywords": "Longevity, transformation, secrets, sudden changes"
        },
        9: {
            "name": "Fortune House (Bhagya)",
            "significations": ["Father", "Dharma", "Fortune", "Higher learning", "Luck", "Religion"],
            "body_part": "Thighs",
            "keywords": "Fortune, dharma, father, higher learning, spirituality"
        },
        10: {
            "name": "Career House (Karma)",
            "significations": ["Career", "Profession", "Reputation", "Status", "Knees"],
            "body_part": "Knees",
            "keywords": "Career, profession, reputation, public image"
        },
        11: {
            "name": "Gains House (Labha)",
            "significations": ["Gains", "Income", "Friends", "Elder siblings", "Ambitions"],
            "body_part": "Shins",
            "keywords": "Gains, income, friends, aspirations"
        },
        12: {
            "name": "Losses House (Vyaya)",
            "significations": ["Losses", "Expenses", "Foreign lands", "Spirituality", "Liberation"],
            "body_part": "Feet",
            "keywords": "Losses, expenses, foreign, spirituality, moksha"
        }
    }
    
    house_info = house_significations.get(house_number, {
        "name": f"House {house_number}",
        "significations": [],
        "keywords": "General life area"
    })
    
    # Build interpretation
    interpretation = f"""
{house_info['name']} (House {house_number}):

Significations:
{', '.join(house_info['significations'])}

Keywords: {house_info['keywords']}
Body Part: {house_info.get('body_part', 'N/A')}

House Lord:
{lord} is the lord of {house_number}th house. The position and strength of {lord} determines the quality of this house.

Occupants:
"""
    
    if occupants:
        interpretation += f"Planets in this house: {', '.join(occupants)}\n"
        interpretation += "These planets influence the significations of this house.\n"
    else:
        interpretation += "No planets in this house. House significations depend on the lord's position.\n"
    
    # Aspects received
    if aspects_in:
        interpretation += "\nAspects Received:\n"
        for aspect in aspects_in:
            aspecting_planet = aspect.get("planet", "Unknown")
            aspect_type = aspect.get("type", "general")
            interpretation += f"• {aspecting_planet} aspects this house ({aspect_type} aspect)\n"
    
    # House strength assessment
    benefics = ["Jupiter", "Venus", "Mercury", "Moon"]
    malefics = ["Saturn", "Mars", "Rahu", "Ketu", "Sun"]
    
    benefic_occupants = [p for p in occupants if p in benefics]
    malefic_occupants = [p for p in occupants if p in malefics]
    
    if benefic_occupants:
        interpretation += f"\nPositive: Benefic planets ({', '.join(benefic_occupants)}) strengthen this house.\n"
    
    if malefic_occupants:
        interpretation += f"\nChallenges: Malefic planets ({', '.join(malefic_occupants)}) may create obstacles in this area.\n"
    
    # House type classification
    kendras = [1, 4, 7, 10]
    trikonas = [5, 9]
    dusthanas = [6, 8, 12]
    upachayas = [3, 6, 10, 11]
    
    house_type = []
    if house_number in kendras:
        house_type.append("Kendra (Angular) - Very important")
    if house_number in trikonas:
        house_type.append("Trikona (Trine) - Highly auspicious")
    if house_number in dusthanas:
        house_type.append("Dusthana (Inauspicious) - Challenges indicated")
    if house_number in upachayas:
        house_type.append("Upachaya (Growth) - Improves over time")
    
    if house_type:
        interpretation += f"\nHouse Type: {', '.join(house_type)}\n"
    
    return {
        "house_number": house_number,
        "house_name": house_info['name'],
        "significations": house_info['significations'],
        "lord": lord,
        "occupants": occupants,
        "aspects_in": aspects_in,
        "aspects_out": aspects_out,
        "house_type": house_type,
        "benefic_occupants": benefic_occupants,
        "malefic_occupants": malefic_occupants,
        "interpretation": interpretation.strip()
    }

