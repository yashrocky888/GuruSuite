/**
 * ⚠️ DEPRECATED - DO NOT USE ⚠️
 * 
 * This file is DISABLED. All astrology calculations are now performed by the guru-api backend.
 * This file is kept for reference only and MUST NOT be imported or used.
 * 
 * The API is the single source of truth. UI must NEVER calculate nakshatras.
 */

import { NAKSHATRAS, NAKSHATRA_LORDS, NAKSHATRA_SPAN } from '../utils/constants';

export interface NakshatraInfo {
  nakshatra: string;
  pada: number; // 1-4
  lord: string;
  degree: number; // Degree within nakshatra (0-13.333)
  startDegree: number; // Starting degree of nakshatra
  endDegree: number; // Ending degree of nakshatra
}

/**
 * Calculate nakshatra from longitude (0-360)
 */
export function calculateNakshatra(longitude: number): NakshatraInfo {
  // Normalize longitude
  let normalizedLong = longitude % 360;
  if (normalizedLong < 0) {
    normalizedLong += 360;
  }

  // Calculate which nakshatra (0-26)
  const nakshatraIndex = Math.floor(normalizedLong / NAKSHATRA_SPAN);
  const nakshatra = NAKSHATRAS[nakshatraIndex % 27];
  
  // Calculate degree within nakshatra
  const degreeInNakshatra = normalizedLong % NAKSHATRA_SPAN;
  
  // Calculate pada (1-4, each pada = 3.333 degrees)
  const pada = Math.floor(degreeInNakshatra / (NAKSHATRA_SPAN / 4)) + 1;
  
  // Get lord
  const lord = NAKSHATRA_LORDS[nakshatraIndex % 27];
  
  // Calculate start and end degrees
  const startDegree = nakshatraIndex * NAKSHATRA_SPAN;
  const endDegree = startDegree + NAKSHATRA_SPAN;

  return {
    nakshatra,
    pada: Math.min(pada, 4), // Ensure pada is 1-4
    lord,
    degree: parseFloat(degreeInNakshatra.toFixed(2)),
    startDegree,
    endDegree,
  };
}

