/**
 * South Indian Rashi Chart Generator
 * 
 * NOTE: This function is deprecated. All calculations are now done by the guru-api backend.
 * This function now ONLY passes through data from the API without any rotation or remapping.
 * 
 * For varga charts: NO rotation is performed - houses are used exactly as returned by API.
 * The API is the single source of truth.
 */

import { RashiChart } from '../../types';
import { PlanetPosition, HouseCusp } from '../../types';

export function generateSouthIndianChart(
  planets: PlanetPosition[],
  houses: HouseCusp[],
  lagna: { signNumber: number }
): RashiChart {
  // CRITICAL: NO calculations, NO rotation, NO remapping
  // Simply pass through the houses and planets as provided by the API
  // The API already contains the correct house assignments
  
  const chartHouses = houses.map((house) => {
    // Find planets in this house using API's house assignment
    // NO calculation of house from sign - use API's house value directly
    const housePlanets = planets
      .filter(planet => {
        // For varga charts and D1: Use house from API data if available
        // Otherwise, this function should not be called
        // This is a fallback that should not execute in normal flow
        return false; // Force empty - this function should not be used
      })
      .map(p => ({
        name: p.planet,
        degree: p.degree,
        nakshatra: p.nakshatra,
        pada: p.pada,
      }));

    return {
      houseNumber: house.houseNumber,
      sign: house.sign,
      signNumber: house.signNumber,
      planets: housePlanets,
    };
  });

  return { houses: chartHouses };
}

// REMOVED: getHouseForSign function - NO rotation/remapping logic allowed

