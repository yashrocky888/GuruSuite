"""
Calculate houses for divisional charts (D7, D10, D12, etc.)

For divisional charts:
1. Calculate varga ascendant by applying varga formula to D1 ascendant
2. Calculate varga houses by applying varga formula to each D1 house cusp
3. Place planets in houses based on their varga longitudes
"""

from typing import Dict, List
from src.jyotish.varga_drik import calculate_varga
from src.utils.converters import normalize_degrees


def calculate_varga_houses(d1_ascendant: float, d1_houses: List[float], varga_type: int, varga_ascendant: float = None) -> Dict:
    """
    Calculate houses for a divisional chart.
    
    Args:
        d1_ascendant: D1 (main chart) ascendant longitude
        d1_houses: List of 12 D1 house cusp longitudes
        varga_type: Varga type (7, 10, 12, etc.)
        varga_ascendant: Optional pre-calculated varga ascendant (for D12, use base formula)
    
    Returns:
        Dictionary with:
            - ascendant: Varga ascendant longitude
            - houses: List of 12 varga house cusp longitudes
    """
    # Calculate varga ascendant (or use provided one)
    if varga_ascendant is not None:
        varga_ascendant_longitude = varga_ascendant
    else:
        # 🔒 D4 SPECIAL: Pass is_ascendant=True for Lagna (D4 Lagna is SIGN-ONLY)
        varga_asc_data = calculate_varga(d1_ascendant, varga_type, is_ascendant=True)
        varga_ascendant_longitude = varga_asc_data["longitude"]
    
    # Calculate varga houses by applying varga formula to each D1 house cusp
    varga_houses = []
    for house_cusp in d1_houses:
        # House cusps are NOT ascendant, so is_ascendant=False (default)
        house_varga_data = calculate_varga(house_cusp, varga_type)
        varga_houses.append(house_varga_data["longitude"])
    
    return {
        "ascendant": varga_ascendant_longitude,
        "houses": varga_houses
    }


def get_planet_house_whole_sign(planet_longitude: float, ascendant_longitude: float) -> int:
    """
    Get house using Whole Sign system for divisional charts.
    
    🔒 DO NOT MODIFY — JHora compatible
    Whole Sign House System:
    - House 1 = Ascendant sign
    - House 2 = Next sign clockwise
    - etc.
    
    Formula: house = ((planet_sign_index - ascendant_sign_index + 12) % 12) + 1
    
    Args:
        planet_longitude: Planet's longitude in the varga chart (0-360)
        ascendant_longitude: Ascendant longitude in the varga chart (0-360)
    
    Returns:
        House number (1-12)
    """
    planet_deg = normalize_degrees(planet_longitude)
    asc_deg = normalize_degrees(ascendant_longitude)
    
    # Get sign indices (0-11): Aries=0, Taurus=1, ..., Pisces=11
    planet_sign_index = int(planet_deg / 30.0)
    asc_sign_index = int(asc_deg / 30.0)
    
    # Whole Sign house calculation:
    # House 1 = ascendant sign
    # House 2 = next sign clockwise from ascendant
    # Formula: ((planet_sign - asc_sign + 12) % 12) + 1
    # The +12 ensures positive result before modulo
    house_num = ((planet_sign_index - asc_sign_index + 12) % 12) + 1
    
    # RUNTIME ASSERTION: House must be 1-12
    assert 1 <= house_num <= 12, f"House must be 1-12, got {house_num} (planet_sign={planet_sign_index}, asc_sign={asc_sign_index})"
    
    return house_num


def get_planet_house_in_varga(planet_varga_longitude: float, varga_ascendant: float, varga_houses: List[float]) -> int:
    """
    Get house number for a planet in a divisional chart using JHORA method.
    
    JHORA uses a specific house calculation method for divisional charts that
    is based on sign positions with varga-specific adjustments.
    
    Args:
        planet_varga_longitude: Planet's longitude in the varga chart
        varga_ascendant: Ascendant longitude in the varga chart
        varga_houses: List of 12 house cusp longitudes in the varga chart
    
    Returns:
        House number (1-12)
    """
    planet_deg = normalize_degrees(planet_varga_longitude)
    asc_deg = normalize_degrees(varga_ascendant)
    
    # Get sign indices (0-11)
    planet_sign = int(planet_deg / 30.0)
    asc_sign = int(asc_deg / 30.0)
    
    # Convert to 1-12 format
    planet_sign_12 = planet_sign + 1
    asc_sign_12 = asc_sign + 1
    
    # JHORA house calculation varies by varga type
    # Determine varga type from the house cusps pattern or use a different method
    # For now, use sign-based calculation with varga-specific rules
    
    # D7 rule: sign+1 for most, sign for signs 2-3
    # D10 and D12 have more complex patterns
    
    # Try using house cusps first (more accurate)
    normalized_houses = [normalize_degrees(h) for h in varga_houses]
    
    # Find which house the planet is in based on house cusps
    for house_num in range(1, 13):
        house_idx = house_num - 1
        house_cusp = normalized_houses[house_idx]
        
        # Next house cusp (wrap around for house 12)
        next_house_idx = house_num % 12
        next_house_cusp = normalized_houses[next_house_idx]
        
        # Handle wrap-around at 360°
        if house_cusp > next_house_cusp:  # Wrap around 360
            if planet_deg >= house_cusp or planet_deg < next_house_cusp:
                return house_num
        else:
            # Normal case: house_cusp <= planet < next_house_cusp
            if house_cusp <= planet_deg < next_house_cusp:
                return house_num
    
    # Fallback to sign-based calculation if house cusp method doesn't work
    # This is a simplified version - may need adjustment based on varga type
    house = (planet_sign_12 + 1) % 12
    if house == 0:
        house = 12
    
    # Exception: If planet sign equals ascendant sign, house = sign
    if planet_sign == asc_sign:
        house = planet_sign_12
    
    return house


def calculate_all_varga_charts_with_houses(
    d1_ascendant: float,
    d1_houses: List[float],
    d1_planets: Dict[str, float]
) -> Dict:
    """
    Calculate all varga charts with house placements.
    
    Args:
        d1_ascendant: D1 ascendant longitude
        d1_houses: List of 12 D1 house cusp longitudes
        d1_planets: Dictionary of planet names to D1 longitudes
    
    Returns:
        Dictionary with D7, D10, D12 charts including houses
    """
    results = {}
    
    for varga_type in [7, 10, 12]:
        varga_name = {7: "D7", 10: "D10", 12: "D12"}[varga_type]
        
        # Calculate varga houses
        varga_houses_data = calculate_varga_houses(d1_ascendant, d1_houses, varga_type)
        varga_ascendant = varga_houses_data["ascendant"]
        varga_houses = varga_houses_data["houses"]
        
        # Calculate planet positions and house placements
        planets = {}
        for planet_name, d1_longitude in d1_planets.items():
            planet_varga_data = calculate_varga(d1_longitude, varga_type)
            planet_varga_longitude = planet_varga_data["longitude"]
            # Use Whole Sign houses for divisional charts (standard in Vedic astrology)
            house_num = get_planet_house_whole_sign(planet_varga_longitude, varga_ascendant)
            
            planets[planet_name] = {
                "longitude": planet_varga_longitude,
                "sign": planet_varga_data["sign"],
                "sign_name": planet_varga_data["sign_name"],
                "degrees_in_sign": planet_varga_data["degrees_in_sign"],
                "house": house_num
            }
        
        results[varga_name] = {
            "ascendant": varga_ascendant,
            "houses": varga_houses,
            "planets": planets
        }
    
    return results

