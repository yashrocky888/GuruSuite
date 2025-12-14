/**
 * Astrology Constants
 */

// Vedic Rashi (Sign) Names
export const VEDIC_RASHIS: string[] = [
  'Mesha',      // 0 - Aries
  'Vrishabha',  // 1 - Taurus
  'Mithuna',    // 2 - Gemini
  'Karka',      // 3 - Cancer
  'Simha',      // 4 - Leo
  'Kanya',      // 5 - Virgo
  'Tula',       // 6 - Libra
  'Vrishchika', // 7 - Scorpio
  'Dhanu',      // 8 - Sagittarius
  'Makara',     // 9 - Capricorn
  'Kumbha',     // 10 - Aquarius
  'Meena',      // 11 - Pisces
];

// Western Sign Names (for reference)
export const WESTERN_SIGNS: string[] = [
  'Aries', 'Taurus', 'Gemini', 'Cancer',
  'Leo', 'Virgo', 'Libra', 'Scorpio',
  'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
];

// Planet Names
export const PLANETS: string[] = [
  'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter',
  'Venus', 'Saturn', 'Rahu', 'Ketu'
];

// Swiss Ephemeris Planet Numbers
export const SWEPH_PLANETS: Record<string, number> = {
  Sun: 0,
  Moon: 1,
  Mars: 2,
  Mercury: 3,
  Jupiter: 4,
  Venus: 5,
  Saturn: 6,
  Rahu: 7,  // True Node
  Ketu: 8,  // Opposite of Rahu
};

// Ayanamsa Types
export const AYANAMSA = {
  LAHIRI: 1,
  RAMAN: 3,
  KP: 5,
};

// Nakshatras (27)
export const NAKSHATRAS: string[] = [
  'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira',
  'Ardra', 'Punarvasu', 'Pushya', 'Ashlesha', 'Magha',
  'Purva Phalguni', 'Uttara Phalguni', 'Hasta', 'Chitra',
  'Swati', 'Vishakha', 'Anuradha', 'Jyeshta', 'Mula',
  'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta',
  'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
];

// Nakshatra Lords (Vimshottari Dasha)
export const NAKSHATRA_LORDS: string[] = [
  'Ketu', 'Venus', 'Sun', 'Moon', 'Mars',
  'Rahu', 'Jupiter', 'Saturn', 'Mercury', 'Ketu',
  'Venus', 'Sun', 'Moon', 'Mars',
  'Rahu', 'Jupiter', 'Saturn', 'Mercury', 'Ketu',
  'Venus', 'Sun', 'Moon', 'Mars',
  'Rahu', 'Jupiter', 'Saturn', 'Mercury'
];

// Each Nakshatra spans 13°20' (13.3333 degrees)
export const NAKSHATRA_SPAN = 13.3333333333;

// Sign to Number Mapping
export const SIGN_TO_NUM: Record<string, number> = {
  'Mesha': 0, 'Vrishabha': 1, 'Mithuna': 2, 'Karka': 3,
  'Simha': 4, 'Kanya': 5, 'Tula': 6, 'Vrishchika': 7,
  'Dhanu': 8, 'Makara': 9, 'Kumbha': 10, 'Meena': 11,
  // Western names
  'Aries': 0, 'Taurus': 1, 'Gemini': 2, 'Cancer': 3,
  'Leo': 4, 'Virgo': 5, 'Libra': 6, 'Scorpio': 7,
  'Sagittarius': 8, 'Capricorn': 9, 'Aquarius': 10, 'Pisces': 11,
};

// Get sign name from number
export function getSignName(signNum: number): string {
  const normalized = ((signNum % 12) + 12) % 12; // Handle negative numbers
  return VEDIC_RASHIS[normalized] || 'Mesha';
}

// Get sign number from longitude (0-360)
export function getSignFromLongitude(longitude: number): { signNum: number; degree: number } {
  const signNum = Math.floor(longitude / 30);
  const degree = longitude % 30;
  return { signNum: signNum % 12, degree };
}

// Convert longitude to sign and degree
export function longitudeToSignDegree(longitude: number): { sign: string; signNumber: number; degree: number } {
  const { signNum, degree } = getSignFromLongitude(longitude);
  return {
    sign: getSignName(signNum),
    signNumber: signNum,
    degree: parseFloat(degree.toFixed(2)),
  };
}

