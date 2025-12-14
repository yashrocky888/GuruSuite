"""
Phase 13: Match Engine

Orchestrates all matching calculations (Gun Milan, Porutham, Manglik, Advanced).
"""

from typing import Dict
from src.matching.gun_milan import gun_milan
from src.matching.porutham import porutham
from src.matching.manglik import check_manglik, check_manglik_cancellation
from src.matching.compatibility import advanced_compatibility
from src.jyotish.dasha_engine import calculate_vimshottari_dasha
from datetime import datetime
import swisseph as swe


def full_match_report(boy_kundli: Dict, girl_kundli: Dict, boy_birth_dt: datetime, girl_birth_dt: datetime) -> Dict:
    """
    Phase 13: Generate complete match report.
    
    Combines:
    - Gun Milan (36 points)
    - Porutham (10 checks)
    - Manglik analysis
    - Advanced compatibility
    
    Args:
        boy_kundli: Boy's kundli dictionary
        girl_kundli: Girl's kundli dictionary
        boy_birth_dt: Boy's birth datetime
        girl_birth_dt: Girl's birth datetime
    
    Returns:
        Complete match report dictionary
    """
    # Calculate Gun Milan
    guna_result = gun_milan(boy_kundli, girl_kundli)
    
    # Calculate Porutham
    porutham_result = porutham(boy_kundli, girl_kundli)
    
    # Check Manglik
    boy_manglik = check_manglik(boy_kundli)
    girl_manglik = check_manglik(girl_kundli)
    manglik_cancellation = check_manglik_cancellation(boy_manglik, girl_manglik)
    
    # Get Dasha information for advanced compatibility
    from src.jyotish.kundli_engine import get_planet_positions
    boy_planets = get_planet_positions(
        swe.julday(boy_birth_dt.year, boy_birth_dt.month, boy_birth_dt.day,
                  boy_birth_dt.hour + boy_birth_dt.minute / 60.0, swe.GREG_CAL)
    )
    girl_planets = get_planet_positions(
        swe.julday(girl_birth_dt.year, girl_birth_dt.month, girl_birth_dt.day,
                  girl_birth_dt.hour + girl_birth_dt.minute / 60.0, swe.GREG_CAL)
    )
    
    boy_dasha = calculate_vimshottari_dasha(boy_birth_dt, boy_planets["Moon"])
    girl_dasha = calculate_vimshottari_dasha(girl_birth_dt, girl_planets["Moon"])
    
    # Advanced compatibility
    advanced_result = advanced_compatibility(boy_kundli, girl_kundli, boy_dasha, girl_dasha)
    
    # Calculate overall match percentage
    guna_percentage = guna_result["percentage"]
    porutham_percentage = porutham_result["percentage"]
    advanced_percentage = advanced_result["overall_index"]
    
    # Weighted overall score
    overall_score = (guna_percentage * 0.4) + (porutham_percentage * 10 * 0.3) + (advanced_percentage * 0.3)
    
    # Final verdict
    if overall_score >= 80:
        final_verdict = "Excellent Match"
        recommendation = "Highly recommended for marriage"
    elif overall_score >= 70:
        final_verdict = "Very Good Match"
        recommendation = "Recommended for marriage"
    elif overall_score >= 60:
        final_verdict = "Good Match"
        recommendation = "Suitable for marriage with some considerations"
    elif overall_score >= 50:
        final_verdict = "Moderate Match"
        recommendation = "Marriage possible but remedies recommended"
    else:
        final_verdict = "Challenging Match"
        recommendation = "Careful consideration and remedies strongly recommended"
    
    return {
        "guna_milan": guna_result,
        "porutham": porutham_result,
        "manglik": {
            "boy": boy_manglik,
            "girl": girl_manglik,
            "cancellation": manglik_cancellation
        },
        "advanced": advanced_result,
        "overall": {
            "score": round(overall_score, 1),
            "percentage": round(overall_score, 1),
            "verdict": final_verdict,
            "recommendation": recommendation,
            "breakdown": {
                "guna_milan": round(guna_percentage, 1),
                "porutham": round(porutham_percentage, 1),
                "advanced": round(advanced_percentage, 1)
            }
        }
    }

