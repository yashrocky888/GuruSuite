/**
 * North Indian Chart - Using Exact Python Coordinates
 * Modern glassmorphic styling
 * FIXED: Planets stay well inside polygon bounds, away from edges
 */

'use client';

import React from 'react';
import { HouseData, getSignNum, getSignName } from './utils';
import { getNorthCoordinates, northPolygonPoints } from './coordinates';
import './NorthIndianChart.css';

interface NorthIndianChartProps {
  houses: HouseData[];
  ascendantSign?: string; // Optional: Direct ascendant sign from API
  ascendantHouse?: number; // Optional: Ascendant house from API (for varga charts: house = sign)
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

/**
 * Get minimum distance from point to polygon edge
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
    
    // Distance from point to line segment
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
 */
function getSafePlanetPosition(
  centroid: { x: number; y: number },
  originalCoords: { x: number; y: number },
  planetIdx: number,
  totalPlanets: number,
  polygonPoints: string
): { x: number; y: number } {
  const MIN_DISTANCE_FROM_EDGE = 20; // Minimum distance from edge in pixels
  
  // Check if original position is far enough from edge
  const distanceFromEdge = getMinDistanceToEdge(originalCoords, polygonPoints);
  if (distanceFromEdge >= MIN_DISTANCE_FROM_EDGE) {
    return originalCoords;
  }

  // Position planets in a ring around the center, ensuring they're away from edges
  const angle = (planetIdx / totalPlanets) * 2 * Math.PI;
  let radius = 20; // Start with smaller radius
  let safeCoords = { x: 0, y: 0 };
  let attempts = 0;
  
  // Try different radii until we find a position far enough from edge
  while (attempts < 15) {
    const testX = centroid.x + Math.cos(angle) * radius;
    const testY = centroid.y + Math.sin(angle) * radius + 10; // Offset down to avoid house number
    
    const distToEdge = getMinDistanceToEdge({ x: testX, y: testY }, polygonPoints);
    if (distToEdge >= MIN_DISTANCE_FROM_EDGE) {
      safeCoords = { x: testX, y: testY };
      break;
    }
    radius -= 2;
    attempts++;
  }
  
  // If still not found, use a position very close to centroid
  if (safeCoords.x === 0 && safeCoords.y === 0) {
    safeCoords = {
      x: centroid.x + (Math.cos(angle) * 10),
      y: centroid.y + (Math.sin(angle) * 10) + 15,
    };
  }

  return safeCoords;
}

export function NorthIndianChart({ houses, ascendantSign: propAscendantSign, ascendantHouse }: NorthIndianChartProps) {
  // CRITICAL FIX: For varga charts, use API's ascendant_house directly (house = sign)
  // For D1 charts, use Whole Sign system (House 1 = Ascendant sign)
  
  // Detect if this is a varga chart (fixed sign grid: house = sign)
  const isVargaChart = houses.length > 0 && houses[0].signNumber === houses[0].houseNumber;
  
  let recalculatedHouses: HouseData[];
  let ascendantHouseNumber: number;
  
  if (isVargaChart && ascendantHouse !== undefined) {
    // CRITICAL: For varga charts - NO ROTATION, NO LAGNA-BASED SHIFTING
    // Use API's ascendant_house directly (house = sign, Whole Sign system)
    // Houses are already in fixed sign grid (House 1 = Mesha, House 2 = Vrishabha, etc.)
    // Lagna is DISPLAY-ONLY (label), NOT a rotation anchor
    // DO NOT rotate - use houses as-is from API
    recalculatedHouses = houses.map(house => ({ ...house })); // Copy to avoid mutations
    ascendantHouseNumber = ascendantHouse; // Use API's ascendant_house
    
    // RUNTIME ASSERTION: Verify no rotation occurred
    if (recalculatedHouses.length > 0 && recalculatedHouses[0].signNumber !== 1) {
      console.error('❌ VARGA VIOLATION: Houses were rotated - varga charts must use fixed sign grid');
    }
  } else {
    // For D1 charts: Recalculate house signs using Whole Sign system (House 1 = Ascendant sign)
    // Get ascendant sign from prop (API) or from houses (fallback)
    const ascendantPlanet = houses.find(h => 
      h.planets.some(p => p.name === 'Ascendant' || p.abbr === 'Asc')
    )?.planets.find(p => p.name === 'Ascendant' || p.abbr === 'Asc');
    
    // Priority: 1. propAscendantSign (from API), 2. ascendantPlanet.sign, 3. house 1 sign, 4. Mesha
    const ascendantSignName = propAscendantSign || ascendantPlanet?.sign || houses.find(h => h.houseNumber === 1)?.signName || 'Mesha';
    const ascendantSignNum = getSignNum(ascendantSignName) - 1; // Convert to 0-11
    
    // Recalculate house signs using Whole Sign system (House 1 = Ascendant sign)
    recalculatedHouses = houses.map((house, index) => {
      const houseNum = index + 1;
      // Calculate sign for this house: (ascendantSignNum + houseNum - 1) % 12
      const signNum = (ascendantSignNum + houseNum - 1) % 12;
      const signName = getSignName(signNum + 1); // getSignName uses 1-12
      
      return {
        ...house,
        signNumber: signNum + 1,
        signName: signName,
      };
    });
    
    // House 1 always contains ascendant in North Indian style for D1
    ascendantHouseNumber = 1;
  }
  
  const houseMap = new Map(recalculatedHouses.map(h => [h.houseNumber, h]));

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

        {/* House Polygons with Centered Text */}
        {Object.entries(northPolygonPoints).map(([houseNum, points]) => {
          const house = houseMap.get(parseInt(houseNum));
          // Check if this house contains Ascendant (use API house value, not hardcoded 1)
          const isAscendant = ascendantHouseNumber !== undefined && parseInt(houseNum) === ascendantHouseNumber;

          // Don't display houses with "Unknown" sign or no sign
          if (!house || house.signName === 'Unknown' || !house.signName) return null;

          const centroid = getPolygonCentroid(points);

          return (
            <g key={houseNum}>
              <polygon
                id={`house-${houseNum}`}
                points={points}
                fill="rgba(255, 255, 255, 0.08)"
                stroke={isAscendant ? '#d4af37' : 'rgba(212, 175, 55, 0.5)'}
                strokeWidth={isAscendant ? '2.5' : '1.5'}
                className={isAscendant ? 'ascendant-house' : ''}
                style={{
                  filter: isAscendant ? 'drop-shadow(0 0 8px rgba(212, 175, 55, 0.4))' : 'none',
                }}
              />
              
              {/* House Number - Top center */}
              <text
                x={centroid.x}
                y={centroid.y - 30}
                fill="#d4af37"
                textAnchor="middle"
                dominantBaseline="middle"
                className="house-number"
                style={{ 
                  fontSize: '16px', 
                  fontWeight: 700,
                  fontFamily: 'sans-serif',
                  textShadow: '0 1px 2px rgba(0,0,0,0.3)'
                }}
              >
                {house.houseNumber}
              </text>

              {/* Rashi Name - Center */}
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
                {house.signName}
              </text>
            </g>
          );
        })}

        {/* Planets - Positioned safely well inside polygon, away from edges */}
        {/* Use recalculated houses with correct signs for North Indian style */}
        {recalculatedHouses.map((house) => {
          const polygonPoints = northPolygonPoints[house.houseNumber];
          const centroid = getPolygonCentroid(polygonPoints);
          
          // Filter out Ascendant planet - it's shown by house 1 highlighting, not as a badge
          return house.planets.filter(planet => planet.name !== 'Ascendant' && planet.abbr !== 'Asc').map((planet, planetIdx) => {
            // Get original coordinates
            const originalCoords = getNorthCoordinates(house.houseNumber, planetIdx + 1);
            
            if (originalCoords.x === 0 && originalCoords.y === 0) {
              return null;
            }

            // Get safe position that stays well inside polygon, away from edges
            const filteredPlanets = house.planets.filter(p => p.name !== 'Ascendant' && p.abbr !== 'Asc');
            const safeCoords = getSafePlanetPosition(
              centroid,
              originalCoords,
              planetIdx,
              filteredPlanets.length,
              polygonPoints
            );

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
                  cx={safeCoords.x}
                  cy={safeCoords.y - 6}
                  r="11"
                  fill="rgba(59, 130, 246, 0.15)"
                  stroke="rgba(59, 130, 246, 0.3)"
                  strokeWidth="1"
                />
                
                {/* Planet abbreviation */}
                <text
                  x={safeCoords.x}
                  y={safeCoords.y}
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
                
                {/* Planet degree (below, smaller) */}
                {degreeText && (
                  <text
                    x={safeCoords.x}
                    y={safeCoords.y + 15}
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
          });
        })}
      </svg>
    </div>
  );
}
