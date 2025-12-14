/**
 * COMPLETE FRONTEND FIX CODE
 * 
 * This file contains the exact code changes needed for the frontend.
 * Copy these files to your frontend repository.
 */

// ============================================================================
// FILE 1: guru-web/utils/dasha.ts
// ============================================================================

/**
 * Calculate current Vimshottari Dasha from Moon's nakshatra
 */
export function calculateCurrentDasha(moonNakshatraIndex: number, birthDate: string): string {
  const nakshatraDashaLords = [
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury',
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury',
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'
  ];
  
  if (moonNakshatraIndex === undefined || moonNakshatraIndex === null) {
    return 'N/A';
  }
  
  const startingLord = nakshatraDashaLords[moonNakshatraIndex % 27];
  const birth = new Date(birthDate);
  const now = new Date();
  const yearsSinceBirth = (now.getTime() - birth.getTime()) / (1000 * 60 * 60 * 24 * 365.25);
  
  const dashaPeriods: Record<string, number> = {
    'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
    'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
  };
  
  const dashaLords = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'];
  const startIndex = dashaLords.indexOf(startingLord);
  
  let currentDashaIndex = startIndex;
  let remainingYears = yearsSinceBirth;
  
  while (remainingYears > 0) {
    const currentLord = dashaLords[currentDashaIndex % 9];
    const period = dashaPeriods[currentLord];
    
    if (remainingYears <= period) {
      return `${currentLord} Dasha`;
    }
    
    remainingYears -= period;
    currentDashaIndex++;
  }
  
  return `${startingLord} Dasha`;
}

// ============================================================================
// FILE 2: guru-web/app/dashboard/page.tsx (UPDATE SECTION)
// ============================================================================

/**
 * FIND THIS CODE (around line 41-52):
 * 
 * if (d1) {
 *   const ascendant = d1.Ascendant;
 *   const planets = d1.Planets || {};
 *   const moon = planets.Moon;
 *   
 *   data = {
 *     currentDasha: data?.currentDasha || 'N/A',  // ← CHANGE THIS
 *     ascendant: ascendant?.sign_sanskrit || ascendant?.sign || 'N/A',
 *     moonSign: moon?.sign_sanskrit || moon?.sign || 'N/A',
 *     system: 'Vedic',
 *     ayanamsa: 'Lahiri'
 *   };
 * }
 * 
 * REPLACE WITH:
 */

// Option 1: Use API's current_dasha (RECOMMENDED - simpler)
if (d1) {
  const ascendant = d1.Ascendant;
  const planets = d1.Planets || {};
  const moon = planets.Moon;
  
  // Try to get current_dasha from kundli response first
  let currentDasha = 'N/A';
  
  // Check if kundliResponse has current_dasha (preferred method)
  if (kundliResponse?.current_dasha?.display) {
    currentDasha = kundliResponse.current_dasha.display;
  }
  // Fallback: Calculate from Moon's nakshatra_index
  else if (moon?.nakshatra_index !== undefined && moon?.nakshatra_index !== null && birthDetails?.date) {
    const { calculateCurrentDasha } = await import('@/utils/dasha');
    currentDasha = calculateCurrentDasha(moon.nakshatra_index, birthDetails.date);
  }
  
  data = {
    currentDasha: currentDasha,  // ← FIXED
    ascendant: ascendant?.sign_sanskrit || ascendant?.sign || 'N/A',
    moonSign: moon?.sign_sanskrit || moon?.sign || 'N/A',
    system: 'Vedic',
    ayanamsa: 'Lahiri'
  };
}

// ============================================================================
// ALTERNATIVE: If kundliResponse is not available in scope
// ============================================================================

/**
 * If you need to fetch kundliResponse separately:
 */

// Get kundli response (includes current_dasha)
const kundliResponse = await getKundli(userId, birthDetails);

if (kundliResponse?.D1) {
  const d1 = kundliResponse.D1;
  const ascendant = d1.Ascendant;
  const planets = d1.Planets || {};
  const moon = planets.Moon;
  
  // Use current_dasha from API (preferred - more accurate)
  let currentDasha = kundliResponse.current_dasha?.display || 'N/A';
  
  // Fallback: Calculate if API doesn't provide it
  if (currentDasha === 'N/A' && moon?.nakshatra_index !== undefined && moon?.nakshatra_index !== null && birthDetails?.date) {
    const { calculateCurrentDasha } = await import('@/utils/dasha');
    currentDasha = calculateCurrentDasha(moon.nakshatra_index, birthDetails.date);
  }
  
  data = {
    currentDasha: currentDasha,  // ← FIXED
    ascendant: ascendant?.sign_sanskrit || ascendant?.sign || 'N/A',
    moonSign: moon?.sign_sanskrit || moon?.sign || 'N/A',
    system: 'Vedic',
    ayanamsa: 'Lahiri'
  };
}

// ============================================================================
// VERIFICATION
// ============================================================================

/**
 * After implementing:
 * 1. Dashboard should show: "Current Dasha: Venus Dasha - Mercury Antardasha" (or other)
 * 2. Should NOT show "N/A"
 * 3. Uses API's current_dasha.display if available
 * 4. Falls back to calculation if API value missing
 */

