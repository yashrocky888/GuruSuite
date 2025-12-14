/**
 * Kundli Chart Types - Single Source of Truth
 * Clean data model for Vedic astrology charts
 */

export interface HouseData {
  houseNumber: number;      // 1–12 from Ascendant
  signName: string;         // 'Mesha', 'Vrishabha', ...
  signIndex: number;        // 0–11 (Aries..Pisces)
  planets: string[];        // ['Su', 'Mo', 'Ma', ...]
}

export interface RawPlanetData {
  name: string;
  sign: string;
  house: number;
  degree?: number;
  nakshatra?: string;
  color?: string;
}

export interface RawKundliData {
  lagna?: number;
  lagnaSign?: string;
  planets: RawPlanetData[];
  ayanamsa?: string;
  system?: string;
  [key: string]: any; // Allow additional properties for backward compatibility
}

// Planet abbreviation map
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

// Vedic Rashi names
export const VEDIC_RASHIS: string[] = [
  'Mesha',      // 0 - Aries
  'Vrishabha',  // 1 - Taurus
  'Mithuna',    // 2 - Gemini
  'Karka',      // 3 - Cancer
  'Simha',      // 4 - Leo
  'Kanya',      // 5 - Virgo
  'Tula',       // 6 - Libra
  'Vrischika',  // 7 - Scorpio
  'Dhanu',      // 8 - Sagittarius
  'Makara',     // 9 - Capricorn
  'Kumbha',     // 10 - Aquarius
  'Meena',      // 11 - Pisces
];

// Sign name to index mapping
export const SIGN_TO_INDEX: Record<string, number> = {
  'Mesha': 0, 'Vrishabha': 1, 'Mithuna': 2, 'Karka': 3,
  'Simha': 4, 'Kanya': 5, 'Tula': 6, 'Vrischika': 7,
  'Dhanu': 8, 'Makara': 9, 'Kumbha': 10, 'Meena': 11,
  'Aries': 0, 'Taurus': 1, 'Gemini': 2, 'Cancer': 3,
  'Leo': 4, 'Virgo': 5, 'Libra': 6, 'Scorpio': 7,
  'Sagittarius': 8, 'Capricorn': 9, 'Aquarius': 10, 'Pisces': 11,
};

/**
 * Map planet name to abbreviation
 */
export function mapPlanetName(nameFromApi: string): string {
  return PLANET_ABBR[nameFromApi] ?? nameFromApi.substring(0, 2);
}

/**
 * Get sign index from sign name
 */
export function getSignIndex(signName: string): number {
  return SIGN_TO_INDEX[signName] ?? 0;
}

/**
 * Normalize raw API kundli data to HouseData array
 * This is the single source of truth for chart rendering
 * 
 * ALL planets from API are included - no filtering
 */
export function normalizeKundliToHouses(raw: RawKundliData | null | undefined): HouseData[] {
  if (!raw || !raw.planets || !Array.isArray(raw.planets)) {
    return [];
  }

  // Get lagna sign index (0-11)
  let lagnaSignIndex = 0;
  if (raw.lagnaSign) {
    lagnaSignIndex = getSignIndex(raw.lagnaSign);
  } else if (raw.lagna !== undefined) {
    lagnaSignIndex = (raw.lagna - 1) % 12;
  }

  // Initialize 12 houses
  const houses: HouseData[] = Array.from({ length: 12 }, (_, i) => {
    const houseNumber = i + 1;
    // Calculate sign for this house
    // House 1 = Lagna sign, then clockwise
    const signIndex = (lagnaSignIndex + houseNumber - 1) % 12;
    const signName = VEDIC_RASHIS[signIndex];

    return {
      houseNumber,
      signName,
      signIndex,
      planets: [],
    };
  });

  // Map ALL planets to houses - NO FILTERING
  raw.planets.forEach((planet) => {
    // Handle different API response formats
    const planetName = planet.name || (planet as any).planet || 'Unknown';
    const houseNumber = planet.house || 1;
    const planetAbbr = mapPlanetName(planetName);

    // Ensure house number is valid (1-12)
    const validHouse = ((houseNumber - 1) % 12) + 1;
    const houseIndex = validHouse - 1;

    if (houses[houseIndex]) {
      houses[houseIndex].planets.push(planetAbbr);
    }
  });

  return houses;
}
