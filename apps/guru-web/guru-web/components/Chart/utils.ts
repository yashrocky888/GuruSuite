/**
 * Chart Utilities - Pure Renderer (NO CALCULATIONS)
 * 
 * CRITICAL RULE: UI must NEVER calculate astrology.
 * This module ONLY provides type definitions and helper functions for display formatting.
 * 
 * API provides:
 * - Ascendant.house = 1 (always)
 * - Houses[] array with all 12 houses and signs
 * - Planets[].house for each planet
 * 
 * UI must use this data directly without any calculations.
 */

// API returns: { name: "Sun", sign: "Mesha", house: 1, ... }
export interface ApiPlanet {
  name: string;
  sign: string;
  house: number;
  degree?: number;
  degrees_in_sign?: number;
  nakshatra?: string;
  pada?: number;
  retrograde?: boolean;
  color?: string;
  speed?: number;
  longitude?: number;
  sign_index?: number;
  sign_sanskrit?: string;
}

export interface ApiKundliData {
  lagna?: number;
  lagnaSign?: string;
  lagnaSignSanskrit?: string;
  lagnaDegree?: number;
  lagnaDegreeInSign?: number;
  lagnaDegreeDms?: number;
  lagnaArcminutes?: number;
  lagnaArcseconds?: number;
  ascendantHouse?: number; // From API: Ascendant.house (always 1)
  planets: ApiPlanet[];
  ayanamsa?: string;
  system?: string;
  houses?: Array<{ 
    house: number; 
    sign: string; 
    sign_sanskrit?: string; 
    sign_index?: number;
    degree?: number; 
    degrees_in_sign?: number;
    lord?: string;
  }>;
  chartType?: string;
}

// Rashi names (Sanskrit in English)
export const RASHI_NAMES: Record<number, string> = {
  1: 'Mesha',
  2: 'Vrishabha',
  3: 'Mithuna',
  4: 'Karka',
  5: 'Simha',
  6: 'Kanya',
  7: 'Tula',
  8: 'Vrishchika',
  9: 'Dhanu',
  10: 'Makara',
  11: 'Kumbha',
  12: 'Meena',
};

// Sign name to number mapping
export const SIGN_TO_NUM: Record<string, number> = {
  'Mesha': 1, 'Vrishabha': 2, 'Mithuna': 3, 'Karka': 4,
  'Simha': 5, 'Kanya': 6, 'Tula': 7, 'Vrishchika': 8, 'Vrischika': 8,
  'Dhanu': 9, 'Makara': 10, 'Kumbha': 11, 'Meena': 12,
  'Aries': 1, 'Taurus': 2, 'Gemini': 3, 'Cancer': 4,
  'Leo': 5, 'Virgo': 6, 'Libra': 7, 'Scorpio': 8,
  'Sagittarius': 9, 'Capricorn': 10, 'Aquarius': 11, 'Pisces': 12,
};

// Planet abbreviations
export const PLANET_ABBR: Record<string, string> = {
  Sun: 'Su',
  Moon: 'Mo',
  Mars: 'Ma',
  Mercury: 'Me',
  Jupiter: 'Ju',
  Venus: 'Ve',
  Saturn: 'Sa',
  Rahu: 'Ra',
  Ketu: 'Ke',
};

/**
 * Get planet abbreviation
 */
export function getPlanetAbbr(planetName: string): string {
  return PLANET_ABBR[planetName] || planetName.substring(0, 2);
}

/**
 * Get sign name from number
 */
export function getSignName(signNum: number): string {
  return RASHI_NAMES[signNum] || 'Mesha';
}

/**
 * Get sign number from name
 */
export function getSignNum(signName: string): number {
  return SIGN_TO_NUM[signName] || 1;
}

/**
 * Convert English sign name to Sanskrit (Vedic) name
 */
export function convertToSanskritSign(englishName: string): string {
  const englishToSanskrit: Record<string, string> = {
    'Aries': 'Mesha',
    'Taurus': 'Vrishabha',
    'Gemini': 'Mithuna',
    'Cancer': 'Karka',
    'Leo': 'Simha',
    'Virgo': 'Kanya',
    'Libra': 'Tula',
    'Scorpio': 'Vrishchika',
    'Sagittarius': 'Dhanu',
    'Capricorn': 'Makara',
    'Aquarius': 'Kumbha',
    'Pisces': 'Meena',
  };
  
  if (SIGN_TO_NUM[englishName]) {
    return englishName;
  }
  
  return englishToSanskrit[englishName] || englishName;
}

/**
 * DEPRECATED: normalizeKundliData() DELETED
 * 
 * This function was mapping API data to a normalized format.
 * Charts must now render DIRECTLY from API structure:
 * 
 * API Structure:
 * {
 *   Ascendant: { sign, house: 1, ... },
 *   Houses: [{ house: 1, sign, ... }, ...],
 *   Planets: { Sun: { sign, house, ... }, ... }
 * }
 * 
 * Charts must use:
 * - api.Houses[houseNum - 1] for house data
 * - api.Planets[planetName].house for planet placement
 * - api.Ascendant.house (always = 1) for ascendant
 * 
 * NO NORMALIZATION. NO TRANSFORMATION. DIRECT RENDERING ONLY.
 */
