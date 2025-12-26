/**
 * House Calculation Utilities
 * 
 * 🔒 ASTROLOGY LOCK
 * UI must NEVER calculate astrology.
 * API is the single source of truth.
 * 
 * This file provides utilities for house-related operations.
 * The API already provides house numbers - these utilities are for
 * defensive checks and normalization only.
 */

/**
 * Sign index mapping (0-11)
 * Used for normalization and validation only
 */
export const SIGN_INDEX: Record<string, number> = {
  aries: 0,
  taurus: 1,
  gemini: 2,
  cancer: 3,
  leo: 4,
  virgo: 5,
  libra: 6,
  scorpio: 7,
  sagittarius: 8,
  capricorn: 9,
  aquarius: 10,
  pisces: 11,
  // Sanskrit names
  mesha: 0,
  vrishabha: 1,
  mithuna: 2,
  karka: 3,
  karkata: 3,
  simha: 4,
  kanya: 5,
  tula: 6,
  vrischika: 7,
  vrishchika: 7,
  dhanu: 8,
  dhanus: 8,
  makara: 9,
  kumbha: 10,
  meena: 11,
  min: 11,
};

/**
 * Normalize sign name to standard key
 * Handles all variations: English, Sanskrit, case, spelling
 */
export function normalizeSignName(signName: string): string {
  if (!signName) return 'aries';
  
  const normalized = signName.toLowerCase().trim();
  
  // Direct lookup in SIGN_INDEX
  if (SIGN_INDEX[normalized] !== undefined) {
    // Return standard English name
    const signNames = ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo',
                       'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces'];
    return signNames[SIGN_INDEX[normalized]];
  }
  
  // Fallback: try partial match
  for (const [key, index] of Object.entries(SIGN_INDEX)) {
    if (normalized.includes(key) || key.includes(normalized)) {
      const signNames = ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo',
                         'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces'];
      return signNames[index];
    }
  }
  
  // Ultimate fallback
  return 'aries';
}

/**
 * Get sign index from sign name
 * Returns 0-11 or null if invalid
 */
export function getSignIndex(signName: string): number | null {
  if (!signName) return null;
  const normalized = normalizeSignName(signName);
  return SIGN_INDEX[normalized] ?? null;
}

