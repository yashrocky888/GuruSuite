/**
 * South Indian Chart - Using Exact Python Coordinates
 * Modern glassmorphic styling
 * FIXED: No overlapping - planets positioned at bottom, clean modern layout
 */

'use client';

import React from 'react';
import { HouseData } from './utils';
import { southRectPositions, SouthChart_AscendantPositionAries, SouthChart_offsets4mAries } from './coordinates';
import './SouthIndianChart.css';

interface SouthIndianChartProps {
  houses: HouseData[];
}

export default function SouthIndianChart({ houses }: SouthIndianChartProps) {
  const houseMap = new Map(houses.map(h => [h.houseNumber, h]));

  // Find the house containing Ascendant (from API, not hardcoded House 1)
  const ascendantHouse = houses.find(h => 
    h.planets.some(p => p.name === 'Ascendant' || p.abbr === 'Asc')
  );
  const ascendantHouseNumber = ascendantHouse?.houseNumber;
  
  // CRITICAL FIX: Get ascendant sign from the Ascendant PLANET, not the house cusp sign
  // In Placidus system, house cusp sign (Mithuna) can differ from planet sign (Vrishchika)
  const ascendantPlanet = ascendantHouse?.planets.find(p => p.name === 'Ascendant' || p.abbr === 'Asc');
  let ascendantSign = ascendantPlanet?.sign?.toLowerCase() || ascendantHouse?.signName.toLowerCase() || 'mesha';
  
  // Handle sign name variations (vrischika vs vrishchika)
  if (ascendantSign === 'vrishchika') {
    ascendantSign = 'vrischika'; // Use the key from coordinates
  }

  // Calculate ascendant position for yellow "Asc" label
  const ascOffset = SouthChart_offsets4mAries[ascendantSign] || SouthChart_offsets4mAries[ascendantSign.replace('h', '')] || { x: 0, y: 0 };
  const ascX = SouthChart_AscendantPositionAries.x + ascOffset.x;
  const ascY = SouthChart_AscendantPositionAries.y + ascOffset.y;

  // Sign to house mapping (signs are fixed, houses rotate)
  const signToHouse: Record<string, HouseData> = {};
  houses.forEach(house => {
    let signKey = house.signName.toLowerCase();
    // Handle sign name variations
    if (signKey === 'vrishchika') {
      signKey = 'vrischika'; // Use the key from coordinates
    }
    signToHouse[signKey] = house;
    // Also map with original name for lookup
    signToHouse[house.signName.toLowerCase()] = house;
  });

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

        {/* Sign Rectangles with House Numbers and Rashi Names */}
        {Object.entries(southRectPositions).map(([signKey, rect]) => {
          const house = signToHouse[signKey];
          // Check if this house contains Ascendant (use API house value, not hardcoded 1)
          const isAscendant = ascendantHouseNumber !== undefined && house?.houseNumber === ascendantHouseNumber;

          // Don't display houses with "Unknown" sign or missing house
          if (!house || house.signName === 'Unknown' || !house.signName) return null;

          const centerX = rect.x + rect.width / 2;
          const topY = rect.y + 18; // Top for house number
          const middleY = rect.y + rect.height / 2; // Middle for rashi name
          const planetAreaStartY = rect.y + rect.height - 35; // Bottom area for planets

          return (
            <g key={signKey}>
              <rect
                id={signKey}
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

              {/* Planets - Positioned at bottom, horizontally distributed */}
              {/* Filter out Ascendant planet - it will be shown as yellow "Asc" label, not blue badge */}
              {house.planets.filter(planet => planet.name !== 'Ascendant' && planet.abbr !== 'Asc').map((planet, planetIdx) => {
                const filteredPlanets = house.planets.filter(p => p.name !== 'Ascendant' && p.abbr !== 'Asc');
                const totalPlanets = filteredPlanets.length;
                const planetSpacing = Math.min(rect.width / (totalPlanets + 1), 30);
                const startX = rect.x + planetSpacing;
                const planetX = startX + (planetIdx * planetSpacing);
                const planetY = planetAreaStartY - (planetIdx % 2) * 18; // Alternate rows if many planets

                // Format degree - use exact DMS from API (degree_dms, arcminutes, arcseconds)
                const degreeText = planet.degree_dms !== undefined && planet.degree_dms !== null
                  ? (planet.degree_minutes !== undefined && planet.degree_minutes !== null
                      ? (planet.degree_seconds !== undefined && planet.degree_seconds !== null && planet.degree_seconds > 0
                          ? `${planet.degree_dms}° ${planet.degree_minutes}' ${planet.degree_seconds}"` // e.g., "1° 25' 30""
                          : `${planet.degree_dms}° ${planet.degree_minutes}'`) // e.g., "1° 25'"
                      : `${planet.degree_dms}°`) // e.g., "1°"
                  : (planet.degree !== undefined && planet.degree !== null
                      ? `${planet.degree.toFixed(2)}°` // Fallback: use float degree
                      : '');

                return (
                  <g key={`${house.houseNumber}-${planet.name}-${planetIdx}`}>
                    {/* Planet badge background */}
                    <circle
                      cx={planetX}
                      cy={planetY - 6}
                      r="11"
                      fill="rgba(59, 130, 246, 0.15)"
                      stroke="rgba(59, 130, 246, 0.3)"
                      strokeWidth="1"
                    />
                    
                    {/* Planet abbreviation */}
                    <text
                      x={planetX}
                      y={planetY}
                      fill="#3b82f6"
                      textAnchor="middle"
                      dominantBaseline="middle"
                      className="planet-text"
                      style={{ 
                        fontSize: '12px',
                        fontWeight: 700,
                        fontFamily: 'sans-serif'
                      }}
                    >
                      {planet.abbr}
                    </text>
                    
                    {/* Planet degree (below) */}
                    {degreeText && (
                      <text
                        x={planetX}
                        y={planetY + 15}
                        fill="#60a5fa"
                        textAnchor="middle"
                        dominantBaseline="middle"
                        className="planet-degree"
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

        {/* Ascendant Label - Yellow "Asc" text (correct, keep this) */}
        {ascendantHouseNumber && (
          <text
            id={`${ascendantSign}Asc`}
            x={ascX}
            y={ascY}
            fill="#d4af37"
            className="ascendant-label"
            style={{ fontWeight: 600, fontSize: '14px' }}
          >
            Asc
          </text>
        )}
      </svg>
    </div>
  );
}
