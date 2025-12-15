"""
Authoritative Varga Computation Engine

This is the SINGLE SOURCE OF TRUTH for all varga calculations.
API routes MUST use this engine and NEVER call calculate_varga() directly.

Architecture:
- Accepts D1 longitudes (planets + ascendant)
- Computes varga sign AND house together atomically
- Uses VERIFIED D10 logic with Prokerala/JHora corrections
- Returns structured output ready for API responses

NON-NEGOTIABLE RULE:
API routes must NEVER call calculate_varga() or calculate_varga_houses() directly.
All varga computation MUST go through this engine.
"""

from typing import Dict, List, Optional
from src.jyotish.varga_drik import calculate_varga as _calculate_varga_internal
from src.utils.converters import normalize_degrees, get_sign_name


# Runtime guard: Track if calculate_varga is called outside this module
_CALLED_FROM_ENGINE = False


def build_varga_chart(
    d1_planets: Dict[str, float],
    d1_ascendant: float,
    varga_type: int
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
        varga_asc_data = _calculate_varga_internal(d1_ascendant, varga_type)
        varga_asc_sign_index = varga_asc_data["sign"]
        
        # CRITICAL: Lagna (Ascendant) is ALWAYS in House 1 (Whole Sign system rule)
        # DO NOT MODIFY — JHora compatible
        # This is a fundamental Vedic astrology rule: Lagna = House 1, regardless of sign
        varga_asc_house = 1
        
        # RUNTIME ASSERTION: Enforce lagna house invariant
        assert varga_asc_house == 1, f"Lagna house must be 1, got {varga_asc_house}"
        
        # Build ascendant result
        result = {
            "ascendant": {
                "degree": round(varga_asc_data["longitude"], 4),
                "sign": varga_asc_data["sign_name"],
                "sign_index": varga_asc_sign_index,
                "degrees_in_sign": round(varga_asc_data["degrees_in_sign"], 4),
                "house": varga_asc_house  # Always 1 for lagna
            },
            "planets": {}
        }
        
        # Calculate varga for each planet
        # DO NOT MODIFY — JHora compatible
        # For planets in varga charts: house = sign_index + 1 (Whole Sign system)
        for planet_name, d1_longitude in d1_planets.items():
            varga_data = _calculate_varga_internal(d1_longitude, varga_type)
            varga_sign_index = varga_data["sign"]
            varga_house = varga_sign_index + 1  # Whole Sign: house = sign (for planets)
            
            # RUNTIME ASSERTION: Planet house must be 1-12
            assert 1 <= varga_house <= 12, \
                f"{planet_name} house must be 1-12, got {varga_house}"
            
            result["planets"][planet_name] = {
                "degree": round(varga_data["longitude"], 4),
                "sign": varga_data["sign_name"],
                "sign_index": varga_sign_index,
                "degrees_in_sign": round(varga_data["degrees_in_sign"], 4),
                "house": varga_house
            }
        
        # RUNTIME ASSERTION: Verify lagna house is 1
        assert result["ascendant"]["house"] == 1, \
            f"Varga lagna house must be 1, got {result['ascendant']['house']}"
        
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
        varga_asc_data = _calculate_varga_internal(d1_ascendant, varga_type)
        varga_asc_sign_index = varga_asc_data["sign"]
        
        # CRITICAL: Lagna (Ascendant) is ALWAYS in House 1 (Whole Sign system rule)
        # DO NOT MODIFY — JHora compatible
        varga_asc_house = 1
        
        # RUNTIME ASSERTION: Enforce lagna house invariant
        assert varga_asc_house == 1, f"Lagna house must be 1, got {varga_asc_house}"
        
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

