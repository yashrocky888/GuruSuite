/**
 * South Indian Sign Chart - Pure Sign Renderer (NO HOUSES)
 * 
 * 🔒 ASTROLOGY LOCK
 * UI must NEVER calculate astrology.
 * API is the single source of truth.
 * 
 * CRITICAL RULES FOR PURE SIGN CHARTS (D24-D60):
 * 1. Signs are in FIXED positions (same as SouthIndianChart layout) - NEVER MOVE
 * 2. Planets are placed by SIGN ONLY (from API Planets[].sign)
 * 3. NO houses - these are pure sign charts
 * 4. NO house numbers, NO house labels, NO house calculations
 * 
 * SOUTH INDIAN CHART LAYOUT (FIXED):
 * Row 1:  capricorn | aquarius | pisces | aries
 * Row 2:  sagittarius |        |        | taurus
 * Row 3:  scorpio     |        |        | gemini
 * Row 4:  libra       | virgo   | leo    | cancer
 */

'use client';

// 🔥 VERIFICATION LOG - If this appears for D24, routing is correct
console.log("🔥 SouthIndianSignChart LOADED", Date.now());

import React, { useMemo } from 'react';
import { southRectPositions } from './coordinates';
import { normalizeSignName, SIGN_INDEX } from './houseUtils';
import { RASHI_NAMES } from './utils';
import './SouthIndianChart.css';

interface PlanetData {
  name: string;
  abbr: string;
  sign: string;
  sign_sanskrit?: string;
  degree?: number;
}

interface SouthIndianSignChartProps {
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

export default function SouthIndianSignChart({ ascendant, planets }: SouthIndianSignChartProps) {
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

        {/* Sign Rectangles - FIXED POSITIONS (SAME AS SOUTH INDIAN CHART) */}
        {/* NO houses, NO house numbers, NO house labels */}
        {(['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 
           'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces'] as const).map((fixedSignKey) => {
          const rect = southRectPositions[fixedSignKey];
          if (!rect) {
            return null;
          }
          
          const normalizedSign = normalizeSignName(fixedSignKey);
          const isAscendantSign = normalizedSign === normalizedAscendantSign;
          const planetsInSign = planetsBySign[normalizedSign] || [];
          
          const centerX = rect.x + rect.width / 2;
          const topY = rect.y + 18;
          const middleY = rect.y + rect.height / 2;
          // CRITICAL: Planets must be below sign name - ensure minimum gap
          // Sign name is at middleY, planets start below it with proper spacing
          const planetAreaStartY = Math.max(middleY + 25, rect.y + rect.height - 35);
          
          return (
            <g key={fixedSignKey}>
              {/* Sign Rectangle */}
              <rect
                id={fixedSignKey}
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
              
              {/* Sign Name - Use Sanskrit name matching D1-D20 */}
              <text
                x={centerX}
                y={middleY}
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
                  // Get sign index (0-11) from normalized sign key
                  const signIndex = SIGN_INDEX[normalizedSign];
                  if (signIndex !== undefined) {
                    // RASHI_NAMES uses 1-12, so add 1
                    return RASHI_NAMES[signIndex + 1] || fixedSignKey.charAt(0).toUpperCase() + fixedSignKey.slice(1);
                  }
                  return fixedSignKey.charAt(0).toUpperCase() + fixedSignKey.slice(1);
                })()}
              </text>

              {/* Planets - Positioned at bottom - SAME layout as house charts */}
              {/* CRITICAL: Ascendant is rendered here as a planet (no separate label) */}
              {planetsInSign.map((planet, planetIdx) => {
                const totalPlanets = planetsInSign.length;
                
                // CRITICAL: Enforce strict boundaries - planets must stay inside sign box
                const padding = 15; // Padding from sign box edges
                const minX = rect.x + padding;
                const maxX = rect.x + rect.width - padding;
                const minY = middleY + 25; // Minimum 25px below sign name
                const maxY = rect.y + rect.height - padding; // Bottom padding
                
                // Calculate planet spacing and position
                const availableWidth = rect.width - (padding * 2);
                const planetsPerRow = Math.min(totalPlanets, Math.floor(availableWidth / 25)); // Max 4-5 planets per row
                const row = Math.floor(planetIdx / planetsPerRow);
                const col = planetIdx % planetsPerRow;
                
                // Horizontal spacing within available width
                const planetSpacing = planetsPerRow > 1 
                  ? (availableWidth - 20) / (planetsPerRow - 1) // Space between planets
                  : 0;
                const startX = minX + 10; // Start 10px from left edge
                const planetX = Math.min(Math.max(startX + (col * planetSpacing), minX), maxX); // Clamp to boundaries
                
                // Vertical stacking - ensure planets stay below sign name and within box
                const basePlanetY = Math.max(planetAreaStartY, minY);
                const rowSpacing = 20; // Vertical spacing between rows
                const planetY = Math.min(basePlanetY + (row * rowSpacing), maxY); // Clamp to boundaries

                // CRITICAL: D24-D60 are pure sign charts - NO DEGREES displayed
                // Do NOT render degree text for sign charts

                // CRITICAL: Detect ASC (now normalized to 'Asc' to match D1-D20)
                const isAscendant = planet.name === 'Ascendant' || planet.abbr === 'Asc';
                
                // ASC rendered exactly like a planet - same circle, color, font, size (no special styling)
                return (
                  <g key={`${fixedSignKey}-${planet.name}-${planetIdx}`}>
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

