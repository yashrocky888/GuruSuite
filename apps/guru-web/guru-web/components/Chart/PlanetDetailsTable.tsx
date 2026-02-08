/**
 * Planet Details Table Component
 * 
 * Prokerala-style planetary details table for ALL divisional charts (D1-D60).
 * 
 * 🔒 UI ONLY - NO ASTROLOGY CALCULATIONS
 * Uses existing computed planet data from API response.
 * 
 * Table Columns (in order):
 * 1. Planet (with icon/symbol)
 * 2. Position (absolute longitude, e.g. 31° 24')
 * 3. Degrees (degrees within sign, e.g. 1° 24')
 * 4. Rasi (sign name + icon)
 * 5. Rasi Lord
 * 6. Nakshatra
 * 7. Nakshatra Lord
 */

'use client';

import React from 'react';

// Sign lords (Rasi lords) - simple mapping
const SIGN_LORDS: { [key: string]: string } = {
  'Aries': 'Mars',
  'Mesha': 'Mars',
  'Taurus': 'Venus',
  'Vrishabha': 'Venus',
  'Gemini': 'Mercury',
  'Mithuna': 'Mercury',
  'Cancer': 'Moon',
  'Karka': 'Moon',
  'Leo': 'Sun',
  'Simha': 'Sun',
  'Virgo': 'Mercury',
  'Kanya': 'Mercury',
  'Libra': 'Venus',
  'Tula': 'Venus',
  'Scorpio': 'Mars',
  'Vrishchika': 'Mars',
  'Sagittarius': 'Jupiter',
  'Dhanu': 'Jupiter',
  'Capricorn': 'Saturn',
  'Makara': 'Saturn',
  'Aquarius': 'Saturn',
  'Kumbha': 'Saturn',
  'Pisces': 'Jupiter',
  'Meena': 'Jupiter',
};

// Planet icons/symbols
const PLANET_SYMBOLS: { [key: string]: string } = {
  'Sun': '☉',
  'Moon': '☽',
  'Mars': '♂',
  'Mercury': '☿',
  'Jupiter': '♃',
  'Venus': '♀',
  'Saturn': '♄',
  'Rahu': '☊',
  'Ketu': '☋',
  'Ascendant': 'ASC',
};

interface PlanetDetailsTableProps {
  chartType?: string; // e.g. "D1", "D2", ..., "D60"
  ascendant: {
    sign?: string;
    sign_sanskrit?: string;
    sign_index?: number;
    degree?: number;
    degrees_in_sign?: number;
    degree_dms?: number;
    arcminutes?: number;
    arcseconds?: number;
    lord?: string;
    nakshatra?: string;
    nakshatra_index?: number;
    retro?: boolean;
  };
  planets: {
    [planetName: string]: {
      sign?: string;
      sign_sanskrit?: string;
      sign_index?: number;
      degree?: number;
      degrees_in_sign?: number;
      degree_dms?: number;
      arcminutes?: number;
      arcseconds?: number;
      house_lord?: string;
      lord?: string;
      nakshatra?: string;
      nakshatra_index?: number;
      retro?: boolean;
    };
  };
  planetFunctionalStrength?: Record<string, any>; // Planet functional strength data (D1 only)
}

export const PlanetDetailsTable: React.FC<PlanetDetailsTableProps> = ({
  chartType,
  ascendant,
  planets,
  planetFunctionalStrength,
}) => {
  // 🔒 D1 ONLY: Check if we should show extended columns
  const isD1 = chartType === 'D1';
  
  // Helper: Get status from functional strength data
  const getStatus = (planetName: string): string => {
    if (!isD1 || !planetFunctionalStrength) {
      // 🧪 DEBUG: Log when data is missing
      if (isD1 && !planetFunctionalStrength) {
        console.warn(`🧪 PlanetDetailsTable: Missing planetFunctionalStrength for ${planetName}`);
      }
      return '—';
    }
    const strength = planetFunctionalStrength[planetName];
    if (!strength) {
      // 🧪 DEBUG: Log when planet key doesn't match
      console.warn(`🧪 PlanetDetailsTable: Planet key mismatch - ${planetName} not found in planetFunctionalStrength`, {
        requestedPlanet: planetName,
        availableKeys: Object.keys(planetFunctionalStrength),
      });
      return '—';
    }
    
    if (strength.exaltation) return 'Exalted';
    if (strength.debilitation) return 'Debilitated';
    if (strength.own_sign) return 'Own Sign';
    return 'Normal';
  };
  
  // Helper: Get functional nature from association
  const getFunctionalNature = (planetName: string): string => {
    if (!isD1 || !planetFunctionalStrength) return '—';
    const strength = planetFunctionalStrength[planetName];
    if (!strength || !strength.association || strength.association.length === 0) return 'Neutral';
    
    const associations = strength.association;
    if (associations.includes('with_benefic')) return 'Benefic';
    if (associations.includes('with_malefic')) return 'Malefic';
    return 'Neutral';
  };
  
  // Helper: Get house type (capitalize first letter)
  const getHouseType = (planetName: string): string => {
    if (!isD1 || !planetFunctionalStrength) return '—';
    const strength = planetFunctionalStrength[planetName];
    if (!strength || !strength.house_type) return '—';
    
    const houseType = strength.house_type;
    // Capitalize first letter
    return houseType.charAt(0).toUpperCase() + houseType.slice(1);
  };
  
  // Helper: Get functional strength (capitalize first letter)
  const getFunctionalStrength = (planetName: string): string => {
    if (!isD1 || !planetFunctionalStrength) return '—';
    const strength = planetFunctionalStrength[planetName];
    if (!strength || !strength.functional_strength) return '—';
    
    const funcStrength = strength.functional_strength;
    // Capitalize first letter and replace underscores with spaces
    return funcStrength
      .split('_')
      .map((word: string) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };
  // Helper: Format degree as "degrees° minutes'"
  const formatDegree = (degree: number | undefined): string => {
    if (degree === undefined) return '-';
    const deg = Math.floor(degree);
    const min = Math.floor((degree - deg) * 60);
    return `${deg}° ${min.toString().padStart(2, '0')}'`;
  };

  // Helper: Format degree in sign (degrees_in_sign)
  const formatDegreeInSign = (
    degreesInSign: number | undefined,
    arcminutes: number | undefined,
    arcseconds: number | undefined
  ): string => {
    if (degreesInSign !== undefined) {
      const deg = Math.floor(degreesInSign);
      const min = arcminutes !== undefined ? arcminutes : Math.floor((degreesInSign - deg) * 60);
      return `${deg}° ${min.toString().padStart(2, '0')}'`;
    }
    return '-';
  };

  // Helper: Get sign name (prefer Sanskrit, fallback to English)
  const getSignName = (sign: string | undefined, signSanskrit: string | undefined): string => {
    return signSanskrit || sign || '-';
  };

  // Helper: Get rasi lord
  const getRasiLord = (
    sign: string | undefined,
    signSanskrit: string | undefined,
    houseLord: string | undefined,
    lord: string | undefined
  ): string => {
    // Prefer house_lord or lord from API
    if (houseLord) return houseLord;
    if (lord) return lord;
    
    // Fallback to lookup table
    const signName = signSanskrit || sign;
    if (signName) {
      return SIGN_LORDS[signName] || '-';
    }
    return '-';
  };

  // Build rows: Ascendant first, then planets in standard order
  const planetOrder = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu'];
  
  const rows = [
    // Ascendant row
    {
      name: 'Ascendant',
      symbol: PLANET_SYMBOLS['Ascendant'] || 'ASC',
      position: formatDegree(ascendant.degree),
      degrees: formatDegreeInSign(ascendant.degrees_in_sign, ascendant.arcminutes, ascendant.arcseconds),
      rasi: getSignName(ascendant.sign, ascendant.sign_sanskrit),
      rasiLord: getRasiLord(ascendant.sign, ascendant.sign_sanskrit, undefined, ascendant.lord),
      nakshatra: ascendant.nakshatra || '-',
      nakshatraLord: (ascendant as any).nakshatra_lord || '-',
      retrograde: ascendant.retro || false,
      // D1 extended fields (not applicable for Ascendant)
      status: '—',
      functionalNature: '—',
      houseType: '—',
      functionalStrength: '—',
    },
    // Planet rows
    ...planetOrder
      .filter(name => planets[name])
      .map(name => {
        const planet = planets[name];
        return {
          name,
          symbol: PLANET_SYMBOLS[name] || name.substring(0, 2),
          position: formatDegree(planet.degree),
          degrees: formatDegreeInSign(planet.degrees_in_sign, planet.arcminutes, planet.arcseconds),
          rasi: getSignName(planet.sign, planet.sign_sanskrit),
          rasiLord: getRasiLord(planet.sign, planet.sign_sanskrit, planet.house_lord, planet.lord),
          nakshatra: planet.nakshatra || '-',
          nakshatraLord: (planet as any).nakshatra_lord || '-',
          retrograde: planet.retro || false,
          // D1 extended fields
          status: getStatus(name),
          functionalNature: getFunctionalNature(name),
          houseType: getHouseType(name),
          functionalStrength: getFunctionalStrength(name),
        };
      }),
  ];

  return (
    <div className="mt-6 overflow-x-auto">
      <div className="glass rounded-lg border border-white/20 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-white/5 dark:bg-gray-800/50">
            <tr>
              <th className="px-4 py-3 text-left font-semibold text-gray-700 dark:text-gray-300">
                Planet
              </th>
              <th className="px-4 py-3 text-left font-semibold text-gray-700 dark:text-gray-300">
                Position
              </th>
              <th className="px-4 py-3 text-left font-semibold text-gray-700 dark:text-gray-300">
                Degrees
              </th>
              <th className="px-4 py-3 text-left font-semibold text-gray-700 dark:text-gray-300">
                Rasi
              </th>
              <th className="px-4 py-3 text-left font-semibold text-gray-700 dark:text-gray-300">
                Rasi Lord
              </th>
              <th className="px-4 py-3 text-left font-semibold text-gray-700 dark:text-gray-300">
                <span
                  className="inline-flex items-center gap-1"
                  title="Nakshatra is based on absolute longitude (D1) and is identical across all divisional charts."
                >
                  Nakshatra
                </span>
              </th>
              <th className="px-4 py-3 text-left font-semibold text-gray-700 dark:text-gray-300">
                <span
                  className="inline-flex items-center gap-1"
                  title="Nakshatra Lord is based on the D1 nakshatra and is identical across all divisional charts."
                >
                  Nakshatra Lord
                </span>
              </th>
              {/* D1 Extended Columns */}
              {isD1 && (
                <>
                  <th className="px-4 py-3 text-left font-semibold text-gray-700 dark:text-gray-300">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-700 dark:text-gray-300">
                    Functional Nature
                  </th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-700 dark:text-gray-300">
                    House Type
                  </th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-700 dark:text-gray-300">
                    Functional Strength
                  </th>
                </>
              )}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10 dark:divide-gray-700/50">
            {rows.map((row, index) => (
              <tr
                key={row.name}
                className={index % 2 === 0 ? 'bg-white/2 dark:bg-gray-800/20' : 'bg-white/5 dark:bg-gray-800/30'}
              >
                <td className="px-4 py-3 text-gray-800 dark:text-gray-200">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{row.symbol}</span>
                    <span className="font-medium">{row.name}</span>
                    {row.retrograde && (
                      <span className="text-xs text-amber-600 dark:text-amber-400" title="Retrograde">
                        (R)
                      </span>
                    )}
                  </div>
                </td>
                <td className="px-4 py-3 text-gray-700 dark:text-gray-300 font-mono">
                  {row.position}
                </td>
                <td className="px-4 py-3 text-gray-700 dark:text-gray-300 font-mono">
                  {row.degrees}
                </td>
                <td className="px-4 py-3 text-gray-700 dark:text-gray-300">
                  {row.rasi}
                </td>
                <td className="px-4 py-3 text-gray-700 dark:text-gray-300">
                  {row.rasiLord}
                </td>
                <td className="px-4 py-3 text-gray-700 dark:text-gray-300">
                  {row.nakshatra}
                </td>
                <td className="px-4 py-3 text-gray-700 dark:text-gray-300">
                  {row.nakshatraLord}
                </td>
                {/* D1 Extended Columns */}
                {isD1 && (
                  <>
                    <td className="px-4 py-3 text-gray-700 dark:text-gray-300">
                      {row.status}
                    </td>
                    <td className="px-4 py-3 text-gray-700 dark:text-gray-300">
                      {row.functionalNature}
                    </td>
                    <td className="px-4 py-3 text-gray-700 dark:text-gray-300">
                      {row.houseType}
                    </td>
                    <td className="px-4 py-3 text-gray-700 dark:text-gray-300">
                      {row.functionalStrength}
                    </td>
                  </>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
