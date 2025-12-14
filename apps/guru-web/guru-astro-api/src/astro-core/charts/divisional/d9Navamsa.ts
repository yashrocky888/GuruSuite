/**
 * Navamsa Chart (D9) Generator
 * 
 * NOTE: This function is deprecated. All calculations are now done by the guru-api backend.
 * This function now ONLY passes through data from the API without any calculations.
 * 
 * For varga charts: NO calculations are performed - data is used exactly as returned by API.
 * The API is the single source of truth.
 */

import { DivisionalChart, PlanetPosition } from '../../../types';

export function generateNavamsaChart(
  planets: PlanetPosition[]
): DivisionalChart {
  // CRITICAL: NO calculations, NO navamsa sign calculation, NO house calculation
  // This function should not be called - use generateNavamsaChartFromAPI instead
  // Return empty chart structure as fallback
  
  const navamsaHouses: DivisionalChart['houses'] = [];
  
  // Initialize 12 empty houses - no calculations
  for (let i = 1; i <= 12; i++) {
    navamsaHouses.push({
      houseNumber: i,
      sign: '',
      signNumber: 0,
      planets: [],
    });
  }

  return {
    chartType: 'D9',
    houses: navamsaHouses,
  };
}

// REMOVED: getNavamsaSignName function - NO calculation logic allowed
// REMOVED: All navamsa calculation logic - API is single source of truth

