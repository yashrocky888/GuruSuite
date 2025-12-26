/**
 * South Indian Chart - Pure Renderer (NO CALCULATIONS)
 * 
 * 🔒 ASTROLOGY LOCK
 * UI must NEVER calculate astrology.
 * API is the single source of truth.
 * 
 * CRITICAL RULES FOR SOUTH INDIAN CHARTS:
 * 1. Signs are in FIXED positions (Aries top-left, etc.) - NEVER MOVE
 * 2. Each sign box shows which HOUSE occupies that sign (from API Houses[] array)
 * 3. Planets are placed by HOUSE NUMBER from API (not by sign lookup)
 * 4. NO sign→house lookup. NO house calculation. Use API data directly.
 * 
 * SOUTH INDIAN CHART LAYOUT (FIXED):
 * Row 1:  capricorn | aquarius | pisces | aries
 * Row 2:  sagittarius |        |        | taurus
 * Row 3:  scorpio     |        |        | gemini
 * Row 4:  libra       | virgo   | leo    | cancer
 */

'use client';

// 🔥 VERIFICATION LOG - If this appears for D24, routing is wrong
console.log("🔥 SouthIndianChart LOADED", Date.now());

import React, { useMemo } from 'react';
import { southRectPositions } from './coordinates';
import { normalizeSignName } from './houseUtils';
import './SouthIndianChart.css';

interface HouseData {
  houseNumber: number;
  signNumber: number;
  signName: string;
  planets: Array<{ 
    name: string; 
    abbr: string; 
    sign: string;
    degree?: number;
    degree_dms?: number;
    degree_minutes?: number;
    degree_seconds?: number;
  }>;
}

interface SouthIndianChartProps {
  houses: HouseData[]; // REQUIRED - this component is ONLY for house charts
}

export default function SouthIndianChart({ houses }: SouthIndianChartProps) {
  // 🔒 CRITICAL: Log when this component is called (should NEVER happen for D24-D60)
  console.log("🏠 SouthIndianChart CALLED with houses.length:", houses?.length || 0);
  
  // GUARD RAIL: This component is ONLY for house-based charts (D1-D20)
  // Sign charts (D24-D60) must use SouthIndianSignChart component
  if (!houses || houses.length !== 12) {
    console.error("❌ FATAL: SouthIndianChart called incorrectly!");
    console.error("   Expected 12 houses, got:", houses?.length || 0);
    console.error("   This component is ONLY for house-based charts (D1-D20)");
    console.error("   Sign charts (D24-D60) must use SouthIndianSignChart component instead.");
    throw new Error(
      `FATAL: SouthIndianChart used incorrectly. ` +
      `Expected 12 houses, got ${houses?.length || 0}. ` +
      `Sign charts (D24-D60) must use SouthIndianSignChart component instead.`
    );
  }
  
  console.log("🏠 SouthIndianChart RENDERING (house-based chart)");
  
  // RUNTIME ASSERTION: Ascendant must be in house 1
  const ascendantHouse = houses.find(h => 
    h.planets.some(p => p.name === 'Ascendant' || p.abbr === 'Asc')
  );
  
  if (!ascendantHouse) {
    throw new Error('FATAL: Ascendant must be present in houses array');
  }
  
  if (ascendantHouse.houseNumber !== 1) {
    throw new Error(`FATAL: Ascendant must be in house 1, found in house ${ascendantHouse.houseNumber}`);
  }

  // CRITICAL: Ascendant sign must come ONLY from Ascendant planet in house 1
  // NO fallbacks. NO derivation from house signName. NO defaults.
  const ascendantPlanet = ascendantHouse.planets.find(p => p.name === 'Ascendant' || p.abbr === 'Asc');
  
  if (!ascendantPlanet || !ascendantPlanet.sign) {
    throw new Error('FATAL: Ascendant sign is missing - cannot render chart');
  }
  
  // Use ascendant sign directly from API (no fallbacks)
  const ascendantSignRaw = ascendantPlanet.sign.toLowerCase();
  const normalizedAscendantSign = normalizeSignName(ascendantSignRaw);
  
  // RUNTIME LOG: Verify ascendant sign is correct
  console.log("ASC SIGN USED:", ascendantSignRaw, "→ normalized:", normalizedAscendantSign);

  // CRITICAL: Build house→sign map ONLY from API response
  // NO calculations. NO rotations. NO hardcoded grids.
  // PURE RENDERER: Use API data directly
  const houseSignMap = new Map<number, string>();
  const signToHouseMap = new Map<string, number>();
  houses.forEach(house => {
    houseSignMap.set(house.houseNumber, house.signName);
    // Also build reverse map: sign → house number (for finding which house has a given sign)
    const normalizedSign = normalizeSignName(house.signName);
    signToHouseMap.set(normalizedSign, house.houseNumber);
  });
  
  console.log("HOUSE→SIGN MAP (from API):", Array.from(houseSignMap.entries()).map(([h, s]) => `H${h}=${s}`).join(', '));

  // CRITICAL: Normalize ASC abbreviation to "ASC" for all houses
  // ASC must be rendered exactly like a planet - same styling, same placement
  const normalizedHouses = houses.map(house => ({
    ...house,
    planets: house.planets.map(planet => {
      if (planet.name === 'Ascendant' || planet.abbr === 'Asc' || planet.abbr === 'ASC') {
        return { ...planet, abbr: 'ASC' }; // Normalize to "ASC"
      }
      return planet;
    })
  }));

  return (
    <div className="south-chart-wrapper">
      <svg
        className="south-chart-svg"
        width="490"
        height="340"
        viewBox="0 0 490 340"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Background */}
        <rect
          id="border"
          width="486"
          height="327"
          x="0"
          y="7"
          fill="rgba(255, 255, 255, 0.05)"
          stroke="rgba(212, 175, 55, 0.4)"
          strokeWidth="2"
          rx="8"
        />

        {/* Center empty box */}
        <rect
          id="center"
          width="235"
          height="156"
          x="126"
          y="92"
          fill="rgba(255, 255, 255, 0.02)"
          stroke="rgba(212, 175, 55, 0.3)"
          strokeWidth="2"
          rx="4"
        />

        {/* Sign Rectangles - PURE RENDERER (NO CALCULATIONS) */}
        {/* Each fixed sign box position displays the house that has that sign (from API) */}
        {/* NO rotation. NO hardcoded grids. Use API house→sign map directly. */}
        {(['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 
           'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces'] as const).map((fixedSignKey) => {
          const rect = southRectPositions[fixedSignKey];
          if (!rect) {
            return null;
          }
          
          // CRITICAL: Find which house has this sign using API house→sign map
          // NO rotation. NO calculation. Just lookup which house API says has this sign.
          const normalizedFixedSign = normalizeSignName(fixedSignKey);
          const houseNumber = signToHouseMap.get(normalizedFixedSign);
          
          // SAFE RENDERING: If house not found for this sign, skip rendering
          // This should never happen if API data is correct, but handle gracefully
          if (!houseNumber) {
            return null; // Skip this sign box silently
          }
          
          // Get house data by house number (use normalized houses with ASC normalized)
          const house = normalizedHouses.find(h => h.houseNumber === houseNumber);
          if (!house) {
            return null; // Skip if house data not found
          }

          // Check if this is house 1 (Ascendant house)
          const isAscendant = house.houseNumber === 1;

          const centerX = rect.x + rect.width / 2;
          const topY = rect.y + 18;
          const middleY = rect.y + rect.height / 2;
          const planetAreaStartY = rect.y + rect.height - 35;

          return (
            <g key={fixedSignKey}>
              <rect
                id={fixedSignKey}
                x={rect.x}
                y={rect.y}
                width={rect.width}
                height={rect.height}
                fill={isAscendant ? 'rgba(212, 175, 55, 0.15)' : 'rgba(255, 255, 255, 0.08)'}
                stroke={isAscendant ? '#d4af37' : 'rgba(212, 175, 55, 0.5)'}
                strokeWidth={isAscendant ? '2.5' : '1.5'}
                className={isAscendant ? 'ascendant-sign' : ''}
                rx="4"
                style={{
                  filter: isAscendant ? 'drop-shadow(0 0 8px rgba(212, 175, 55, 0.4))' : 'none',
                  transition: 'all 0.3s ease',
                }}
              />
              
              {/* House Number (Top) */}
              <text
                x={centerX}
                y={topY}
                fill="#d4af37"
                textAnchor="middle"
                className="house-number"
                style={{ 
                  fontSize: '15px', 
                  fontWeight: 700,
                  fontFamily: 'sans-serif',
                  textShadow: '0 1px 2px rgba(0,0,0,0.3)'
                }}
              >
                {house.houseNumber}
              </text>

              {/* Rashi Name (Middle) */}
              <text
                x={centerX}
                y={middleY}
                fill="#ffb347"
                textAnchor="middle"
                className="rashi-name"
                style={{ 
                  fontSize: '17px', 
                  fontWeight: 600,
                  fontFamily: 'sans-serif',
                  textShadow: '0 1px 2px rgba(0,0,0,0.2)'
                }}
              >
                {house.signName}
              </text>

              {/* Planets - Positioned at bottom */}
              {/* CRITICAL: ASC is rendered here as a planet (no separate label) - ASC rendered using shared style for consistency */}
              {house.planets.map((planet, planetIdx) => {
                const totalPlanets = house.planets.length;
                const planetSpacing = Math.min(rect.width / (totalPlanets + 1), 30);
                const startX = rect.x + planetSpacing;
                const planetX = startX + (planetIdx * planetSpacing);
                const planetY = planetAreaStartY - (planetIdx % 2) * 18;

                const degreeText = planet.degree_dms !== undefined && planet.degree_dms !== null
                  ? (planet.degree_minutes !== undefined && planet.degree_minutes !== null
                      ? (planet.degree_seconds !== undefined && planet.degree_seconds !== null && planet.degree_seconds > 0
                          ? `${planet.degree_dms}° ${planet.degree_minutes}' ${planet.degree_seconds}"`
                          : `${planet.degree_dms}° ${planet.degree_minutes}'`)
                      : `${planet.degree_dms}°`)
                  : (planet.degree !== undefined && planet.degree !== null
                      ? `${planet.degree.toFixed(2)}°`
                      : '');

                // CRITICAL: Detect ASC regardless of case or exact abbreviation
                const isAscendant = planet.name === 'Ascendant' || 
                                  planet.abbr === 'ASC' || 
                                  planet.abbr === 'Asc' || 
                                  planet.abbr?.toUpperCase() === 'ASC';

                return (
                  <g key={`${house.houseNumber}-${planet.name}-${planetIdx}`}>
                    <circle
                      cx={planetX}
                      cy={planetY - 6}
                      r="11"
                      fill="rgba(59, 130, 246, 0.15)"
                      stroke="rgba(59, 130, 246, 0.3)"
                      strokeWidth="1"
                    />
                    
                    <text
                      x={planetX}
                      y={planetY}
                      textAnchor="middle"
                      dominantBaseline="middle"
                      className={isAscendant ? 'asc-text' : 'planet-text'}
                      style={{ 
                        fontSize: '12px',
                        fontWeight: 700,
                        fontFamily: 'sans-serif'
                      }}
                    >
                      {planet.abbr}
                    </text>
                    
                    {degreeText && (
                      <text
                        x={planetX}
                        y={planetY + 15}
                        textAnchor="middle"
                        dominantBaseline="middle"
                        className={isAscendant ? 'asc-degree' : 'planet-degree'}
                        style={{ 
                          fontSize: '9px',
                          fontWeight: 500,
                          fontFamily: 'sans-serif',
                          opacity: 0.85
                        }}
                      >
                        {degreeText}
                      </text>
                    )}
                  </g>
                );
              })}
            </g>
          );
        })}

        {/* NO SEPARATE ASCENDANT LABEL - Ascendant is rendered as a planet inside its sign */}
      </svg>
    </div>
  );
}
