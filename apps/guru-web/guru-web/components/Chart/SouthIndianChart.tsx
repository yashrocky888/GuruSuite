/**
 * South Indian Chart - SIGN-FIXED Renderer (NO CALCULATIONS)
 * 
 * ====================================================================
 * 🔒 CRITICAL ASTROLOGY RULE (NON-NEGOTIABLE - PERMANENTLY LOCKED)
 * ====================================================================
 * 
 * South Indian chart is SIGN-FIXED.
 * North Indian chart is LAGNA-ROTATED.
 * 
 * This is a FUNDAMENTAL Jyotish rule.
 * This applies to ALL charts: D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D30, D60 — ALL.
 * 
 * ====================================================================
 * PERMANENT RULE: South Indian chart is SIGN-FIXED. Do NOT rotate.
 * ====================================================================
 * 
 * This is NOT a UI preference.
 * This is NOT optional.
 * This is a CORE ASTROLOGY LAW.
 * 
 * Once applied:
 * ✔ South Indian chart is permanently correct
 * ✔ No future regression is allowed
 * ✔ Any rotation in South Indian chart is a BUG
 * 
 * ====================================================================
 * 
 * 🔒 ASTROLOGY LOCK
 * UI must NEVER calculate astrology.
 * API is the single source of truth.
 * 
 * SOUTH INDIAN CHART RULES:
 * 1. Signs are in FIXED positions (Aries, Taurus, Gemini, etc.) - NEVER MOVE
 * 2. Aries is ALWAYS in the SAME physical box
 * 3. Taurus is ALWAYS in the SAME physical box
 * 4. ... till Pisces
 * 5. Only PLANETS move between signs (based on planet.sign from API)
 * 6. Ascendant is DISPLAYED as a label/marker inside the sign it falls in
 * 7. Sign positions are STATIC - chart looks IDENTICAL for everyone
 * 
 * ❌ NEVER rotate the South Indian chart based on Ascendant
 * ❌ NEVER move Aries to House 1 visually
 * ❌ NEVER anchor South Indian chart to Lagna
 * 
 * SOUTH INDIAN CHART LAYOUT (FIXED):
 * Row 1:  capricorn | aquarius | pisces | aries
 * Row 2:  sagittarius |        |        | taurus
 * Row 3:  scorpio     |        |        | gemini
 * Row 4:  libra       | virgo   | leo    | cancer
 */

'use client';

import React, { useMemo } from 'react';
import { southRectPositions } from './coordinates';
import { normalizeSignName } from './houseUtils';
import './SouthIndianChart.css';

// 🔒 RASHI METADATA: Fixed rashi numbers and Sanskrit names in English (NON-NEGOTIABLE)
// Rashi numbers are FIXED: Aries = 1, Taurus = 2, ..., Pisces = 12
// These numbers DO NOT depend on Lagna or house - they are absolute zodiac order
// Rashi numbers NEVER rotate - even if Lagna = Scorpio, Mesha remains 1
const RASHI_META: Record<string, { number: number; name: string }> = {
  aries:       { number: 1,  name: 'Mesha' },
  taurus:      { number: 2,  name: 'Vrishabha' },
  gemini:      { number: 3,  name: 'Mithuna' },
  cancer:      { number: 4,  name: 'Karka' },
  leo:         { number: 5,  name: 'Simha' },
  virgo:       { number: 6,  name: 'Kanya' },
  libra:       { number: 7,  name: 'Tula' },
  scorpio:     { number: 8,  name: 'Vrischika' },
  sagittarius: { number: 9,  name: 'Dhanu' },
  capricorn:   { number: 10, name: 'Makara' },
  aquarius:    { number: 11, name: 'Kumbha' },
  pisces:      { number: 12, name: 'Meena' }
};

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
  houses: HouseData[]; // REQUIRED - this component renders charts with house structure (D1-D20)
  // NOTE: South Indian chart is SIGN-FIXED for ALL charts (D1-D60)
  // Signs never move. Only planets move between signs based on planet.sign from API.
}

export default function SouthIndianChart({ houses }: SouthIndianChartProps) {
  // 🔒 GUARD RAIL: South Indian chart is SIGN-FIXED for ALL charts (D1-D60)
  // This component renders charts with house structure (D1-D20)
  // Sign charts (D24-D60) must use SouthIndianSignChart component
  if (!houses || houses.length !== 12) {
    console.warn("⚠️ SouthIndianChart: Expected 12 houses, got:", houses?.length || 0);
    console.warn("   Sign charts (D24-D60) must use SouthIndianSignChart component instead.");
    return null; // Fail silently - NO throw
  }
  
  // 🔒 PERMANENT RULE: South Indian chart is SIGN-FIXED. Do NOT rotate.
  // This applies to ALL charts: D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, etc.
  // Signs are in FIXED positions. Only planets move between signs based on planet.sign from API.
  
  // Get Ascendant sign from house 1
  const ascendantHouse = houses.find(h => 
    h.planets.some(p => p.name === 'Ascendant' || p.abbr === 'Asc' || p.abbr === 'ASC')
  );
  
  const ascendantPlanet = ascendantHouse?.planets.find(p => 
    p.name === 'Ascendant' || p.abbr === 'Asc' || p.abbr === 'ASC'
  );
  
  const ascendantSign = ascendantPlanet?.sign || '';
  const normalizedAscendantSign = ascendantSign ? normalizeSignName(ascendantSign.toLowerCase()) : '';
  
  // 🔒 STEP 3: SOUTH INDIAN CHART INPUT CONTRACT
  // SouthIndianChart MUST:
  // - Receive houses + planets
  // - IGNORE house numbers for placement
  // - Group planets STRICTLY by planet.sign
  // - Render planets ONLY inside sign boxes
  // - Display Ascendant ONLY as marker in its sign
  // - Display house number ONLY as a label
  //
  // 🚫 DO NOT:
  // - Place planets by house
  // - Rotate grid
  // - Anchor to Lagna
  // - Apply D1 logic
  //
  // 🔒 CRITICAL FOR D4:
  // - D4 planets come DIRECTLY from API (planet.sign EXACTLY as provided)
  // - House-based pre-grouping is IGNORED
  // - Planets are grouped STRICTLY by planet.sign (NOT by house)
  //
  // This is the FUNDAMENTAL South Indian chart rule - applies to ALL charts (D1-D60)
  // Planets are placed STRICTLY using planet.sign from API
  // NEVER use planet.house to position planets in South Indian chart
  // NEVER calculate sign_index offsets, NEVER rotate based on Lagna
  const planetsBySign = useMemo(() => {
    const grouped: Record<string, Array<{
      name: string;
      abbr: string;
      sign: string;
      degree?: number;
      degree_dms?: number;
      degree_minutes?: number;
      degree_seconds?: number;
    }>> = {};
    
    // 🔒 CRITICAL: Collect ALL planets from ALL houses, grouped STRICTLY by planet.sign
    // For D4: This ensures planets are placed by their sign (from API), NOT by house
    // House structure is IGNORED for planet placement - only used for labels
    houses.forEach(house => {
      house.planets.forEach(planet => {
        // 🔒 ABSOLUTE RULE: Use planet.sign EXACTLY as provided (from API)
        // DO NOT infer from house, DO NOT recompute, DO NOT derive
        const planetSign = planet.sign;
        if (!planetSign) {
          console.warn(`⚠️ Planet ${planet.name} missing sign - skipping`);
          return;
        }
        
        const normalizedSign = normalizeSignName(planetSign.toLowerCase());
        if (!grouped[normalizedSign]) {
          grouped[normalizedSign] = [];
        }
        
        // Normalize ASC abbreviation
        const abbr = (planet.name === 'Ascendant' || planet.abbr === 'Asc' || planet.abbr === 'ASC') 
          ? 'ASC' 
          : planet.abbr;
        
        grouped[normalizedSign].push({
          name: planet.name,
          abbr,
          sign: planetSign, // Use planet.sign EXACTLY as provided (from API)
          degree: planet.degree,
          degree_dms: planet.degree_dms,
          degree_minutes: planet.degree_minutes,
          degree_seconds: planet.degree_seconds,
        });
      });
    });
    
    return grouped;
  }, [houses]);
  
  // 🔒 FIXED SIGN GRID: Standard South Indian Layout (NON-NEGOTIABLE)
  // 
  // Visual Layout (FIXED FOREVER):
  // Row 1: [Pisces] [Aries] [Taurus] [Gemini]
  // Row 2: [Aquarius] [CENTER] [Cancer]
  // Row 3: [Capricorn] [CENTER] [Leo]
  // Row 4: [Sagittarius] [Scorpio] [Libra] [Virgo]
  //
  // These signs are ALWAYS in the SAME physical positions - NEVER rotate
  // This applies to ALL charts: D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, etc.
  // Chart layout is IDENTICAL for every person - only planets move between signs
  // 
  // Sign positions are determined by sign_index (0-11) mapping to fixed coordinates:
  // - sign_index 0 (Aries/Mesha) → ALWAYS at coordinates (123, 10)
  // - sign_index 1 (Taurus/Vrishabha) → ALWAYS at coordinates (243, 10)
  // - sign_index 11 (Pisces/Meena) → ALWAYS at coordinates (3, 10)
  // etc.
  //
  // The order in this array doesn't matter - each sign is rendered at its fixed position
  // from southRectPositions. This array is just for iteration.
  const fixedSigns: Array<keyof typeof southRectPositions> = [
    'pisces',      // sign_index 11 - Fixed position: (3, 10)
    'aries',       // sign_index 0  - Fixed position: (123, 10) - ALWAYS SAME BOX
    'taurus',      // sign_index 1  - Fixed position: (243, 10) - ALWAYS SAME BOX
    'gemini',      // sign_index 2  - Fixed position: (363, 10)
    'aquarius',    // sign_index 10 - Fixed position: (3, 90)
    'cancer',      // sign_index 3  - Fixed position: (363, 90)
    'capricorn',   // sign_index 9  - Fixed position: (3, 170)
    'leo',         // sign_index 4  - Fixed position: (363, 170)
    'sagittarius', // sign_index 8  - Fixed position: (3, 250)
    'scorpio',     // sign_index 7  - Fixed position: (123, 250)
    'libra',       // sign_index 6  - Fixed position: (243, 250)
    'virgo'        // sign_index 5  - Fixed position: (363, 250)
  ];

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

        {/* Define clip paths for each sign box (prevents overflow) */}
        <defs>
          {fixedSigns.map((signKey) => {
            const rect = southRectPositions[signKey];
            if (!rect) return null;
            return (
              <clipPath key={`clip-${signKey}`} id={`clip-${signKey}`}>
                <rect
                  x={rect.x + 4}
                  y={rect.y + 4}
                  width={rect.width - 8}
                  height={rect.height - 8}
                  rx="3"
                />
              </clipPath>
            );
          })}
        </defs>

        {/* 🔒 SIGN-FIXED GRID: Render signs in FIXED positions */}
        {/* Aries is ALWAYS in the same box, Taurus is ALWAYS in the same box, etc. */}
        {/* Only planets move between signs based on planet.sign from API */}
        {fixedSigns.map((signKey) => {
          const rect = southRectPositions[signKey];
          if (!rect) {
            return null;
          }
          
          // Normalize sign name for matching
          const normalizedSign = normalizeSignName(signKey);
          
          // Check if this is the Ascendant sign
          const isAscendantSign = normalizedSign === normalizedAscendantSign;
          
          // Get planets in this sign (from API planet.sign)
          const planetsInSign = planetsBySign[normalizedSign] || [];

          const centerX = rect.x + rect.width / 2;
          const topY = rect.y + 18;
          const middleY = rect.y + rect.height / 2;

          return (
            <g key={signKey}>
              <rect
                id={signKey}
                x={rect.x}
                y={rect.y}
                width={rect.width}
                height={rect.height}
                fill={isAscendantSign ? 'rgba(212, 175, 55, 0.15)' : 'rgba(255, 255, 255, 0.08)'}
                stroke={isAscendantSign ? '#d4af37' : 'rgba(212, 175, 55, 0.5)'}
                strokeWidth={isAscendantSign ? '2.5' : '1.5'}
                className={isAscendantSign ? 'ascendant-sign' : ''}
                rx="4"
                style={{
                  filter: isAscendantSign ? 'drop-shadow(0 0 8px rgba(212, 175, 55, 0.4))' : 'none',
                  transition: 'all 0.3s ease',
                }}
              />
              
              {/* Rashi Number (Top) - FIXED zodiac number (1-12) */}
              {/* 🔒 CRITICAL: Rashi numbers are FIXED and NEVER depend on Lagna or house */}
              {/* Aries = 1, Taurus = 2, ..., Pisces = 12 - ALWAYS */}
              {RASHI_META[signKey] && (
              <text
                x={centerX}
                  y={middleY - 10}
                fill="#d4af37"
                textAnchor="middle"
                  className="rashi-number"
                style={{ 
                    fontSize: '13px',
                    fontWeight: 600,
                  fontFamily: 'sans-serif',
                  textShadow: '0 1px 2px rgba(0,0,0,0.3)'
                }}
              >
                  {RASHI_META[signKey].number}
              </text>
              )}

              {/* Rashi Name (Below Number) - Sanskrit name in English letters */}
              {/* 🔒 CRITICAL: Display ONLY the fixed Sanskrit rashi name */}
              {/* DO NOT use houseInSign?.signName as it may come from rotating houses */}
              {/* DO NOT add dots, DO NOT concatenate with number, DO NOT include house numbers */}
              {RASHI_META[signKey] && (
              <text
                x={centerX}
                  y={middleY + 8}
                fill="#ffb347"
                textAnchor="middle"
                className="rashi-name"
                style={{ 
                  fontSize: '17px', 
                    fontWeight: 700,
                  fontFamily: 'sans-serif',
                  textShadow: '0 1px 2px rgba(0,0,0,0.2)'
                }}
              >
                  {RASHI_META[signKey].name}
              </text>
              )}

              {/* FIX 1: Clip path wrapper - prevents ALL planet overflow to other signs */}
              <g clipPath={`url(#clip-${signKey})`}>

              {/* Planets - FIXED ROW HEIGHT WITH CENTERED STACKING */}
              {/* 🔒 CRITICAL: Planets are placed STRICTLY using planet.sign from API */}
              {/* NEVER use planet.house to position planets in South Indian chart */}
              {/* NEVER calculate sign_index offsets, NEVER rotate based on Lagna */}
              {/* ALL planets MUST be visible - NO planet may ever disappear */}
              {(() => {
                // Define safe vertical padding
                const topPadding = 44; // Space for rashi number and name
                const bottomPadding = 10; // Safety margin at bottom
                const availableHeight = rect.height - topPadding - bottomPadding;

                // Fixed row height per planet (professional density)
                const rowHeight = 16;

                // Split planets into two columns
                const total = planetsInSign.length;
                const leftPlanets = planetsInSign.slice(0, Math.ceil(total / 2));
                const rightPlanets = planetsInSign.slice(Math.ceil(total / 2));

                // Compute column heights
                const leftHeight = leftPlanets.length * rowHeight;
                const rightHeight = rightPlanets.length * rowHeight;
                const columnHeight = Math.max(leftHeight, rightHeight);

                // Vertically center planet block inside sign
                const startY = rect.y + topPadding + (availableHeight - columnHeight) / 2;

                // Fixed X positions (compact, balanced)
                const leftX = rect.x + rect.width * 0.28;
                const rightX = rect.x + rect.width * 0.72;

                // Helper function to render a planet
                // 🔒 CRITICAL: NEVER return null - ALL planets must render
                const renderPlanet = (planet: typeof planetsInSign[0], planetX: number, planetY: number, key: string) => {
                  // ❌ REMOVED: Overflow check that was hiding planets
                  // NO planet may ever be skipped or hidden

                const degreeText = planet.degree_dms !== undefined && planet.degree_dms !== null
                  ? (planet.degree_minutes !== undefined && planet.degree_minutes !== null
                      ? (planet.degree_seconds !== undefined && planet.degree_seconds !== null && planet.degree_seconds > 0
                          ? `${planet.degree_dms}° ${planet.degree_minutes}' ${planet.degree_seconds}"`
                          : `${planet.degree_dms}° ${planet.degree_minutes}'`)
                      : `${planet.degree_dms}°`)
                  : (planet.degree !== undefined && planet.degree !== null
                      ? `${planet.degree.toFixed(2)}°`
                      : '');

                  const isAscendant = planet.name === 'Ascendant' || 
                                    planet.abbr === 'ASC' || 
                                    planet.abbr === 'Asc' || 
                                    planet.abbr?.toUpperCase() === 'ASC';

                return (
                    <g key={key}>
                      {/* FIX 2: Reduced planet visual footprint - compact design */}
                    <circle
                      cx={planetX}
                        cy={planetY - 4}
                        r="6"
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
                          fontSize: '10px',
                        fontWeight: 700,
                        fontFamily: 'sans-serif'
                      }}
                    >
                      {planet.abbr}
                    </text>
                    
                      {/* FIX 5: Degree text position - below planet, white, no overlap */}
                    {degreeText && (
                      <text
                        x={planetX}
                          y={planetY + 8}
                        textAnchor="middle"
                        dominantBaseline="middle"
                          className={isAscendant ? 'asc-degree' : 'planet-degree'}
                        style={{ 
                            fontSize: '8px',
                          fontWeight: 500,
                          fontFamily: 'sans-serif',
                            fill: '#ffffff',
                            opacity: 1
                        }}
                      >
                        {degreeText}
                      </text>
                    )}
                  </g>
                );
                };

                return (
                  <>
                    {/* Render LEFT column - Fixed row height, centered stacking */}
                    {leftPlanets.map((planet, idx) => {
                      const planetX = leftX;
                      const planetY = startY + idx * rowHeight;
                      return renderPlanet(planet, planetX, planetY, `${signKey}-left-${planet.name}-${idx}`);
                    })}

                    {/* Render RIGHT column - Fixed row height, centered stacking */}
                    {rightPlanets.map((planet, idx) => {
                      const planetX = rightX;
                      const planetY = startY + idx * rowHeight;
                      return renderPlanet(planet, planetX, planetY, `${signKey}-right-${planet.name}-${idx}`);
                    })}
                  </>
                );
              })()}
              </g>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
