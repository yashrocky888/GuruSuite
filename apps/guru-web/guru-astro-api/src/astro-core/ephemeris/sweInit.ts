/**
 * ⚠️ DEPRECATED - DO NOT USE ⚠️
 * 
 * This file is DISABLED. All astrology calculations are now performed by the guru-api backend.
 * This file is kept for reference only and MUST NOT be imported or used.
 * 
 * The API is the single source of truth. UI must NEVER initialize Swiss Ephemeris.
 */

let swephInitialized = false;

export function initializeSwissEphemeris(): void {
  if (swephInitialized) {
    return;
  }

  try {
    // Try to load swisseph package
    const sweph = require('swisseph');
    
    // Set path to ephemeris files if needed
    // sweph.swe_set_ephe_path('./ephemeris');
    
    swephInitialized = true;
    console.log('✅ Swiss Ephemeris initialized');
  } catch (error) {
    // If swisseph not available, use fallback mode
    console.warn('⚠️ Swiss Ephemeris not available, using fallback calculations');
    swephInitialized = true; // Mark as initialized to allow fallback
  }
}

export function isSwephInitialized(): boolean {
  return swephInitialized;
}

