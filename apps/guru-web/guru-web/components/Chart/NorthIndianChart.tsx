/**
 * North Indian Chart - Pure Renderer (NO CALCULATIONS)
 * 
 * 🔒 ASTROLOGY LOCK
 * UI must NEVER calculate astrology.
 * API is the single source of truth.
 * 
 * CRITICAL RULES:
 * 1. House positions are STATIC (house 1 = center, house 2 = NE, etc.)
 * 2. Use API Houses[] array directly
 * 3. Use API Planets[].house directly
 * 4. NO rotation. NO remapping. NO calculation.
 */

'use client';

import React from 'react';
import { getNorthCoordinates, northPolygonPoints } from './coordinates';
import './NorthIndianChart.css';

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

interface NorthIndianChartProps {
  houses: HouseData[]; // REQUIRED - this component is ONLY for house charts
  ascendantSign?: string;
  ascendantHouse?: number;
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

export function NorthIndianChart({ 
  houses, 
  ascendantSign: propAscendantSign, 
  ascendantHouse
}: NorthIndianChartProps) {
  // GUARD RAIL: This component is ONLY for house-based charts (D1-D20)
  // Sign charts (D24-D60) must use NorthIndianSignChart component
  if (!houses || houses.length !== 12) {
    throw new Error(
      `FATAL: NorthIndianChart used incorrectly. ` +
      `Expected 12 houses, got ${houses?.length || 0}. ` +
      `Sign charts (D24-D60) must use NorthIndianSignChart component instead.`
    );
  }

  // RUNTIME ASSERTION: Ascendant house must be 1
  const ascendantHouseNumber = ascendantHouse !== undefined ? ascendantHouse : 1;
  if (ascendantHouseNumber !== 1) {
    throw new Error(`FATAL: Ascendant house must be 1, got ${ascendantHouseNumber}`);
  }
  
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
  
  const houseMap = new Map(normalizedHouses.map(h => [h.houseNumber, h]));

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

        {/* House Polygons - STATIC POSITIONS (NO ROTATION) */}
        {Object.entries(northPolygonPoints).map(([houseNum, points]) => {
          const house = houseMap.get(parseInt(houseNum));
          
          // RUNTIME ASSERTION: House must exist
          if (!house) {
            throw new Error(`FATAL: House ${houseNum} missing in houseMap`);
          }
          
          // RUNTIME ASSERTION: House must have sign
          if (!house.signName) {
            throw new Error(`FATAL: House ${houseNum} missing sign`);
          }
          
          // House 1 always contains Ascendant (static position)
          const isAscendant = parseInt(houseNum) === 1;

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
              
              {/* House Number */}
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

              {/* Rashi Name */}
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

        {/* Planets - Use API house numbers directly */}
        {/* CRITICAL: ASC is rendered here as a planet (no separate label) - ASC rendered using shared style for consistency */}
        {normalizedHouses.map((house) => {
          const polygonPoints = northPolygonPoints[house.houseNumber];
          const centroid = getPolygonCentroid(polygonPoints);
          
          return house.planets.map((planet, planetIdx) => {
            const originalCoords = getNorthCoordinates(house.houseNumber, planetIdx + 1);
            
            if (originalCoords.x === 0 && originalCoords.y === 0) {
              return null;
            }

            const safeCoords = getSafePlanetPosition(
              centroid,
              originalCoords,
              planetIdx,
              house.planets.length,
              polygonPoints
            );

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
                
                {degreeText && (
                  <text
                    x={safeCoords.x}
                    y={safeCoords.y + 15}
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
          });
        })}

        {/* NO SEPARATE ASCENDANT LABEL - Ascendant is rendered as a planet inside its sign */}
      </svg>
    </div>
  );
}
