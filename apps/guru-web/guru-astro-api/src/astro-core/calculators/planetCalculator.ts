/**
 * ⚠️ DEPRECATED - DO NOT USE ⚠️
 * 
 * This file is DISABLED. All astrology calculations are now performed by the guru-api backend.
 * This file is kept for reference only and MUST NOT be imported or used.
 * 
 * The API is the single source of truth. UI must NEVER calculate planets.
 */

import { SwePlanetPosition } from '../ephemeris/getPlanetPositions';
import { PlanetPosition } from '../../types';
import { longitudeToSignDegree } from '../utils/constants';
import { calculateNakshatra } from './nakshatraCalculator';

/**
 * Calculate complete planet information
 */
export function calculatePlanetInfo(
  planet: string,
  position: SwePlanetPosition
): PlanetPosition {
  // Get sign and degree
  const signInfo = longitudeToSignDegree(position.longitude);
  
  // Get nakshatra
  const nakshatraInfo = calculateNakshatra(position.longitude);
  
  // Check combustion (planets too close to Sun)
  const combust = checkCombustion(planet, position);
  
  return {
    planet,
    longitude: position.longitude,
    latitude: position.latitude,
    distance: position.distance,
    speed: position.speed,
    retrograde: position.retrograde,
    sign: signInfo.sign,
    signNumber: signInfo.signNumber,
    degree: signInfo.degree,
    nakshatra: nakshatraInfo.nakshatra,
    pada: nakshatraInfo.pada,
    nakshatraLord: nakshatraInfo.lord,
    combust,
  };
}

/**
 * Check if planet is combust (too close to Sun)
 * Combustion limits:
 * - Mercury: 14° (before) to 12° (after)
 * - Venus: 10° (before) to 8° (after)
 * - Others: 8.5° (before) to 8.5° (after)
 */
function checkCombustion(planet: string, position: SwePlanetPosition): boolean {
  // This requires Sun's position - simplified check
  // In full implementation, compare with Sun's longitude
  if (planet === 'Sun' || planet === 'Moon' || planet === 'Rahu' || planet === 'Ketu') {
    return false; // These don't combust
  }
  
  // For now, return false - full implementation needs Sun position
  // TODO: Implement full combustion calculation
  return false;
}

/**
 * Calculate all planets with full information
 */
export function calculateAllPlanets(
  planetPositions: Record<string, SwePlanetPosition>
): PlanetPosition[] {
  const planets: PlanetPosition[] = [];
  
  for (const [planet, position] of Object.entries(planetPositions)) {
    try {
      const planetInfo = calculatePlanetInfo(planet, position);
      planets.push(planetInfo);
    } catch (error) {
      console.error(`Error calculating ${planet}:`, error);
    }
  }
  
  return planets;
}

