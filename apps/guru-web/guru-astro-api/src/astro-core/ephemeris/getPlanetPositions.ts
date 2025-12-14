/**
 * ⚠️ DEPRECATED - DO NOT USE ⚠️
 * 
 * This file is DISABLED. All astrology calculations are now performed by the guru-api backend.
 * This file is kept for reference only and MUST NOT be imported or used.
 * 
 * The API is the single source of truth. UI must NEVER calculate planetary positions.
 */

import { initializeSwissEphemeris } from './sweInit';
import { SWEPH_PLANETS, AYANAMSA } from '../utils/constants';

export interface SwePlanetPosition {
  longitude: number; // 0-360 degrees
  latitude: number;
  distance: number;
  speed: number; // degrees per day
  retrograde: boolean;
}

/**
 * Get planet position from Swiss Ephemeris
 */
export function getPlanetPosition(
  julianDay: number,
  planet: string,
  ayanamsa: number = AYANAMSA.LAHIRI
): SwePlanetPosition {
  initializeSwissEphemeris();
  
  try {
    // Try swisseph package (Node.js wrapper for Swiss Ephemeris)
    const sweph = require('swisseph');
    const planetNum = SWEPH_PLANETS[planet];
    
    if (planetNum === undefined) {
      throw new Error(`Unknown planet: ${planet}`);
    }

    // Set sidereal mode (ayanamsa)
    sweph.swe_set_sid_mode(ayanamsa, 0, 0);

    // Calculate planet position
    // SEFLG_SWIEPH = use Swiss Ephemeris files
    // SEFLG_SIDEREAL = sidereal zodiac
    const flags = sweph.SEFLG_SWIEPH | sweph.SEFLG_SIDEREAL;
    const result = sweph.swe_calc_ut(julianDay, planetNum, flags);
    
    if (result.error) {
      throw new Error(`Swiss Ephemeris error: ${result.error}`);
    }

    const [longitude, latitude, distance, speedLongitude] = result.data;

    // Check if retrograde (speed is negative)
    const retrograde = speedLongitude < 0;

    // Normalize longitude to 0-360
    let normalizedLongitude = longitude % 360;
    if (normalizedLongitude < 0) {
      normalizedLongitude += 360;
    }

    return {
      longitude: normalizedLongitude,
      latitude,
      distance,
      speed: Math.abs(speedLongitude),
      retrograde,
    };
  } catch (error: any) {
    // Fallback: If sweph not available, use simplified calculation
    console.warn('Swiss Ephemeris not available, using fallback calculation');
    return getPlanetPositionFallback(julianDay, planet, ayanamsa);
  }
}

/**
 * Fallback calculation if Swiss Ephemeris is not available
 * This is a simplified approximation
 */
function getPlanetPositionFallback(
  julianDay: number,
  planet: string,
  ayanamsa: number
): SwePlanetPosition {
  // Simplified calculation - in production, Swiss Ephemeris is required
  // This is just a placeholder
  const baseLongitude = (julianDay % 360) * 0.9856; // Approximate Sun motion
  
  let longitude = baseLongitude;
  if (planet === 'Moon') {
    longitude = (baseLongitude * 13.2) % 360; // Moon moves faster
  } else if (planet === 'Mars') {
    longitude = (baseLongitude * 0.524) % 360;
  } else if (planet === 'Mercury') {
    longitude = (baseLongitude * 4.1) % 360;
  } else if (planet === 'Jupiter') {
    longitude = (baseLongitude * 0.083) % 360;
  } else if (planet === 'Venus') {
    longitude = (baseLongitude * 1.6) % 360;
  } else if (planet === 'Saturn') {
    longitude = (baseLongitude * 0.033) % 360;
  } else if (planet === 'Rahu') {
    longitude = (baseLongitude * 0.053) % 360;
  } else if (planet === 'Ketu') {
    longitude = ((baseLongitude * 0.053) + 180) % 360;
  }
  
  // Apply ayanamsa (Lahiri = ~24°)
  const ayanamsaValue = ayanamsa === 1 ? 24.0 : 23.5; // Simplified
  longitude = (longitude - ayanamsaValue + 360) % 360;
  
  return {
    longitude,
    latitude: 0,
    distance: 1,
    speed: 1,
    retrograde: false,
  };
}

/**
 * Get all planet positions
 */
export function getAllPlanetPositions(
  julianDay: number,
  ayanamsa: number = AYANAMSA.LAHIRI
): Record<string, SwePlanetPosition> {
  const planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu'];
  const positions: Record<string, SwePlanetPosition> = {};

  for (const planet of planets) {
    try {
      positions[planet] = getPlanetPosition(julianDay, planet, ayanamsa);
    } catch (error) {
      console.error(`Error calculating ${planet}:`, error);
      // Continue with other planets
    }
  }

  // Calculate Ketu (opposite of Rahu)
  if (positions.Rahu) {
    positions.Ketu = {
      longitude: (positions.Rahu.longitude + 180) % 360,
      latitude: -positions.Rahu.latitude,
      distance: positions.Rahu.distance,
      speed: positions.Rahu.speed,
      retrograde: positions.Rahu.retrograde,
    };
  }

  return positions;
}

/**
 * Calculate Lagna (Ascendant) using Swiss Ephemeris
 */
export function calculateLagna(
  julianDay: number,
  localSiderealTime: number,
  latitude: number,
  houseSystem: number = 1 // Placidus = 1
): number {
  initializeSwissEphemeris();
  
  const sweph = require('swisseph');
  
  // Calculate house cusps
  const houses = sweph.swe_houses(julianDay, latitude, 0, houseSystem);
  
  if (houses.error) {
    throw new Error(`House calculation error: ${houses.error}`);
  }

  // First house cusp is the ascendant
  const ascendant = houses.cusp[1]; // cusp[1] is house 1
  
  // Normalize to 0-360
  let normalizedAsc = ascendant % 360;
  if (normalizedAsc < 0) {
    normalizedAsc += 360;
  }

  return normalizedAsc;
}

