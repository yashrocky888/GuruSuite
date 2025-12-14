"""
Phase 6: Complete Yoga Detection Engine

This is the main yoga engine that combines all yoga detection modules
to provide comprehensive yoga analysis following JHora-style rules.
"""

from typing import Dict, List

from src.jyotish.yogas.planetary_yogas import detect_planetary_yogas
from src.jyotish.yogas.mahapurusha_yogas import detect_mahapurusha_yogas
from src.jyotish.yogas.house_yogas import detect_house_yogas
from src.jyotish.yogas.combination_yogas import detect_combination_yogas
from src.jyotish.yogas.raja_yogas import detect_advanced_raja_yogas
from src.jyotish.yogas.extended_yogas import detect_extended_yogas


def detect_all_yogas(planets: Dict, houses: List[Dict]) -> Dict:
    """
    Phase 6: Detect all yogas in the birth chart.
    
    This function combines all yoga detection modules to provide
    a complete analysis of 250+ classical yogas.
    
    Args:
        planets: Dictionary of planet positions with degrees, signs, houses
        houses: List of house data with signs and degrees
    
    Returns:
        Complete yoga analysis dictionary
    """
    all_yogas = []
    
    # 1. Planetary Placement Yogas
    planetary_yogas = detect_planetary_yogas(planets, houses)
    all_yogas.extend(planetary_yogas)
    
    # 2. Panch Mahapurusha Yogas
    mahapurusha_yogas = detect_mahapurusha_yogas(planets, houses)
    all_yogas.extend(mahapurusha_yogas)
    
    # 3. House-Based Yogas
    house_yogas = detect_house_yogas(planets, houses)
    all_yogas.extend(house_yogas)
    
    # 4. Combination Yogas
    combination_yogas = detect_combination_yogas(planets, houses)
    all_yogas.extend(combination_yogas)
    
    # 5. Advanced Raja Yogas
    advanced_raja_yogas = detect_advanced_raja_yogas(planets, houses)
    all_yogas.extend(advanced_raja_yogas)
    
    # 6. Extended Yogas (250+ total)
    extended_yogas = detect_extended_yogas(planets, houses)
    all_yogas.extend(extended_yogas)
    
    # Categorize yogas
    major_yogas = [y for y in all_yogas if y.get("category") == "Major"]
    moderate_yogas = [y for y in all_yogas if y.get("category") == "Moderate"]
    doshas = [y for y in all_yogas if y.get("category") == "Dosha"]
    
    # Group by type
    planetary = [y for y in all_yogas if y.get("type") == "Planetary"]
    house_based = [y for y in all_yogas if y.get("type") == "House"]
    mahapurusha = [y for y in all_yogas if y.get("type") == "Mahapurusha"]
    combination = [y for y in all_yogas if y.get("type") == "Combination"]
    raja = [y for y in all_yogas if y.get("type") == "Raja Yoga"]
    
    return {
        "total_yogas": len(all_yogas),
        "all_yogas": all_yogas,
        "major_yogas": major_yogas,
        "moderate_yogas": moderate_yogas,
        "doshas": doshas,
        "by_type": {
            "planetary": planetary,
            "house_based": house_based,
            "mahapurusha": mahapurusha,
            "combination": combination,
            "raja_yoga": raja
        },
        "summary": {
            "total": len(all_yogas),
            "major": len(major_yogas),
            "moderate": len(moderate_yogas),
            "doshas": len(doshas)
        }
    }

