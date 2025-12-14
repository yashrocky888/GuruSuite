/**
 * Chart Utilities - Data Normalization
 * FIXED: Proper API data handling with debugging
 * 
 * API Calculation Method:
 * - Backend uses FLG_SIDEREAL flag for direct sidereal positions
 * - Backend uses swe.houses_ex() with FLG_SIDEREAL for sidereal ascendant
 * - All positions are already in sidereal zodiac format from API
 * - No manual ayanamsa conversion needed on frontend
 */

// API returns: { name: "Sun", sign: "Mesha", house: 1, ... }
// Updated for Drik Panchang compatibility
export interface ApiPlanet {
  name: string;
  sign: string;
  house: number;
  degree?: number;
  nakshatra?: string;
  pada?: number;
  retrograde?: boolean;
  color?: string;
  speed?: number;
  longitude?: number;
}

export interface ApiKundliData {
  lagna?: number;
  lagnaSign?: string;
  lagnaSignSanskrit?: string;
  lagnaDegree?: number; // Full longitude (0-360°) for Ascendant
  lagnaDegreeInSign?: number; // Degrees in sign (0-30°) for Ascendant
  lagnaDegreeDms?: number; // Degree part (int) for Ascendant
  lagnaArcminutes?: number; // Minutes part (int) for Ascendant
  lagnaArcseconds?: number; // Seconds part (int) for Ascendant
  ascendantHouse?: number; // House number (1-12) from API - CRITICAL: Use this for placement
  planets: ApiPlanet[];
  ayanamsa?: string;
  system?: string;
  houses?: Array<{ house: number; sign: string; sign_sanskrit?: string; degree: number; degrees_in_sign?: number }>; // API house data
  chartType?: string; // For divisional charts: D1, D2, D9, D10, etc.
}

// Rashi names (Sanskrit in English) - Use correct spelling "Vrishchika"
export const RASHI_NAMES: Record<number, string> = {
  1: 'Mesha',
  2: 'Vrishabha',
  3: 'Mithuna',
  4: 'Karka',
  5: 'Simha',
  6: 'Kanya',
  7: 'Tula',
  8: 'Vrishchika', // Correct spelling
  9: 'Dhanu',
  10: 'Makara',
  11: 'Kumbha',
  12: 'Meena',
};

// Sign name to number mapping
export const SIGN_TO_NUM: Record<string, number> = {
  'Mesha': 1, 'Vrishabha': 2, 'Mithuna': 3, 'Karka': 4,
  'Simha': 5, 'Kanya': 6, 'Tula': 7, 'Vrishchika': 8, 'Vrischika': 8, // Both spellings
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
 * Aries -> Mesha, Taurus -> Vrishabha, etc.
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
  
  // If already Sanskrit, return as is
  if (SIGN_TO_NUM[englishName]) {
    return englishName;
  }
  
  // Convert English to Sanskrit
  return englishToSanskrit[englishName] || englishName;
}

/**
 * Calculate sign for a house based on lagna
 * House 1 = Lagna sign, then clockwise
 */
export function getSignForHouse(houseNum: number, lagnaSign: number): number {
  const lagnaIndex = lagnaSign - 1;
  const houseIndex = (lagnaIndex + houseNum - 1) % 12;
  return houseIndex + 1;
}

/**
 * House data with planets (includes degree)
 */
export interface HouseData {
  houseNumber: number;
  signNumber: number;
  signName: string;
  planets: Array<{ 
    name: string; 
    abbr: string; 
    sign: string;
    degree?: number;
    degree_minutes?: number; // Minutes component (0-59)
    degree_seconds?: number; // Seconds component (0-59)
  }>;
}

/**
 * Normalize API data to house structure
 * ✅ Uses API data + calculates house signs from lagna (old working method)
 */
export function normalizeKundliData(apiData: ApiKundliData | null | undefined): HouseData[] {
  if (!apiData || !apiData.planets || !Array.isArray(apiData.planets)) {
    return [];
  }

  // Get lagna sign number (for calculating house signs)
  // API now returns Sanskrit names directly, so use them as-is
  let lagnaSign = 1;
  if (apiData.lagnaSignSanskrit) {
    // Prefer lagnaSignSanskrit for divisional charts
    lagnaSign = getSignNum(apiData.lagnaSignSanskrit);
  } else if (apiData.lagnaSign) {
    // API returns Sanskrit names directly (Vrishchika, Mesha, etc.)
    lagnaSign = getSignNum(apiData.lagnaSign);
  } else if (apiData.lagna !== undefined) {
    lagnaSign = apiData.lagna;
  }

  // Initialize 12 houses - ALWAYS use API Houses array (JHORA calculations) if available
  // For varga charts (South Indian style): Use fixed sign grid (house = sign number)
  const houses: HouseData[] = [];
  const isVargaChart = apiData.chartType && apiData.chartType !== 'D1';
  
  if (isVargaChart) {
    // For varga charts: Fixed sign grid - each house = sign number (1-12)
    // House 1 = Mesha, House 2 = Vrishabha, ..., House 12 = Meena
    for (let i = 1; i <= 12; i++) {
      houses.push({
        houseNumber: i,
        signNumber: i,
        signName: getSignName(i), // Fixed sign grid
        planets: [],
      });
    }
  } else if (apiData.houses && Array.isArray(apiData.houses) && apiData.houses.length > 0) {
    // Check if houses array contains objects with sign info (JHORA format)
    const firstHouse = apiData.houses[0];
    if (typeof firstHouse === 'object' && firstHouse !== null && ('sign' in firstHouse || 'sign_sanskrit' in firstHouse)) {
      // API Houses array with sign objects: [{ house: 1, sign: "Vrishchika", sign_sanskrit: "Vrishchika", ... }]
      // This is JHORA house calculation format - use it as source of truth
      for (let i = 1; i <= 12; i++) {
        const apiHouse = apiData.houses.find((h: any) => h.house === i);
        if (apiHouse && (apiHouse.sign || (apiHouse as any).sign_sanskrit)) {
          // API returns sign_sanskrit or sign - prefer sign_sanskrit, use sign as fallback
          const sign = (apiHouse as any).sign_sanskrit || apiHouse.sign;
          // Check if already Sanskrit, else convert
          const sanskritSign = SIGN_TO_NUM[sign] ? sign : convertToSanskritSign(sign);
          const signNum = getSignNum(sanskritSign);
          houses.push({
            houseNumber: i,
            signNumber: signNum,
            signName: sanskritSign, // Sanskrit sign from JHORA API calculation
            planets: [],
          });
        } else {
          // House not found in API - calculate from lagna as fallback
          const signNum = getSignForHouse(i, lagnaSign);
          houses.push({
            houseNumber: i,
            signNumber: signNum,
            signName: getSignName(signNum),
            planets: [],
          });
        }
      }
    } else {
      // Houses array is just numbers: [1, 2, 3, ...] - calculate from lagna
      for (let i = 1; i <= 12; i++) {
        const signNum = getSignForHouse(i, lagnaSign);
        houses.push({
          houseNumber: i,
          signNumber: signNum,
          signName: getSignName(signNum),
          planets: [],
        });
      }
    }
  } else {
    // Fallback: Calculate signs from lagna (old method - should not happen with JHORA API)
    for (let i = 1; i <= 12; i++) {
      const signNum = getSignForHouse(i, lagnaSign);
      houses.push({
        houseNumber: i,
        signNumber: signNum,
        signName: getSignName(signNum),
        planets: [],
      });
    }
  }

  // Map ALL planets to houses
  // For South Indian charts (varga charts): Use planet's sign_index to determine house (house = sign number)
  // For North Indian/D1 charts: Match planet sign to house sign (JHORA/Placidus system)
  console.log(`🔍 Mapping ${apiData.planets.length} planets to houses...`);
  
  apiData.planets.forEach((planet) => {
    // Validate API data - Log missing fields for debugging
    if (!planet.sign || planet.degree === undefined || planet.degree === null) {
      console.warn(`⚠️ Skipping planet ${planet.name}:`, {
        house: planet.house,
        sign: planet.sign,
        degree: planet.degree
      });
      return;
    }
 
    // API returns Sanskrit names directly (Vrishchika, Mesha, etc.) or English for varga charts
    let planetSign = planet.sign;
    
    // Convert English sign to Sanskrit if needed
    if (!SIGN_TO_NUM[planetSign]) {
      planetSign = convertToSanskritSign(planetSign);
    }
    
    let houseNum: number;
    let houseIndex: number;
    
    if (isVargaChart) {
      // CRITICAL: For varga charts, use house directly from API (Whole Sign system)
      // API provides planet.house which is already calculated (house = sign)
      // DO NOT calculate or infer house - use API value exactly
      // RUNTIME ASSERTION: house MUST equal sign (architectural requirement)
      if (planet.house !== undefined && planet.house >= 1 && planet.house <= 12) {
        houseNum = planet.house; // Use API's house value directly
        
        // CRITICAL ASSERTION: house must equal sign for varga charts
        const planetSignIndex = planet.sign_index !== undefined ? planet.sign_index : getSignNum(planetSign) - 1;
        const expectedHouse = planetSignIndex + 1;
        
        if (houseNum !== expectedHouse) {
          console.error(`❌ VARGA VIOLATION: ${planet.name} - house (${houseNum}) must equal sign (${expectedHouse})`);
          // Force correction: use sign-based house
          houseNum = expectedHouse;
        }
        
        houseIndex = houseNum - 1;
      } else {
        // Fallback: If API doesn't provide house, use sign number (shouldn't happen)
        console.warn(`⚠️ Planet ${planet.name} missing house in varga chart, using sign as fallback`);
        const signNum = getSignNum(planetSign);
        houseNum = signNum;
        houseIndex = houseNum - 1;
      }
      
      // Ensure house exists, create if missing (shouldn't happen, but safety check)
      if (!houses[houseIndex]) {
        const signNum = getSignNum(planetSign);
        houses[houseIndex] = {
          houseNumber: houseNum,
          signNumber: signNum,
          signName: planetSign,
          planets: [],
        };
      }
    } else {
      // For D1 charts: Match planet sign to house sign (JHORA/Placidus system)
      const matchingHouse = houses.find(h => h.signName === planetSign);
      
      if (!matchingHouse) {
        // Fallback: Use API's house field if available
        if (planet.house !== undefined && planet.house >= 1 && planet.house <= 12) {
          houseNum = planet.house;
          houseIndex = houseNum - 1;
          console.warn(`⚠️ No house found with sign ${planetSign} for ${planet.name}, using API house ${houseNum}`);
        } else {
          console.error(`❌ No house found with sign ${planetSign} for planet ${planet.name}`);
          return;
        }
      } else {
        houseNum = matchingHouse.houseNumber;
        houseIndex = houseNum - 1;
      }
    }

    // Use degrees_in_sign for display (0-30°), not total degree (0-360°)
    // API now returns exact degrees and minutes - use them directly
    const displayDegree = (planet as any).degrees_in_sign !== undefined 
      ? (planet as any).degrees_in_sign 
      : planet.degree;

    // CRITICAL: Calculate DMS from degrees_in_sign (0-30°), NOT from degree_dms (which is 0-360°)
    // API returns degree_dms as total degree, but we need DMS in 0-30° format
    const degreeInSign = displayDegree; // Already in 0-30° range
    const degreeDms = Math.floor(degreeInSign); // Integer part of degrees in sign (0-29)
    const minutes = Math.floor((degreeInSign - degreeDms) * 60); // Minutes from fractional part
    const seconds = Math.floor(((degreeInSign - degreeDms) * 60 - minutes) * 60); // Seconds

    if (houses[houseIndex]) {
      // Add planet with exact API data (sign already in Sanskrit, degree in sign)
      houses[houseIndex].planets.push({
        name: planet.name,
        abbr: getPlanetAbbr(planet.name),
        sign: planetSign, // Already Sanskrit from API (sign_sanskrit)
        degree: displayDegree, // Degrees in sign (0-30°) from API - EXACT
        degree_dms: degreeDms, // Degree part in sign (0-29) - calculated from degrees_in_sign
        degree_minutes: minutes, // Minutes part - calculated from degrees_in_sign
        degree_seconds: seconds, // Seconds part - calculated from degrees_in_sign
      });
      console.log(`  ✅ ${planet.name} (${planetSign}) → House ${houseNum} (${houses[houseIndex].signName}): ${displayDegree.toFixed(2)}°`);
    } else {
      console.error(`❌ Invalid house index ${houseIndex} for planet ${planet.name} (sign=${planetSign})`);
    }
  });

  // CRITICAL FIX: Use API's house field for Ascendant placement
  // For varga charts: house = sign (Whole Sign system) - use ascendant_house from API
  // For D1 charts: Use ascendant.house from API (Placidus system)
  // DO NOT calculate or infer house - use API value exactly
  if (apiData.lagnaSignSanskrit && apiData.ascendantHouse !== undefined) {
    // Use the house number from API (house = sign for varga charts)
    const ascendantHouse = apiData.ascendantHouse; // From API: ascendant_house field
    // CRITICAL: Use degrees_in_sign (0-30°) for display, NOT total degree (0-360°)
    const ascendantDegree = apiData.lagnaDegreeInSign !== undefined 
      ? apiData.lagnaDegreeInSign 
      : (apiData.lagnaDegree !== undefined ? (apiData.lagnaDegree % 30) : 0);
    // CRITICAL: Use Ascendant's own sign (Vrishchika), NOT the house cusp's sign (Mithuna)
    // In Placidus system, house cusps and planet signs can differ
    const ascendantSign = apiData.lagnaSignSanskrit || apiData.lagnaSign || 'Mesha';
    
    // Use house number from API - ensure valid range (1-12)
    const validHouse = ((ascendantHouse - 1) % 12) + 1;
    const houseIndex = validHouse - 1;
    
    console.log(`📍 Ascendant: House=${ascendantHouse} (from API), Sign=${ascendantSign} (Ascendant's sign, NOT house cusp sign), Degree in Sign=${ascendantDegree.toFixed(2)}°`);
    
    if (houses[houseIndex]) {
      // CRITICAL: Calculate DMS from degrees_in_sign (0-30°), NOT total degree (0-360°)
      // The API's degree_dms might be from total degree, so recalculate from degrees_in_sign
      const degreeInSign = ascendantDegree; // Already in 0-30° range
      const degreeDms = Math.floor(degreeInSign); // Integer part of degrees in sign (0-29)
      const minutes = Math.floor((degreeInSign - degreeDms) * 60); // Minutes from fractional part
      const seconds = Math.floor(((degreeInSign - degreeDms) * 60 - minutes) * 60); // Seconds
      
      // Use API's arcminutes/arcseconds if available (they should be for degrees_in_sign)
      // Otherwise calculate from degrees_in_sign
      const finalMinutes = apiData.lagnaArcminutes !== undefined 
        ? apiData.lagnaArcminutes 
        : minutes;
      const finalSeconds = apiData.lagnaArcseconds !== undefined 
        ? apiData.lagnaArcseconds 
        : seconds;
      
      houses[houseIndex].planets.push({
        name: 'Ascendant',
        abbr: 'Asc',
        sign: ascendantSign, // CRITICAL: Use Ascendant's own sign (Vrishchika), NOT house cusp sign
        degree: ascendantDegree, // Degrees in sign (0-30°) - CRITICAL: Use this, not total degree
        degree_dms: degreeDms, // Degree part in sign (0-29) - calculated from degrees_in_sign
        degree_minutes: finalMinutes, // Minutes part (int) - from API or calculated
        degree_seconds: finalSeconds, // Seconds part (int) - from API or calculated
      });
      console.log(`  ✅ Ascendant → House ${validHouse} (house cusp: ${houses[houseIndex].signName}, Ascendant sign: ${ascendantSign}): ${ascendantDegree.toFixed(2)}° (${degreeDms}°${finalMinutes}'${finalSeconds}")`);
    } else {
      console.warn(`⚠️ Invalid house index ${houseIndex} for Ascendant (house=${ascendantHouse})`);
    }
  } else if (apiData.lagnaSignSanskrit) {
    console.warn('⚠️ Ascendant sign found but house number not provided from API');
  }

  // Return all 12 houses (even empty ones) for chart structure, but chart will hide empty ones
  return houses;
}
