/**
 * Chart Coordinates - Exact Math from Python Reference
 * Converts Python coordinate system to TypeScript
 */

// ==================== NORTH INDIAN CHART COORDINATES ====================

/**
 * North Indian Chart Planet Positions
 * Array index = house number - 1 (0-11)
 * Inner array index = planet index - 1 (0-7)
 */
export const planetPosition_northSquareClassic: Array<Array<{ x: string; y: string }>> = [
  // House 1 (Tan Bhav) - 8 planet positions
  [
    { y: '140', x: '185' }, // first planet
    { y: '100', x: '195' }, // second planet
    { y: '138', x: '225' }, // third planet
    { y: '100', x: '235' }, // fourth planet
    { y: '60', x: '205' },  // fifth planet
    { y: '85', x: '165' },  // sixth planet
    { y: '130', x: '145' }, // seventh planet
    { y: '122', x: '263' }, // eighth planet
  ],
  // House 2 (Dhan Bhav)
  [
    { x: '96', y: '56' },
    { y: '35', x: '130' },
    { y: '32', x: '70' },
    { y: '70', x: '123' },
    { y: '70', x: '73' },
    { y: '33', x: '40' },
    { y: '33', x: '160' },
    { y: '36', x: '105' },
  ],
  // House 3 (Anuj Bhav)
  [
    { x: '40', y: '110' },
    { x: '15', y: '145' },
    { x: '12', y: '85' },
    { x: '45', y: '135' },
    { x: '50', y: '90' },
    { x: '13', y: '55' },
    { x: '13', y: '175' },
    { x: '16', y: '120' },
  ],
  // House 4 (Maata Bhav)
  [
    { x: '120', y: '200' },
    { x: '80', y: '210' },
    { x: '118', y: '240' },
    { x: '80', y: '250' },
    { x: '40', y: '220' },
    { x: '65', y: '180' },
    { x: '110', y: '160' },
    { x: '102', y: '278' },
  ],
  // House 5 (Santan Bhav)
  [
    { x: '40', y: '310' },
    { x: '15', y: '345' },
    { x: '12', y: '285' },
    { x: '50', y: '338' },
    { x: '50', y: '288' },
    { x: '13', y: '255' },
    { x: '13', y: '375' },
    { x: '16', y: '320' },
  ],
  // House 6 (Rog Bhav)
  [
    { x: '97', y: '360' },
    { x: '60', y: '375' },
    { x: '128', y: '398' },
    { x: '100', y: '385' },
    { x: '80', y: '403' },
    { x: '40', y: '400' },
    { x: '162', y: '402' },
    { x: '130', y: '370' },
  ],
  // House 7 (Dampathya Bhav)
  [
    { y: '275', x: '182' },
    { y: '325', x: '195' },
    { y: '285', x: '225' },
    { y: '325', x: '235' },
    { y: '365', x: '205' },
    { y: '340', x: '165' },
    { y: '295', x: '145' },
    { y: '305', x: '260' },
  ],
  // House 8 (Aayu Bhav)
  [
    { x: '300', y: '360' },
    { x: '260', y: '375' },
    { x: '328', y: '398' },
    { x: '300', y: '385' },
    { x: '280', y: '403' },
    { x: '240', y: '400' },
    { x: '362', y: '402' },
    { x: '330', y: '370' },
  ],
  // House 9 (Bhagya Bhav)
  [
    { x: '360', y: '310' },
    { x: '350', y: '340' },
    { x: '350', y: '285' },
    { x: '380', y: '273' },
    { x: '380', y: '335' },
    { x: '369', y: '360' },
    { x: '383', y: '250' },
    { x: '385', y: '382' },
  ],
  // House 10 (Karma Bhav)
  [
    { x: '270', y: '200' },
    { x: '320', y: '210' },
    { x: '282', y: '240' },
    { x: '320', y: '250' },
    { x: '360', y: '220' },
    { x: '335', y: '180' },
    { x: '290', y: '160' },
    { x: '298', y: '278' },
  ],
  // House 11 (Laab Bhav)
  [
    { x: '360', y: '110' },
    { x: '350', y: '140' },
    { x: '350', y: '85' },
    { x: '380', y: '73' },
    { x: '380', y: '135' },
    { x: '369', y: '160' },
    { x: '383', y: '50' },
    { x: '385', y: '182' },
  ],
  // House 12 (Karch Bhav)
  [
    { x: '296', y: '56' },
    { y: '35', x: '330' },
    { y: '32', x: '270' },
    { y: '70', x: '323' },
    { y: '70', x: '273' },
    { y: '33', x: '240' },
    { y: '33', x: '360' },
    { y: '36', x: '305' },
  ],
];

/**
 * Get coordinates for planet in North Indian chart
 * @param houseNum House number (1-12)
 * @param planetIdx Planet index in that house (1-8)
 * @returns {x, y} coordinates
 */
export function getNorthCoordinates(houseNum: number, planetIdx: number): { x: number; y: number } {
  if (planetIdx >= 1 && planetIdx <= 8 && houseNum >= 1 && houseNum <= 12) {
    const pos = planetPosition_northSquareClassic[houseNum - 1][planetIdx - 1];
    return {
      x: parseInt(pos.x),
      y: parseInt(pos.y),
    };
  }
  return { x: 0, y: 0 };
}

// North Indian Chart Polygon Points (from Python)
export const northPolygonPoints: Record<number, string> = {
  1: '210,10 110,110 210,210 310,110',      // Tan Bhav
  2: '10,10 210,10 110,110',                // Dhan Bhav
  3: '10,10 10,210 110,110',                // Anuj Bhav
  4: '110,110 10,210 110,310 210,210',      // Maata Bhav
  5: '10,210 110,310 10,410',               // Santan Bhav
  6: '210,410 110,310 10,410',              // Rog Bhav
  7: '210,410 110,310 210,210 310,310',     // Dampathya Bhav
  8: '210,410 310,310 410,410',             // Aayu Bhav
  9: '310,310 410,410 410,210',             // Bhagya Bhav
  10: '310,310 410,210 310,110 210,210',    // Karma Bhav
  11: '410,210 310,110 410,10',             // Laab Bhav
  12: '310,110 410,10 210,10',              // Karch Bhav
};

// Sign number positions for North chart
export const northSignPositions: Record<number, { x: number; y: number }> = {
  1: { x: 193, y: 195 },   // Tan
  2: { x: 97, y: 95 },     // Dhan
  3: { x: 70, y: 118 },     // Anuj
  4: { x: 170, y: 218 },   // Maata
  5: { x: 75, y: 316 },    // Santaan
  6: { x: 97, y: 335 },    // Rog
  7: { x: 195, y: 240 },   // Dampathya
  8: { x: 296, y: 337 },   // Aayu
  9: { x: 320, y: 318 },   // Bhagya
  10: { x: 220, y: 218 },  // Karma
  11: { x: 318, y: 118 },  // Laab
  12: { x: 298, y: 98 },   // Karch
};

// ==================== SOUTH INDIAN CHART COORDINATES ====================

/**
 * South Chart offsets from Aries position
 */
export const SouthChart_offsets4mAries: Record<string, { x: number; y: number }> = {
  aries: { x: 0, y: 0 },
  taurus: { x: 120, y: 0 },
  gemini: { x: 240, y: 0 },
  cancer: { x: 240, y: 80 },
  leo: { x: 240, y: 160 },
  virgo: { x: 240, y: 240 },
  libra: { x: 120, y: 240 },
  scorpio: { x: 0, y: 240 },
  sagittarius: { x: -120, y: 240 },
  capricorn: { x: -120, y: 160 },
  aquarius: { x: -120, y: 80 },
  pisces: { x: -120, y: 0 },
  // Vedic names
  mesha: { x: 0, y: 0 },
  vrishabha: { x: 120, y: 0 },
  mithuna: { x: 240, y: 0 },
  karka: { x: 240, y: 80 },
  simha: { x: 240, y: 160 },
  kanya: { x: 240, y: 240 },
  tula: { x: 120, y: 240 },
  vrischika: { x: 0, y: 240 },
  vrishchika: { x: 0, y: 240 }, // Handle both spellings
  dhanu: { x: -120, y: 240 },
  makara: { x: -120, y: 160 },
  kumbha: { x: -120, y: 80 },
  meena: { x: -120, y: 0 },
};

/**
 * Ascendant position for Aries
 */
export const SouthChart_AscendantPositionAries = { x: 202, y: 83 };

/**
 * Base coordinates for planets (9 positions)
 */
export const base_coordinates: Array<{ x: number; y: number }> = [
  { x: 155, y: 40 },   // planet 1
  { x: 185, y: 48 },   // planet 2
  { x: 170, y: 70 },   // planet 3
  { x: 135, y: 58 },   // planet 4
  { x: 215, y: 60 },   // planet 5
  { x: 145, y: 83 },   // planet 6
  { x: 210, y: 35 },   // planet 7
  { x: 130, y: 32 },   // planet 8
  { x: 180, y: 30 },   // planet 9
];

/**
 * Get coordinates for planet in South Indian chart
 * @param sign Sign name (e.g., "Aries", "Taurus", "Mesha", "Vrishabha")
 * @param planetIdx Planet index in that sign (1-9)
 * @returns {x, y} coordinates
 */
export function getSouthCoordinates(sign: string, planetIdx: number): { x: number; y: number } {
  if (planetIdx >= 1 && planetIdx <= 9) {
    const signLower = sign.toLowerCase();
    const offset = SouthChart_offsets4mAries[signLower] || { x: 0, y: 0 };
    const base = base_coordinates[planetIdx - 1];
    return {
      x: base.x + offset.x,
      y: base.y + offset.y,
    };
  }
  return { x: 0, y: 0 };
}

// South Indian Chart Rectangle Positions (from Python)
export const southRectPositions: Record<string, { x: number; y: number; width: number; height: number }> = {
  aries: { x: 123, y: 10, width: 120, height: 80 },
  taurus: { x: 243, y: 10, width: 120, height: 80 },
  gemini: { x: 363, y: 10, width: 120, height: 80 },
  cancer: { x: 363, y: 90, width: 120, height: 80 },
  leo: { x: 363, y: 170, width: 120, height: 80 },
  virgo: { x: 363, y: 250, width: 120, height: 80 },
  libra: { x: 243, y: 250, width: 120, height: 80 },
  scorpio: { x: 123, y: 250, width: 120, height: 80 },
  sagittarius: { x: 3, y: 250, width: 120, height: 80 },
  capricorn: { x: 3, y: 170, width: 120, height: 80 },
  aquarius: { x: 3, y: 90, width: 120, height: 80 },
  pisces: { x: 3, y: 10, width: 120, height: 80 },
  // Vedic names
  mesha: { x: 123, y: 10, width: 120, height: 80 },
  vrishabha: { x: 243, y: 10, width: 120, height: 80 },
  mithuna: { x: 363, y: 10, width: 120, height: 80 },
  karka: { x: 363, y: 90, width: 120, height: 80 },
  simha: { x: 363, y: 170, width: 120, height: 80 },
  kanya: { x: 363, y: 250, width: 120, height: 80 },
  tula: { x: 243, y: 250, width: 120, height: 80 },
  vrischika: { x: 123, y: 250, width: 120, height: 80 },
  vrishchika: { x: 123, y: 250, width: 120, height: 80 }, // Handle both spellings
  dhanu: { x: 3, y: 250, width: 120, height: 80 },
  makara: { x: 3, y: 170, width: 120, height: 80 },
  kumbha: { x: 3, y: 90, width: 120, height: 80 },
  meena: { x: 3, y: 10, width: 120, height: 80 },
};
