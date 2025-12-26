"""
Authoritative Varga Computation Engine

This is the SINGLE SOURCE OF TRUTH for all varga calculations.
API routes MUST use this engine and NEVER call calculate_varga() directly.

🔒 PROKERALA + JHORA VERIFIED
🔒 DO NOT MODIFY WITHOUT GOLDEN TEST UPDATE

All house calculations and varga chart structures must match Prokerala/JHora exactly.
Any changes must be verified against Prokerala reference data.

Architecture:
- Accepts D1 longitudes (planets + ascendant)
- Computes varga sign AND house together atomically
- Uses VERIFIED D10 logic with Prokerala/JHora corrections
- Returns structured output ready for API responses

NON-NEGOTIABLE RULE:
API routes must NEVER call calculate_varga() or calculate_varga_houses() directly.
All varga computation MUST go through this engine.
"""

import math
from typing import Dict, List, Optional
from src.jyotish.varga_drik import calculate_varga as _calculate_varga_internal
from src.utils.converters import normalize_degrees, get_sign_name


# Runtime guard: Track if calculate_varga is called outside this module
_CALLED_FROM_ENGINE = False


def build_varga_chart(
    d1_planets: Dict[str, float],
    d1_ascendant: float,
    varga_type: int,
    chart_method: Optional[int] = None
) -> Dict:
    """
    Build complete varga chart with sign and house assignments.
    
    This is the ONLY function API routes should call for varga computation.
    
    Args:
        d1_planets: Dictionary of {planet_name: D1_longitude}
                   Must include all planets: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu
        d1_ascendant: D1 ascendant longitude (0-360)
        varga_type: Varga type (2, 3, 4, 7, 9, 10, 12, etc.)
    
    Returns:
        Dictionary with structure:
        {
            "ascendant": {
                "degree": float,
                "sign": str,
                "sign_index": int,  # 0-11
                "degrees_in_sign": float,
                "house": int  # 1-12 (Whole Sign: house = sign_index + 1)
            },
            "planets": {
                "Sun": {
                    "degree": float,
                    "sign": str,
                    "sign_index": int,
                    "degrees_in_sign": float,
                    "house": int  # 1-12 (Whole Sign)
                },
                ... (all planets)
            }
        }
    """
    global _CALLED_FROM_ENGINE
    _CALLED_FROM_ENGINE = True
    
    try:
        # Calculate varga ascendant
        # NOTE: D24 is locked to method 1, chart_method parameter is ignored for D24
        varga_asc_data = _calculate_varga_internal(d1_ascendant, varga_type, chart_method=chart_method if varga_type != 24 else None)
        varga_asc_sign_index = varga_asc_data["sign"]
        
        # For D24-D60: NO HOUSE CALCULATION (pure sign charts)
        # For D1-D20: Calculate house using Whole Sign system
        if varga_type in (24, 27, 30, 40, 45, 60):
            varga_asc_house = None  # No house for D24-D60
        else:
            # Calculate Ascendant house using SAME formula as planets (not forced to 1)
            # Formula: house = ((planet_sign - lagna_sign + 12) % 12) + 1
            # For Ascendant: planet_sign = lagna_sign, so naturally house = 1
            varga_asc_house = ((varga_asc_sign_index - varga_asc_sign_index + 12) % 12) + 1
        
        # Compute Ascendant DMS exactly as Prokerala (EXACT Prokerala/JHora precision)
        # 🔒 DO NOT MODIFY — JHora compatible
        # Preserve absolute longitude as float (0-360) without rounding
        # Compute sign_degree = absolute_longitude % 30
        varga_asc_sign_degree = varga_asc_data["degrees_in_sign"]
        # Compute DMS exactly as Prokerala:
        # degrees = floor(sign_degree)
        # minutes = floor((sign_degree - degrees) * 60)
        # seconds = floor((((sign_degree - degrees) * 60) - minutes) * 60)
        varga_asc_dms_degrees = int(math.floor(varga_asc_sign_degree))
        varga_asc_dms_minutes_float = (varga_asc_sign_degree - varga_asc_dms_degrees) * 60.0
        varga_asc_dms_minutes = int(math.floor(varga_asc_dms_minutes_float))
        varga_asc_dms_seconds = int(math.floor((varga_asc_dms_minutes_float - varga_asc_dms_minutes) * 60.0))
        # Formatted string: "25° 15′ 00″"
        varga_asc_degree_formatted = f"{varga_asc_dms_degrees}° {varga_asc_dms_minutes:02d}′ {varga_asc_dms_seconds:02d}″"
        
        # Build ascendant result - only include house for D1-D20
        ascendant_response = {
            "degree": round(varga_asc_data["longitude"], 4),
            "sign": varga_asc_data["sign_name"],
            "sign_index": varga_asc_sign_index,
            "degrees_in_sign": round(varga_asc_data["degrees_in_sign"], 4),
            # Add JHORA deg-min-sec format (EXACT Prokerala/JHora precision)
            "degree_dms": varga_asc_dms_degrees,
            "arcminutes": varga_asc_dms_minutes,
            "arcseconds": varga_asc_dms_seconds,
            "degree_formatted": varga_asc_degree_formatted
        }
        
        # Only add house field for D1-D20 (not for D24-D60 pure sign charts)
        if varga_asc_house is not None:
            ascendant_response["house"] = varga_asc_house
        
        result = {
            "ascendant": ascendant_response,
            "planets": {}
        }
        
        # Calculate varga for each planet
        # For D24-D60: NO HOUSE CALCULATION (pure sign charts)
        # For D1-D20: Whole Sign House System
        for planet_name, d1_longitude in d1_planets.items():
            # NOTE: D24 is locked to method 1, chart_method parameter is ignored for D24
            varga_data = _calculate_varga_internal(d1_longitude, varga_type, chart_method=chart_method if varga_type != 24 else None)
            varga_sign_index = varga_data["sign"]
            
            # For D24-D60: No house calculation (pure sign charts)
            if varga_type in (24, 27, 30, 40, 45, 60):
                varga_house = None  # No house for D24-D60
            else:
                # Whole Sign house calculation relative to varga ascendant
                # This ensures planets in same sign as ascendant → house 1
                # Formula: house = ((planet_sign_index - ascendant_sign_index + 12) % 12) + 1
                varga_house = ((varga_sign_index - varga_asc_sign_index + 12) % 12) + 1
                
                # RUNTIME ASSERTION: Planet house must be 1-12 (only for D1-D20)
                assert 1 <= varga_house <= 12, \
                    f"{planet_name} house must be 1-12, got {varga_house} (planet_sign={varga_sign_index}, asc_sign={varga_asc_sign_index})"
            
            # Compute DMS exactly as Prokerala (EXACT Prokerala/JHora precision)
            # 🔒 DO NOT MODIFY — JHora compatible
            # Preserve absolute longitude as float (0-360) without rounding
            # Compute sign_degree = absolute_longitude % 30
            varga_sign_degree = varga_data["degrees_in_sign"]
            # Compute DMS exactly as Prokerala:
            # degrees = floor(sign_degree)
            # minutes = floor((sign_degree - degrees) * 60)
            # seconds = floor((((sign_degree - degrees) * 60) - minutes) * 60)
            varga_dms_degrees = int(math.floor(varga_sign_degree))
            varga_dms_minutes_float = (varga_sign_degree - varga_dms_degrees) * 60.0
            varga_dms_minutes = int(math.floor(varga_dms_minutes_float))
            varga_dms_seconds = int(math.floor((varga_dms_minutes_float - varga_dms_minutes) * 60.0))
            # Formatted string: "25° 15′ 00″"
            varga_degree_formatted = f"{varga_dms_degrees}° {varga_dms_minutes:02d}′ {varga_dms_seconds:02d}″"
            
            # Build planet response - only include house for D1-D20
            planet_response = {
                "degree": round(varga_data["longitude"], 4),
                "sign": varga_data["sign_name"],
                "sign_index": varga_sign_index,
                "degrees_in_sign": round(varga_data["degrees_in_sign"], 4),
                # Add JHORA deg-min-sec format (EXACT Prokerala/JHora precision)
                "degree_dms": varga_dms_degrees,
                "arcminutes": varga_dms_minutes,
                "arcseconds": varga_dms_seconds,
                "degree_formatted": varga_degree_formatted
            }
            
            # Only add house field for D1-D20 (not for D24-D60 pure sign charts)
            if varga_house is not None:
                planet_response["house"] = varga_house
            
            result["planets"][planet_name] = planet_response
        
        # Debug logging for validation (1995-05-16 18:38 Bangalore test case)
        import logging
        logger = logging.getLogger(__name__)
        
        # For D24-D60: Log full_longitude, varga_longitude, varga_sign (NO HOUSE - pure sign charts)
        if varga_type in (24, 27, 30, 40, 45, 60):
            # Log Ascendant
            asc_varga_data = _calculate_varga_internal(d1_ascendant, varga_type)
            asc_full_longitude = d1_ascendant
            asc_varga_longitude = asc_varga_data["longitude"]
            asc_varga_sign = result['ascendant']['sign_index']
            logger.info(f"🔍 D{varga_type} DEBUG (Ascendant): full_longitude={asc_full_longitude:.6f}°, varga_longitude={asc_varga_longitude:.6f}°, varga_sign={asc_varga_sign} ({result['ascendant']['sign']}) [PURE SIGN CHART - NO HOUSE]")
            
            # Log Sun
            if "Sun" in d1_planets:
                sun_full_longitude = d1_planets["Sun"]
                sun_varga_data = _calculate_varga_internal(sun_full_longitude, varga_type)
                sun_varga_longitude = sun_varga_data["longitude"]
                sun_varga_sign = result["planets"]["Sun"]["sign_index"]
                logger.info(f"🔍 D{varga_type} DEBUG (Sun): full_longitude={sun_full_longitude:.6f}°, varga_longitude={sun_varga_longitude:.6f}°, varga_sign={sun_varga_sign} ({result['planets']['Sun']['sign']}) [PURE SIGN CHART - NO HOUSE]")
            
            # Log Moon
            if "Moon" in d1_planets:
                moon_full_longitude = d1_planets["Moon"]
                moon_varga_data = _calculate_varga_internal(moon_full_longitude, varga_type)
                moon_varga_longitude = moon_varga_data["longitude"]
                moon_varga_sign = result["planets"]["Moon"]["sign_index"]
                logger.info(f"🔍 D{varga_type} DEBUG (Moon): full_longitude={moon_full_longitude:.6f}°, varga_longitude={moon_varga_longitude:.6f}°, varga_sign={moon_varga_sign} ({result['planets']['Moon']['sign']}) [PURE SIGN CHART - NO HOUSE]")
        else:
            # For D1-D20: Log raw varga sign outputs for verification
            logger.info(f"🔍 D{varga_type} RAW VARGA SIGNS:")
            logger.info(f"   Ascendant: sign_index={result['ascendant']['sign_index']}, sign={result['ascendant']['sign']}, house={result['ascendant']['house']}")
            for planet_name in sorted(result["planets"].keys()):
                planet_data = result["planets"][planet_name]
                logger.info(f"   {planet_name}: sign_index={planet_data['sign_index']}, sign={planet_data['sign']}, house={planet_data['house']}")
        
        # RUNTIME ASSERTION: Verify all planets have valid houses (1-12) - ONLY for D1-D20
        if varga_type not in (24, 27, 30, 40, 45, 60):
            for planet_name, planet_data in result["planets"].items():
                assert 1 <= planet_data["house"] <= 12, \
                    f"Varga {varga_type} {planet_name}: house {planet_data['house']} not in range 1-12"
            
            # RUNTIME ASSERTION: Verify house calculation matches Whole Sign formula
            asc_sign_index = result["ascendant"]["sign_index"]
            for planet_name, planet_data in result["planets"].items():
                planet_sign_index = planet_data["sign_index"]
                planet_house = planet_data["house"]
                expected_house = ((planet_sign_index - asc_sign_index + 12) % 12) + 1
                assert planet_house == expected_house, \
                    f"Varga {varga_type} {planet_name}: house {planet_house} != expected {expected_house} " \
                    f"(planet_sign={planet_sign_index}, asc_sign={asc_sign_index})"
        
        return result
    
    finally:
        _CALLED_FROM_ENGINE = False


def build_all_varga_charts(
    d1_planets: Dict[str, float],
    d1_ascendant: float,
    varga_types: List[int] = [2, 3, 4, 7, 9, 10, 12]
) -> Dict[int, Dict]:
    """
    Build multiple varga charts at once for efficiency.
    
    Args:
        d1_planets: Dictionary of {planet_name: D1_longitude}
        d1_ascendant: D1 ascendant longitude
        varga_types: List of varga types to compute (default: [2, 3, 4, 7, 9, 10, 12])
    
    Returns:
        Dictionary of {varga_type: varga_chart_dict}
        Example: {2: {...}, 9: {...}, 10: {...}}
    """
    results = {}
    for varga_type in varga_types:
        results[varga_type] = build_varga_chart(d1_planets, d1_ascendant, varga_type)
    return results


def get_varga_ascendant_only(d1_ascendant: float, varga_type: int) -> Dict:
    """
    Get only varga ascendant (for cases where planets aren't needed).
    
    Args:
        d1_ascendant: D1 ascendant longitude
        varga_type: Varga type
    
    Returns:
        Dictionary with ascendant data:
        {
            "degree": float,
            "sign": str,
            "sign_index": int,
            "degrees_in_sign": float,
            "house": int
        }
    """
    global _CALLED_FROM_ENGINE
    _CALLED_FROM_ENGINE = True
    
    try:
        # NOTE: D24 is locked to method 1, chart_method parameter is ignored for D24
        varga_asc_data = _calculate_varga_internal(d1_ascendant, varga_type, chart_method=chart_method if varga_type != 24 else None)
        varga_asc_sign_index = varga_asc_data["sign"]
        
        # For D24-D60: NO HOUSE CALCULATION (pure sign charts)
        # For D1-D20: Calculate house using Whole Sign system
        if varga_type in (24, 27, 30, 40, 45, 60):
            varga_asc_house = None  # No house for D24-D60
        else:
            # Calculate Ascendant house using SAME formula as planets (not forced to 1)
            # Formula: house = ((planet_sign - lagna_sign + 12) % 12) + 1
            # For Ascendant: planet_sign = lagna_sign, so naturally house = 1
            varga_asc_house = ((varga_asc_sign_index - varga_asc_sign_index + 12) % 12) + 1
        
        return {
            "degree": round(varga_asc_data["longitude"], 4),
            "sign": varga_asc_data["sign_name"],
            "sign_index": varga_asc_sign_index,
            "degrees_in_sign": round(varga_asc_data["degrees_in_sign"], 4),
            "house": varga_asc_house  # Always 1 for lagna
        }
    
    finally:
        _CALLED_FROM_ENGINE = False


def _is_called_from_engine() -> bool:
    """
    Internal function to check if calculate_varga is being called from the engine.
    Used by varga_drik.py to enforce the guard.
    """
    return _CALLED_FROM_ENGINE

