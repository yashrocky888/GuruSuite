/**
 * North Indian Sign Chart - Pure Sign Renderer (NO HOUSES)
 * 
 * 🔒 ASTROLOGY LOCK
 * UI must NEVER calculate astrology.
 * API is the single source of truth.
 * 
 * CRITICAL RULES FOR PURE SIGN CHARTS (D24-D60):
 * 1. Signs are in FIXED positions (same as NorthIndianChart layout) - NEVER MOVE
 * 2. Planets are placed by SIGN ONLY (from API Planets[].sign)
 * 3. NO houses - these are pure sign charts
 * 4. NO house numbers, NO house labels, NO house calculations
 * 
 * NORTH INDIAN CHART LAYOUT (FIXED):
 * House positions are static (house 1 = center, house 2 = NE, etc.)
 * For sign charts: sign_index + 1 = house polygon position
 */

'use client';

import React, { useMemo } from 'react';
import { northPolygonPoints } from './coordinates';
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
    degree?: number;
  };
  planets: Record<string, {
    sign: string;
    sign_sanskrit?: string;
    degree?: number;
    [key: string]: any;
  }>;
}

/**
 * Calculate centroid (center point) of a polygon
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

export default function NorthIndianSignChart({ ascendant, planets }: NorthIndianSignChartProps) {
  // GUARD RAIL: This component must NEVER accept houses
  // Sign charts have NO house structure
  
  // Extract ascendant sign (prefer Sanskrit, fallback to English)
  const ascendantSign = ascendant.sign_sanskrit || ascendant.sign;
  if (!ascendantSign) {
    throw new Error('FATAL: Ascendant sign is missing - cannot render sign chart');
  }
  
  // Group planets by sign
  // CRITICAL: Treat Ascendant as a planet - add it to the planets list
  const planetsBySign = useMemo(() => {
    const grouped: Record<string, PlanetData[]> = {};
    
    // Add Ascendant as a planet in its sign
    const normalizedAscendantSign = normalizeSignName(ascendantSign.toLowerCase());
    if (!grouped[normalizedAscendantSign]) {
      grouped[normalizedAscendantSign] = [];
    }
    grouped[normalizedAscendantSign].push({
      name: 'Ascendant',
      abbr: 'Asc', // Match D1-D20 casing (not ALL CAPS)
      sign: ascendantSign,
      sign_sanskrit: ascendant.sign_sanskrit,
      degree: ascendant.degree, // Will be hidden for sign charts
    });
    
    // Add all other planets
    Object.entries(planets).forEach(([name, planet]) => {
      // Extract sign from planet (prefer sign_sanskrit, fallback to sign)
      const planetSign = planet.sign_sanskrit || planet.sign;
      if (!planetSign) {
        return; // Skip planets without sign
      }
      
      const normalizedSign = normalizeSignName(planetSign.toLowerCase());
      if (!grouped[normalizedSign]) {
        grouped[normalizedSign] = [];
      }
      
      // Build planet data with abbreviation - match D1-D20 format (2 chars, normal case)
      grouped[normalizedSign].push({
        name,
        abbr: name.substring(0, 2), // Sun -> Su, Moon -> Mo (match D1-D20)
        sign: planetSign,
        sign_sanskrit: planet.sign_sanskrit,
        degree: planet.degree, // Will be hidden for sign charts
      });
    });
    
    return grouped;
  }, [planets, ascendantSign, ascendant]);
  
  // Normalize ascendant sign (for highlighting the sign box)
  const normalizedAscendantSign = normalizeSignName(ascendantSign.toLowerCase());
  
  // Map signs to house polygon positions (sign_index + 1 = house number)
  // Sign 0 (Aries) → House 1, Sign 1 (Taurus) → House 2, etc.
  const signNames = ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo',
                     'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces'];
  
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

        {/* Sign Polygons - STATIC POSITIONS (NO ROTATION) */}
        {/* Each sign occupies its natural house polygon position (sign_index + 1) */}
        {signNames.map((signName, index) => {
          const houseNum = index + 1; // sign_index + 1 = house polygon position
          const points = northPolygonPoints[houseNum];
          if (!points) {
            return null;
          }
          
          const normalizedSign = normalizeSignName(signName);
          const isAscendantSign = normalizedSign === normalizedAscendantSign;
          const planetsInSign = planetsBySign[normalizedSign] || [];
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

              {/* Planets - Unlimited data-driven layout with polygon-aware boundaries */}
              {/* CRITICAL: Render exactly what API provides - no recalculation, no normalization */}
              {/* CRITICAL: Ascendant is rendered here as a planet (no separate label) */}
              {(() => {
                const totalPlanets = planetsInSign.length;
                if (totalPlanets === 0) return null;
                
                // CRITICAL: Polygon-aware SAFE PLACEMENT ZONE
                // Calculate polygon bounding box from points string
                const polygonBounds = (() => {
                  const pointArray = points.split(' ').map(p => {
                    const [x, y] = p.split(',').map(Number);
                    return { x, y };
                  });
                  const xs = pointArray.map(p => p.x);
                  const ys = pointArray.map(p => p.y);
                  return {
                    minX: Math.min(...xs),
                    maxX: Math.max(...xs),
                    minY: Math.min(...ys),
                    maxY: Math.max(...ys),
                  };
                })();
                
                // Safe placement zone with 14px padding
                // minY allows overlap with sign name if space is tight (boundary correctness > sign-name cleanliness)
                const padding = 14;
                const safeRect = {
                  minX: polygonBounds.minX + padding,
                  maxX: polygonBounds.maxX - padding,
                  minY: polygonBounds.minY + 18, // Allow overlap with sign name if needed
                  maxY: polygonBounds.maxY - padding,
                };
                
                // Unlimited, data-driven planet layout (NO LIMITS)
                const spacingX = 24;
                const spacingY = 24;
                const availableWidth = safeRect.maxX - safeRect.minX;
                // Adaptive grid based on available width
                const cols = Math.max(1, Math.floor(availableWidth / spacingX));
                
                // Calculate grid positions for ALL planets (unlimited, exactly as API provides)
                const planetPositions = planetsInSign.map((planet, planetIdx) => {
                  const row = Math.floor(planetIdx / cols);
                  const col = planetIdx % cols;
                  
                  // Fill left → right, wrap downward
                  let planetX = safeRect.minX + (col * spacingX);
                  let planetY = safeRect.minY + (row * spacingY);
                  
                  // HARD BOUNDARY ENFORCEMENT: Every planet position MUST be clamped to safeRect
                  // If even ONE planet escapes → this is a BUG
                  planetX = Math.min(Math.max(planetX, safeRect.minX), safeRect.maxX);
                  planetY = Math.min(Math.max(planetY, safeRect.minY), safeRect.maxY);
                  
                  // CRITICAL: Detect ASC (normalized to 'Asc' to match D1-D20)
                  // ASC behaves exactly like a planet - same layout rules, no special handling
                  const isAscendant = planet.name === 'Ascendant' || planet.abbr === 'Asc';
                  
                  return {
                    planet,
                    planetX,
                    planetY,
                    isAscendant,
                  };
                });
                
                // DATA TRUTH GUARANTEE: Render exactly what API provides
                // Same planet list, same signs, same varga output
                // No recalculation, no normalization, no correction attempts
                return planetPositions.map(({ planet, planetX, planetY, isAscendant }, idx) => (
                  <g key={`${signName}-${planet.name}-${idx}`}>
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
                    
                    {/* NO DEGREE TEXT FOR SIGN CHARTS (D24-D60) */}
                  </g>
                ));
              })()}
            </g>
          );
        })}

        {/* NO SEPARATE ASCENDANT LABEL - Ascendant is rendered as a planet inside its sign */}
      </svg>
    </div>
  );
}

