/**
 * North Indian Sign Chart - Pure Sign Renderer (NO HOUSES)
 * 
 * 🔒 ASTROLOGY LOCK
 * UI must NEVER calculate astrology.
 * API is the single source of truth.
 * 
 * CRITICAL RULES FOR PURE SIGN CHARTS (D24-D60):
 * 1. Signs are LAGNA-RELATIVE: Ascendant sign → House 1, other signs rotate
 * 2. Planets are placed by SIGN ONLY (from API Planets[].sign)
 * 3. NO houses - these are pure sign charts
 * 4. NO house numbers, NO house labels, NO house calculations
 * 
 * NORTH INDIAN CHART LAYOUT (LAGNA-RELATIVE):
 * House positions are static (house 1 = center, house 2 = NE, etc.)
 * Signs rotate so Ascendant sign occupies House 1
 * For sign charts: rotatedSigns[0] → House 1, rotatedSigns[1] → House 2, etc.
 */

'use client';

import React, { useMemo } from 'react';
import { getNorthCoordinates, northPolygonPoints } from './coordinates';
import { normalizeSignName, SIGN_INDEX } from './houseUtils';
import { RASHI_NAMES } from './utils';
import './NorthIndianChart.css';

interface PlanetData {
  name: string;
  abbr: string;
  sign: string;
  sign_sanskrit?: string;
  degree?: number;
}

interface NorthIndianSignChartProps {
  ascendant: {
    sign: string;
    sign_sanskrit?: string;
    sign_index?: number; // 0-11, required for Lagna rotation
    degree?: number;
  };
  planets: Record<string, {
    sign: string;
    sign_sanskrit?: string;
    sign_index?: number;
    degree?: number;
    [key: string]: any;
  }>;
  chartType?: string; // Chart type (e.g., "D24", "D27", etc.) - used for conditional verification
  // d24ChartMethod prop REMOVED - D24 is locked to Method 1 (JHora verified)
}

/**
 * Calculate centroid (center point) of a polygon
 * REUSED FROM NorthIndianChart.tsx - DO NOT MODIFY
 */
function getPolygonCentroid(pointsString: string): { x: number; y: number } {
  const points = pointsString.split(' ').map(point => {
    const [x, y] = point.split(',').map(Number);
    return { x, y };
  });

  let sumX = 0;
  let sumY = 0;
  points.forEach(point => {
    sumX += point.x;
    sumY += point.y;
  });

  return {
    x: sumX / points.length,
    y: sumY / points.length,
  };
}

/**
 * Get minimum distance from point to polygon edge
 * REUSED FROM NorthIndianChart.tsx - DO NOT MODIFY
 */
function getMinDistanceToEdge(point: { x: number; y: number }, polygonPoints: string): number {
  const points = polygonPoints.split(' ').map(p => {
    const [x, y] = p.split(',').map(Number);
    return { x, y };
  });

  let minDist = Infinity;
  for (let i = 0; i < points.length; i++) {
    const p1 = points[i];
    const p2 = points[(i + 1) % points.length];
    
    const A = point.x - p1.x;
    const B = point.y - p1.y;
    const C = p2.x - p1.x;
    const D = p2.y - p1.y;
    
    const dot = A * C + B * D;
    const lenSq = C * C + D * D;
    let param = -1;
    
    if (lenSq !== 0) param = dot / lenSq;
    
    let xx, yy;
    if (param < 0) {
      xx = p1.x;
      yy = p1.y;
    } else if (param > 1) {
      xx = p2.x;
      yy = p2.y;
    } else {
      xx = p1.x + param * C;
      yy = p1.y + param * D;
    }
    
    const dx = point.x - xx;
    const dy = point.y - yy;
    const dist = Math.sqrt(dx * dx + dy * dy);
    minDist = Math.min(minDist, dist);
  }
  
  return minDist;
}

/**
 * Calculate safe planet position - stay well inside polygon, away from edges
 * REUSED FROM NorthIndianChart.tsx - DO NOT MODIFY
 */
function getSafePlanetPosition(
  centroid: { x: number; y: number },
  originalCoords: { x: number; y: number },
  planetIdx: number,
  totalPlanets: number,
  polygonPoints: string
): { x: number; y: number } {
  const MIN_DISTANCE_FROM_EDGE = 20;
  
  const distanceFromEdge = getMinDistanceToEdge(originalCoords, polygonPoints);
  if (distanceFromEdge >= MIN_DISTANCE_FROM_EDGE) {
    return originalCoords;
  }

  const angle = (planetIdx / totalPlanets) * 2 * Math.PI;
  let radius = 20;
  let safeCoords = { x: 0, y: 0 };
  let attempts = 0;
  
  while (attempts < 15) {
    const testX = centroid.x + Math.cos(angle) * radius;
    const testY = centroid.y + Math.sin(angle) * radius + 10;
    
    const distToEdge = getMinDistanceToEdge({ x: testX, y: testY }, polygonPoints);
    if (distToEdge >= MIN_DISTANCE_FROM_EDGE) {
      safeCoords = { x: testX, y: testY };
      break;
    }
    radius -= 2;
    attempts++;
  }
  
  if (safeCoords.x === 0 && safeCoords.y === 0) {
    safeCoords = {
      x: centroid.x + (Math.cos(angle) * 10),
      y: centroid.y + (Math.sin(angle) * 10) + 15,
    };
  }

  return safeCoords;
}

export default function NorthIndianSignChart({ ascendant, planets, chartType }: NorthIndianSignChartProps) {
  // ============================================================================
  // 🔒 CRITICAL: NORTH INDIAN CHARTS MUST BE LAGNA-RELATIVE
  // Ascendant sign MUST appear in House 1 (top center diamond)
  // This is a NON-NEGOTIABLE Jyotish rule
  // ============================================================================
  
  console.log('🔵 NorthIndianSignChart INIT:', { 
    ascendantSign: ascendant.sign, 
    ascendantSignSanskrit: ascendant.sign_sanskrit,
    ascendantSignIndex: ascendant.sign_index 
  });
  
  // STEP 1: Extract ascendant sign (prefer Sanskrit, fallback to English)
  const ascendantSign = ascendant.sign_sanskrit || ascendant.sign;
  if (!ascendantSign) {
    throw new Error('FATAL: Ascendant sign is missing - cannot render sign chart');
  }
  
  // STEP 2: Normalize ascendant sign name (CRITICAL for matching)
  const normalizedAscendantSign = normalizeSignName(ascendantSign.toLowerCase());
  const expectedIndex = SIGN_INDEX[normalizedAscendantSign];
  
  if (expectedIndex === undefined) {
    throw new Error(`FATAL: Cannot normalize ascendant sign "${ascendantSign}" - invalid sign name. Normalized: "${normalizedAscendantSign}"`);
  }
  
  console.log(`📊 STEP 2: Normalized ascendant sign "${ascendantSign}" → "${normalizedAscendantSign}" (index ${expectedIndex})`);
  
  // STEP 3: Get ascendant sign index (0-11) for Lagna rotation
  // Priority: API sign_index (if valid) → Derived from sign name
  let ascendantSignIndex: number;
  
  if (ascendant.sign_index !== undefined && ascendant.sign_index >= 0 && ascendant.sign_index <= 11) {
    // API provided index - verify it matches sign name
    if (ascendant.sign_index !== expectedIndex) {
      console.warn(`⚠️ API ascendantSignIndex (${ascendant.sign_index}) does not match sign "${ascendantSign}" (expected ${expectedIndex}). Using derived index.`);
      ascendantSignIndex = expectedIndex;
    } else {
      ascendantSignIndex = ascendant.sign_index;
      console.log(`✅ Using API ascendantSignIndex: ${ascendantSignIndex}`);
    }
  } else {
    // Derive from sign name
    ascendantSignIndex = expectedIndex;
    console.log(`🔧 Derived ascendantSignIndex ${ascendantSignIndex} from sign "${ascendantSign}"`);
  }
  
  // STEP 4: Final validation - index must be valid
  if (ascendantSignIndex < 0 || ascendantSignIndex > 11) {
    throw new Error(`FATAL: Invalid ascendantSignIndex ${ascendantSignIndex} - must be 0-11`);
  }
  
  console.log(`✅ FINAL: Ascendant sign="${ascendantSign}" (normalized="${normalizedAscendantSign}"), index=${ascendantSignIndex}`);
  
  // ============================================================================
  // CRITICAL: GROUP PLANETS BY SIGN (PURE SIGN CHART LOGIC)
  // ============================================================================
  // For D24-D60: Planets are placed ONLY by planet.sign from API
  // API planet.sign is the SINGLE SOURCE OF TRUTH
  // We MUST normalize correctly to match rotated signs
  // ============================================================================
  const planetsBySign = useMemo(() => {
    const grouped: Record<string, PlanetData[]> = {};
    
    console.log('📦 GROUPING PLANETS BY SIGN (from API data):');
    console.log('   Raw API planets:', Object.keys(planets));
    
    // Add Ascendant as a planet in its sign
    const normalizedAscendantSignForGrouping = normalizeSignName(ascendantSign.toLowerCase());
    if (!grouped[normalizedAscendantSignForGrouping]) {
      grouped[normalizedAscendantSignForGrouping] = [];
    }
    grouped[normalizedAscendantSignForGrouping].push({
      name: 'Ascendant',
      abbr: 'Asc',
      sign: ascendantSign,
      sign_sanskrit: ascendant.sign_sanskrit,
      degree: ascendant.degree,
    });
    console.log(`   ✅ Ascendant → sign="${ascendantSign}" (normalized="${normalizedAscendantSignForGrouping}")`);
    
    // Add all other planets - CRITICAL: Use EXACT sign from API
    Object.entries(planets).forEach(([name, planet]) => {
      // Extract sign from planet (prefer sign_sanskrit, fallback to sign)
      const planetSign = planet.sign_sanskrit || planet.sign;
      if (!planetSign) {
        console.warn(`   ⚠️ ${name}: Missing sign data, skipping`);
        return; // Skip planets without sign
      }
      
      const normalizedSign = normalizeSignName(planetSign.toLowerCase());
      if (!grouped[normalizedSign]) {
        grouped[normalizedSign] = [];
      }
      
      // Build planet data with abbreviation
      grouped[normalizedSign].push({
        name,
        abbr: name.substring(0, 2),
        sign: planetSign,
        sign_sanskrit: planet.sign_sanskrit,
        degree: planet.degree,
      });
      
      console.log(`   ✅ ${name} → sign="${planetSign}" (normalized="${normalizedSign}")`);
    });
    
    // Log final grouping for verification
    console.log('📊 PLANETS BY SIGN (final grouping - verify against Prokerala):');
    Object.entries(grouped).forEach(([sign, planetList]) => {
      const planetNames = planetList.map(p => p.name).join(', ');
      console.log(`   ${sign}: [${planetNames}]`);
    });
    
    return grouped;
  }, [planets, ascendantSign, ascendant]);
  
  // CRITICAL: Create rotated sign array for Lagna-relative North Indian chart
  // Ascendant sign must be at index 0 (House 1), other signs rotate accordingly
  const signNames = ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo',
                     'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces'];
  
  // ============================================================================
  // STEP 5: ROTATE SIGNS ARRAY (CRITICAL - LAGNA-RELATIVE LAYOUT)
  // ============================================================================
  // Formula: rotatedSigns[i] = signNames[(ascendantSignIndex + i) % 12]
  // This ensures Ascendant sign (at ascendantSignIndex) becomes rotatedSigns[0]
  // rotatedSigns[0] → House 1, rotatedSigns[1] → House 2, etc.
  // Example: If Ascendant is Leo (index 4):
  //   rotatedSigns[0] = signNames[(4+0)%12] = signNames[4] = "leo" → House 1 ✅
  //   rotatedSigns[1] = signNames[(4+1)%12] = signNames[5] = "virgo" → House 2
  // ============================================================================
  const rotatedSigns = useMemo(() => {
    if (ascendantSignIndex < 0 || ascendantSignIndex > 11) {
      throw new Error(`FATAL: Invalid ascendantSignIndex ${ascendantSignIndex} for rotation`);
    }
    
    console.log(`🔄 ROTATION START: ascendantSignIndex=${ascendantSignIndex}, signNames[${ascendantSignIndex}]="${signNames[ascendantSignIndex]}"`);
    
    const rotated: string[] = [];
    for (let i = 0; i < 12; i++) {
      const rotatedIndex = (ascendantSignIndex + i) % 12;
      const signName = signNames[rotatedIndex];
      rotated.push(signName);
      if (i < 3) {
        console.log(`   rotatedSigns[${i}] = signNames[${rotatedIndex}] = "${signName}" → House ${i + 1}`);
      }
    }
    
    // CRITICAL VERIFICATION: rotatedSigns[0] MUST be the ascendant sign
    const firstSignNormalized = normalizeSignName(rotated[0]);
    if (firstSignNormalized !== normalizedAscendantSign) {
      const errorMsg = `FATAL: Rotation failed! rotatedSigns[0]="${rotated[0]}" (normalized="${firstSignNormalized}") ` +
        `does not match ascendant sign "${ascendantSign}" (normalized="${normalizedAscendantSign}") ` +
        `with ascendantSignIndex=${ascendantSignIndex}. ` +
        `Expected signNames[${ascendantSignIndex}]="${signNames[ascendantSignIndex]}" but got "${rotated[0]}"`;
      console.error(`❌ ${errorMsg}`);
      throw new Error(errorMsg);
    }
    
    console.log(`✅ ROTATION VERIFIED: rotatedSigns[0]="${rotated[0]}" (normalized="${firstSignNormalized}") matches ascendant → House 1`);
    return rotated;
  }, [ascendantSignIndex, normalizedAscendantSign, ascendantSign]);
  
  // ============================================================================
  // CONDITIONAL VERIFICATION CHECKPOINT (After rotation and grouping)
  // ============================================================================
  // ⚠️ CRITICAL: D24 is NOT VERIFIED and supports multiple classical methods
  // Planet-sign assertions are ONLY for verification mode, NOT normal rendering
  // ============================================================================
  const isD24 = chartType === 'D24' || chartType === 'd24';
  // D24 is LOCKED to Method 1 (JHora verified) - no method switching
  // Verification mode: Only in development, for Method 1 results
  const isVerificationMode = process.env.NODE_ENV === 'development' && isD24;
  
  if (isD24) {
    console.log(`🔍 D24 VERIFICATION CHECKPOINT (Method 1 - JHora Verified):`);
    console.log(`   Chart Type: D24`);
    console.log(`   Chart Method: 1 (Traditional Parasara Siddhamsa - JHora verified)`);
    console.log(`   Verification Mode: ${isVerificationMode ? 'ENABLED' : 'DISABLED'}`);
    
    // Log planet placements for verification (Method 1 expected results)
    if (isVerificationMode) {
      console.log(`   Expected (JHora Method 1): Traditional Parasara Siddhamsa results`);
      const saturnSign = Object.entries(planetsBySign).find(([_, planets]) => 
        planets.some(p => p.name === 'Saturn')
      )?.[0];
      if (saturnSign) {
        console.log(`   ℹ️ Saturn is in ${saturnSign} sign (Method 1)`);
      }
      // Log all planet placements for verification
      Object.entries(planetsBySign).forEach(([sign, planets]) => {
        const planetNames = planets.map(p => p.name).join(', ');
        if (planetNames) {
          console.log(`   ℹ️ ${sign}: [${planetNames}]`);
        }
      });
    } else {
      // Normal mode: Just log planet placements
      const saturnSign = Object.entries(planetsBySign).find(([_, planets]) => 
        planets.some(p => p.name === 'Saturn')
      )?.[0];
      if (saturnSign) {
        console.log(`   ℹ️ Saturn is in ${saturnSign} sign (Method 1 - JHora verified)`);
      }
    }
  }
  
  // Log full rotation map
  console.log('🔄 FULL ROTATION MAP (verify against Prokerala):');
  rotatedSigns.forEach((sign, idx) => {
    const normalized = normalizeSignName(sign);
    const planetsInThisSign = planetsBySign[normalized] || [];
    const planetNames = planetsInThisSign.map(p => p.name).join(', ') || 'NONE';
    console.log(`   House ${idx + 1}: ${sign} (normalized="${normalized}") → [${planetNames}]`);
  });
  
  return (
    <div className="north-chart-wrapper">
      <svg
        className="north-chart-svg"
        width="420"
        height="420"
        viewBox="0 0 420 420"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Background */}
        <rect
          width="410"
          height="410"
          x="5"
          y="5"
          fill="rgba(255, 255, 255, 0.05)"
          stroke="rgba(212, 175, 55, 0.4)"
          strokeWidth="2"
          rx="8"
        />

        {/* ============================================================================ */}
        {/* SIGN POLYGONS - LAGNA-RELATIVE POSITIONS (CRITICAL) */}
        {/* Ascendant sign → House 1, other signs rotate accordingly */}
        {/* ============================================================================ */}
        {rotatedSigns.map((signName, rotatedIndex) => {
          // CRITICAL: House number = rotatedIndex + 1 (NOT original zodiac index)
          const houseNum = rotatedIndex + 1;
          const points = northPolygonPoints[houseNum];
          if (!points) {
            console.error(`❌ FATAL: No polygon points for house ${houseNum}`);
            return null;
          }
          
          // Normalize sign name for matching
          const normalizedSign = normalizeSignName(signName);
          const isAscendantSign = normalizedSign === normalizedAscendantSign;
          const planetsInSign = planetsBySign[normalizedSign] || [];
          
          // CRITICAL DEBUG: Log planet placement for each sign (verify against Prokerala)
          if (planetsInSign.length > 0) {
            const planetNames = planetsInSign.map(p => `${p.name}(${p.sign})`).join(', ');
            console.log(`📍 House ${houseNum} (${signName}, normalized="${normalizedSign}"): Planets=[${planetNames}]`);
          } else {
            // Log empty signs for debugging
            if (houseNum <= 4) {
              console.log(`📍 House ${houseNum} (${signName}, normalized="${normalizedSign}"): NO PLANETS`);
            }
          }
          
          // ============================================================================
          // CRITICAL SAFETY GUARD: Ascendant sign MUST be in House 1
          // This is a NON-NEGOTIABLE Jyotish rule for North Indian charts
          // ============================================================================
          if (houseNum === 1) {
            if (!isAscendantSign) {
              const errorMsg = `FATAL: House 1 does NOT contain Ascendant sign! ` +
                `House 1 has "${signName}" (normalized: "${normalizedSign}"), ` +
                `but Ascendant is "${ascendantSign}" (normalized: "${normalizedAscendantSign}") ` +
                `with ascendantSignIndex=${ascendantSignIndex}. ` +
                `rotatedSigns[0]="${rotatedSigns[0]}" should be the ascendant sign.`;
              console.error(`❌ ${errorMsg}`);
              throw new Error(errorMsg);
            } else {
              console.log(`✅ House 1 VERIFIED: Contains Ascendant sign "${signName}" (normalized: "${normalizedSign}")`);
            }
          }
          
          if (isAscendantSign && houseNum !== 1) {
            const errorMsg = `FATAL: Ascendant sign "${signName}" is in House ${houseNum}, but MUST be in House 1! ` +
              `This violates North Indian chart Lagna-relative rule. ` +
              `rotatedSigns[${rotatedIndex}]="${signName}" should only be at rotatedIndex=0.`;
            console.error(`❌ ${errorMsg}`);
            throw new Error(errorMsg);
          }
          const centroid = getPolygonCentroid(points);
          
          return (
            <g key={signName}>
              <polygon
                id={`sign-${signName}`}
                points={points}
                fill="rgba(255, 255, 255, 0.08)"
                stroke={isAscendantSign ? '#d4af37' : 'rgba(212, 175, 55, 0.5)'}
                strokeWidth={isAscendantSign ? '2.5' : '1.5'}
                className={isAscendantSign ? 'ascendant-sign' : ''}
                style={{
                  filter: isAscendantSign ? 'drop-shadow(0 0 8px rgba(212, 175, 55, 0.4))' : 'none',
                }}
              />
              
              {/* Sign Name - Use Sanskrit name matching D1-D20 */}
              <text
                x={centroid.x}
                y={centroid.y}
                fill="#ffb347"
                textAnchor="middle"
                dominantBaseline="middle"
                className="rashi-name"
                style={{ 
                  fontSize: '17px', 
                  fontWeight: 600,
                  fontFamily: 'sans-serif',
                  textShadow: '0 1px 2px rgba(0,0,0,0.2)'
                }}
              >
                {(() => {
                  // Get sign index (0-11) from normalized sign name
                  const signIndex = SIGN_INDEX[normalizedSign];
                  if (signIndex !== undefined) {
                    // RASHI_NAMES uses 1-12, so add 1
                    return RASHI_NAMES[signIndex + 1] || signName.charAt(0).toUpperCase() + signName.slice(1);
                  }
                  return signName.charAt(0).toUpperCase() + signName.slice(1);
                })()}
              </text>

              {/* Planets - REUSE EXACT SAME LOGIC AS NorthIndianChart.tsx */}
              {/* CRITICAL: Render EXACTLY the planets received from API - no caps, no filtering, no reordering */}
              {/* CRITICAL: Ascendant behaves exactly like a planet ("Asc") */}
              {/* CRITICAL: Use rotated house number for planet placement */}
              {planetsInSign.map((planet, planetIdx) => {
                // Use rotated house number (from Lagna-relative mapping)
                const polygonPoints = northPolygonPoints[houseNum];
                const centroid = getPolygonCentroid(polygonPoints);
                
                // REUSE EXACT SAME LOGIC AS NorthIndianChart.tsx
                const originalCoords = getNorthCoordinates(houseNum, planetIdx + 1);
                
                if (originalCoords.x === 0 && originalCoords.y === 0) {
                  return null;
                }

                const safeCoords = getSafePlanetPosition(
                  centroid,
                  originalCoords,
                  planetIdx,
                  planetsInSign.length,
                  polygonPoints
                );

                // CRITICAL: Detect ASC regardless of case or exact abbreviation (EXACT SAME AS D1-D20)
                const isAscendant = planet.name === 'Ascendant' || 
                                  planet.abbr === 'ASC' || 
                                  planet.abbr === 'Asc' || 
                                  planet.abbr?.toUpperCase() === 'ASC';

                return (
                  <g key={`${signName}-${planet.name}-${planetIdx}`}>
                    <circle
                      cx={safeCoords.x}
                      cy={safeCoords.y - 6}
                      r="11"
                      fill="rgba(59, 130, 246, 0.15)"
                      stroke="rgba(59, 130, 246, 0.3)"
                      strokeWidth="1"
                    />
                    
                    <text
                      x={safeCoords.x}
                      y={safeCoords.y}
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
                    
                    {/* NO DEGREE TEXT FOR SIGN CHARTS (D24-D60) */}
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

