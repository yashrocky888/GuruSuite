/**
 * Chart Container - Pure Renderer (NO CALCULATIONS)
 * 
 * 🔒 ASTROLOGY LOCK
 * UI must NEVER calculate astrology.
 * API is the single source of truth.
 * 
 * CRITICAL RULE: Renders directly from API structure.
 * NO normalization. NO transformation. NO calculations.
 * 
 * API Structure (CANONICAL):
 * {
 *   Ascendant: { sign, house: 1, sign_index, degree, degree_dms, arcminutes, arcseconds, ... },
 *   Houses: [{ house: 1, sign, sign_index, ... }, ...],
 *   Planets: { Sun: { sign, house, degree, degree_dms, arcminutes, arcseconds, ... }, ... }
 * }
 */

'use client';

// 🔥 VERIFICATION LOG - If this doesn't appear, wrong file is being used
console.log("🔥 NEW ChartContainer LOADED", Date.now(), "Version: 2.0.0-PURE-SIGN-FIX");

import React, { useState, useMemo } from 'react';
import SouthIndianChart from './SouthIndianChart';
import { NorthIndianChart } from './NorthIndianChart';
import { isHouseChart, isSignChart, HOUSE_CHARTS, SIGN_CHARTS } from './chartUtils';
import SouthIndianSignChart from './SouthIndianSignChart';
import NorthIndianSignChart from './NorthIndianSignChart';

interface ChartContainerProps {
  chartData: any; // Raw API data
  chartType?: 'rasi' | 'navamsa' | 'dasamsa';
  vargaName?: string; // Optional varga name for display (e.g., "D16 - Shodasamsa Chart")
  // d24ChartMethod prop REMOVED - D24 is locked to Method 1 (JHora verified)
}

type ChartStyle = 'north' | 'south';

interface DirectApiChart {
  chartType?: string; // Chart type (e.g., "D1", "D24", etc.)
  Ascendant: {
    sign: string;
    sign_sanskrit?: string;
    sign_index: number;
    house?: number; // Optional for pure sign charts
    degree?: number;
    degrees_in_sign?: number;
    degree_dms?: number;
    arcminutes?: number;
    arcseconds?: number;
  };
  Houses: Array<{
    house: number;
    sign: string;
    sign_sanskrit?: string;
    sign_index: number;
  }> | null; // null for pure sign charts (D24-D60)
  Planets: {
    [planetName: string]: {
      sign: string;
      sign_sanskrit?: string;
      sign_index: number;
      house?: number; // Optional for pure sign charts
      degree?: number;
      degrees_in_sign?: number;
      degree_dms?: number;
      arcminutes?: number;
      arcseconds?: number;
    };
  };
}

export const ChartContainer: React.FC<ChartContainerProps> = ({ 
  chartData, 
  chartType = 'rasi',
  vargaName 
}) => {
  const [chartStyle, setChartStyle] = useState<ChartStyle>('south');

  // Extract chart data directly from API - NO NORMALIZATION
  // 🔒 CHART-TYPE AGNOSTIC: All charts (D1, D9, D10, etc.) follow the same structure
  const apiChart = useMemo((): DirectApiChart | null => {
    if (!chartData) {
      return null;
    }

    // Handle multiple API response formats
    let chart: any = null;
    const chartType = (chartData as any).chartType || 'Unknown';
    
    // 🔒 CRITICAL: Log D24 extraction for debugging
    const isD24 = vargaName?.includes('D24') || chartType === 'D24';

    // Format 1: { D1: { Ascendant, Houses, Planets }, D2: {...}, D9: {...}, ... }
    // Check for any divisional chart key (D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60)
    const divisionalChartKeys = ['D1', 'D2', 'D3', 'D4', 'D7', 'D9', 'D10', 'D12', 'D16', 'D20', 'D24', 'D27', 'D30', 'D40', 'D45', 'D60'];
    for (const key of divisionalChartKeys) {
      if ((chartData as any)[key]) {
        chart = (chartData as any)[key];
        if (isD24 || key === 'D24') {
          console.log(`🔍 D24 EXTRACTION (Format 1):`, {
            key,
            ascendantSign: chart.Ascendant?.sign,
            ascendantSignIndex: chart.Ascendant?.sign_index,
            planets: chart.Planets ? Object.keys(chart.Planets) : [],
            houses: chart.Houses,
          });
    }
        console.log(`✅ Extracted chart from Format 1 (${key}):`, { chartType: chart.chartType || key, hasAscendant: !!chart.Ascendant, hasHouses: !!chart.Houses, hasPlanets: !!chart.Planets });
        break;
      }
    }
    
    // Format 2: { data: { kundli: { D1: {...}, D9: {...}, ... } } }
    if (!chart && (chartData as any).data?.kundli) {
      for (const key of divisionalChartKeys) {
        if ((chartData as any).data.kundli[key]) {
          chart = (chartData as any).data.kundli[key];
          if (isD24 || key === 'D24') {
            console.log(`🔍 D24 EXTRACTION (Format 2):`, {
              key,
              ascendantSign: chart.Ascendant?.sign,
              ascendantSignIndex: chart.Ascendant?.sign_index,
              planets: chart.Planets ? Object.keys(chart.Planets) : [],
              houses: chart.Houses,
            });
          }
          console.log(`✅ Extracted chart from Format 2 (${key}):`, { chartType: chart.chartType || key, hasAscendant: !!chart.Ascendant, hasHouses: !!chart.Houses, hasPlanets: !!chart.Planets });
          break;
        }
      }
      // If no divisional key found, try direct kundli object
      if (!chart && (chartData as any).data.kundli.Ascendant) {
        chart = (chartData as any).data.kundli;
        console.log(`✅ Extracted chart from Format 2 (direct kundli):`, { chartType: chart.chartType || 'D1', hasAscendant: !!chart.Ascendant, hasHouses: !!chart.Houses, hasPlanets: !!chart.Planets });
    }
    }
    
    // Format 3: Direct chart object { Ascendant, Houses, Planets, chartType }
    // This is the format used when divisional chart page extracts D9/D10 from main response
    // CRITICAL: D24-D60 are "pure sign charts" with Houses: null (astrologically correct)
    // D1-D20 must have Houses array, D24-D60 have Houses: null
    if (!chart && (chartData as any).Ascendant) {
      const houses = (chartData as any).Houses;
      const planets = (chartData as any).Planets;
      const chartTypeFromData = (chartData as any).chartType || '';
      
      // Determine if this is a pure sign chart using single source of truth
      const isSignChartType = isSignChart(chartTypeFromData);
      
      // For pure sign charts: Houses can be null (valid)
      // For other charts: Houses must be an array
      const hasValidHouses = isSignChartType 
        ? (houses === null || houses === undefined)  // null is valid for D24-D60
        : (Array.isArray(houses) && houses.length === 12);  // Must be 12-element array for D1-D20
      
      const hasValidPlanets = planets && typeof planets === 'object' && Object.keys(planets).length > 0;
      
      if (hasValidHouses && hasValidPlanets) {
      chart = chartData;
        if (process.env.NODE_ENV === 'development') {
          console.log(`✅ Extracted chart from Format 3 (direct):`, { 
            chartType: chart.chartType || 'Unknown', 
            hasAscendant: !!chart.Ascendant, 
            housesType: isSignChartType ? 'null (pure sign chart)' : `array[${houses.length}]`,
            planetsCount: Object.keys(planets).length
          });
        }
      } else {
        // Only warn in development, don't treat as error
        if (process.env.NODE_ENV === 'development') {
          console.warn(`⚠️ Format 3 validation:`, {
            chartType: chartTypeFromData || 'Unknown',
            isSignChartType,
            hasAscendant: !!(chartData as any).Ascendant,
            housesValue: houses,
            housesIsArray: Array.isArray(houses),
            housesLength: Array.isArray(houses) ? houses.length : 'N/A',
            hasPlanets: !!planets,
            planetsIsObject: planets && typeof planets === 'object',
            planetsKeys: planets && typeof planets === 'object' ? Object.keys(planets).length : 'N/A'
          });
        }
      }
    }
    
    // Format 4: { success: true, data: { kundli: { Ascendant, Houses, Planets } } }
    if (!chart && (chartData as any).data?.kundli?.Ascendant) {
      chart = (chartData as any).data.kundli;
      console.log(`✅ Extracted chart from Format 4:`, { chartType: chart.chartType || 'D1', hasAscendant: !!chart.Ascendant, hasHouses: !!chart.Houses, hasPlanets: !!chart.Planets });
    }

    if (!chart) {
      const receivedKeys = Object.keys(chartData || {});
      const hasAscendant = !!(chartData as any).Ascendant;
      const hasHouses = !!(chartData as any).Houses;
      const hasPlanets = !!(chartData as any).Planets;
      const chartTypeFromData = (chartData as any).chartType || chartType || 'Unknown';
      const isSignChartType = isSignChart(chartTypeFromData);
      
      // CRITICAL: Don't log as error if this is legitimate data absence
      // Pure sign charts or unsupported charts are valid states, not errors
      const isLegitimateAbsence = isSignChartType || 
        (chartTypeFromData && chartTypeFromData !== 'Unknown' && chartTypeFromData !== 'D1');
      
      if (isLegitimateAbsence) {
        // Informational log only - not an error
        if (process.env.NODE_ENV === 'development') {
          console.info(`ℹ️ Chart ${chartTypeFromData} not available or not computed:`, {
            chartType: chartTypeFromData,
            hasAscendant,
            hasHouses: hasHouses ? (Array.isArray((chartData as any).Houses) ? 'array' : typeof (chartData as any).Houses) : false,
            hasPlanets,
            reason: isSignChartType ? 'Pure sign chart (may not have house structure)' : 'Chart not computed or not supported'
          });
        }
        return null; // Return null gracefully - UI will show informational message
      }
      
      // Only log as error if this appears to be a real extraction failure
      // (e.g., D1-D20 missing required fields)
      if (process.env.NODE_ENV === 'development') {
        const errorDetails: Record<string, any> = {
          chartType: chartTypeFromData,
          receivedKeys: receivedKeys.length > 0 ? receivedKeys : 'EMPTY_OBJECT',
          hasAscendant,
          hasHouses,
          hasPlanets,
        };
        
        if (hasHouses) {
          errorDetails.housesType = Array.isArray((chartData as any).Houses) ? 'array' : typeof (chartData as any).Houses;
          if (Array.isArray((chartData as any).Houses)) {
            errorDetails.housesLength = (chartData as any).Houses.length;
          }
        }
        
        if (hasPlanets) {
          errorDetails.planetsType = typeof (chartData as any).Planets;
          if (typeof (chartData as any).Planets === 'object' && (chartData as any).Planets !== null) {
            errorDetails.planetsKeys = Object.keys((chartData as any).Planets);
          }
        }
        
        if (hasAscendant && (chartData as any).Ascendant) {
          errorDetails.ascendantKeys = Object.keys((chartData as any).Ascendant);
        }
        
        console.error('❌ Cannot extract chart from API response (extraction failure):', errorDetails);
      }
      return null;
    }

    // RUNTIME ASSERTION: Ascendant must exist and have sign
    // CRITICAL: Ascendant sign is REQUIRED - no fallbacks allowed
    if (!chart.Ascendant) {
      console.error('❌ Ascendant missing in API response');
      return null;
    }
    
    if (!chart.Ascendant.sign && !chart.Ascendant.sign_sanskrit) {
      console.error('❌ Ascendant sign missing in API response');
      return null;
    }

    // RUNTIME ASSERTION: Validate houses based on chart type
    // D24-D60 are "pure sign charts" with Houses: null (astrologically correct)
    // D1-D20 must have exactly 12 houses
    const chartTypeFromChart = chart.chartType || '';
    const isSignChartType = isSignChart(chartTypeFromChart);
    
    // For house-based charts: Validate Ascendant.house must be 1
    // For pure sign charts: NO house validation (sign-only)
    if (!isSignChartType && chart.Ascendant?.house !== undefined && chart.Ascendant.house !== 1) {
      throw new Error(`FATAL: Ascendant.house must be 1 for house-based charts, got ${chart.Ascendant.house}`);
    }

    if (isSignChartType) {
      // Pure sign charts: Houses should be null (valid state)
      if (chart.Houses !== null && chart.Houses !== undefined) {
        if (process.env.NODE_ENV === 'development') {
          console.warn(`⚠️ Pure sign chart ${chartTypeFromChart} has Houses (expected null):`, chart.Houses);
        }
        // Still allow it - might be API variation
      }
    } else {
      // D1-D20: Must have exactly 12 houses
    if (!chart.Houses || !Array.isArray(chart.Houses) || chart.Houses.length !== 12) {
        if (process.env.NODE_ENV === 'development') {
          console.error(`❌ Invalid house data for ${chartTypeFromChart || 'chart'}. Expected 12 houses, got ${chart.Houses?.length || 0}`);
        }
      return null; // Return null instead of throwing - UI will show "No chart data available"
    }
    }

    // RUNTIME ASSERTION: Validate planets
    // For pure sign charts (D24-D60): NO house validation (sign-only charts)
    // For D1-D20: Planets must have house
    if (chart.Planets && !isSignChartType) {
      // Only validate houses for house-based charts
      Object.entries(chart.Planets).forEach(([name, planet]: [string, any]) => {
        // D1-D20: Planets must have valid house
        if (planet.house === undefined || planet.house < 1 || planet.house > 12) {
          if (process.env.NODE_ENV === 'development') {
            console.warn(`⚠️ Planet ${name} in ${chartTypeFromChart} has invalid house: ${planet.house} - will be skipped`);
          }
        }
      });
    }
    // For D24-D60: NO house validation - planets are sign-only

    return chart as DirectApiChart;
  }, [chartData]);

  // Convert API structure to chart component format (PURE MAPPING - NO CALCULATIONS)
  // CRITICAL: This useMemo must be called BEFORE early return to follow Rules of Hooks
  const housesForChart = useMemo(() => {
    // If apiChart is null, return empty array
    if (!apiChart) {
      return [];
    }
    
    // 🔒 CRITICAL: HARD GUARD - If Houses is null, this is a pure sign chart
    // Bypass ALL house logic immediately
    if (apiChart.Houses === null || apiChart.Houses === undefined) {
      const chartTypeFromChart = apiChart.chartType || '';
      console.log(`🔒 PURE SIGN MODE ENABLED — bypassing house renderer for ${chartTypeFromChart}`);
      console.log(`   Houses: null (pure sign chart)`);
      console.log(`   Ascendant: ${apiChart.Ascendant?.sign_sanskrit || apiChart.Ascendant?.sign} (sign index: ${apiChart.Ascendant?.sign_index})`);
      return []; // Empty array - chart will show planets by sign only
    }
    
    // CRITICAL: D24-D60 are "pure sign charts" with Houses: null
    // These charts don't have house structure - they're sign-only charts
    const chartTypeFromChart = apiChart.chartType || '';
    const isSignChartType = isSignChart(chartTypeFromChart);
    
    if (isSignChartType) {
      // Pure sign charts: Return empty array - these charts don't have houses
      // They only show planets in signs, not in houses
      console.log(`🔒 PURE SIGN MODE ENABLED — bypassing house renderer for ${chartTypeFromChart}`);
      console.log(`   Chart type detected as pure sign chart (D24-D60)`);
      return []; // Empty array - chart will show planets by sign only
    }
    
    // D1-D20: Must have houses array
    if (!apiChart.Houses || !Array.isArray(apiChart.Houses)) {
      if (process.env.NODE_ENV === 'development') {
        console.error(`❌ Chart ${chartTypeFromChart} missing houses array`);
      }
      return [];
    }
    
    // 🔒 CRITICAL: Only build house→sign map for HOUSE-BASED charts
    // This code should NEVER execute for pure sign charts (D24-D60)
    // RUNTIME LOG: Verify API houses array
    if (process.env.NODE_ENV === 'development') {
      console.log("🏠 HOUSE-BASED CHART MODE — Building house structure");
    console.log("API HOUSES ARRAY:", apiChart.Houses.map(h => ({ house: h.house, sign: h.sign_sanskrit || h.sign })));
    console.log("API PLANETS WITH HOUSES:", Object.entries(apiChart.Planets).map(([name, planet]: [string, any]) => ({
      name,
      sign: planet.sign_sanskrit || planet.sign,
      house: planet.house,
      degree: planet.degree
    })));
    }
    
    // Build houses array directly from API Houses[]
    const houses = apiChart.Houses.map((apiHouse) => {
      // Find all planets in this house
      // Filter invalid planets (house must be 1-12)
      const planetsInHouse = Object.entries(apiChart.Planets)
        .filter(([name, planet]: [string, any]) => {
          const house = planet.house;
          const matches = house !== undefined && house >= 1 && house <= 12 && house === apiHouse.house;
          if (matches) {
            console.log(`✅ Planet ${name} (sign: ${planet.sign_sanskrit || planet.sign}, house: ${house}) → House ${apiHouse.house} (${apiHouse.sign_sanskrit || apiHouse.sign})`);
          }
          return matches;
        })
        .map(([name, planet]) => ({
          name,
          abbr: name.substring(0, 2),
          sign: planet.sign_sanskrit || planet.sign,
          // PURE API MAPPING - NO CALCULATIONS
          // Use degrees_in_sign ONLY if provided - NO fallback to degree
          degree: planet.degrees_in_sign ?? undefined,
          degree_dms: planet.degree_dms ?? undefined,
          degree_minutes: planet.arcminutes ?? undefined,
          degree_seconds: planet.arcseconds ?? undefined,
        }));

      // Add Ascendant if this is house 1
      if (apiHouse.house === 1) {
        planetsInHouse.push({
          name: 'Ascendant',
          abbr: 'Asc',
          sign: apiChart.Ascendant.sign_sanskrit || apiChart.Ascendant.sign,
          // PURE API MAPPING - NO CALCULATIONS
          // Use degrees_in_sign ONLY if provided - NO fallback to degree
          degree: apiChart.Ascendant.degrees_in_sign ?? undefined,
          degree_dms: apiChart.Ascendant.degree_dms ?? undefined,
          degree_minutes: apiChart.Ascendant.arcminutes ?? undefined,
          degree_seconds: apiChart.Ascendant.arcseconds ?? undefined,
        });
      }

      const houseData = {
        houseNumber: apiHouse.house,
        signNumber: apiHouse.sign_index + 1, // 1-12 (just for display, not calculation)
        signName: apiHouse.sign_sanskrit || apiHouse.sign,
        planets: planetsInHouse,
      };
      
      // RUNTIME LOG: Verify house data
      if (houseData.planets.length > 0) {
        console.log(`House ${houseData.houseNumber} (${houseData.signName}):`, 
          houseData.planets.map(p => `${p.name} (${p.sign})`).join(', '));
      }
      
      return houseData;
    });

    return houses;
  }, [apiChart]);

  // Early return AFTER all hooks are called (Rules of Hooks compliance)
  if (!apiChart) {
    // Normalize chart type for display (same logic as main render)
    let normalizedVargaForDisplay = '';
    if ((chartData as any)?.chartType && (chartData as any).chartType.length > 0) {
      normalizedVargaForDisplay = (chartData as any).chartType.toUpperCase();
    } else if (chartType === 'navamsa') {
      normalizedVargaForDisplay = 'D9';
    } else if (chartType === 'dasamsa') {
      normalizedVargaForDisplay = 'D10';
    } else {
      normalizedVargaForDisplay = 'D1'; // Default
    }
    
    const chartTypeDisplay = vargaName || normalizedVargaForDisplay || 'chart';
    const chartTypeFromData = normalizedVargaForDisplay;
    const isSignChartType = isSignChart(chartTypeFromData);
    
    // Determine if this is a legitimate data absence (pure sign chart or unsupported)
    const isLegitimateAbsence = isSignChartType || (chartTypeFromData && chartTypeFromData !== 'D1');
    
    return (
      <div className="glass rounded-xl p-10 text-center">
        <div className="space-y-4">
          {isLegitimateAbsence ? (
            <>
              <p className="text-lg font-semibold text-gray-700 dark:text-gray-300">
                Chart Not Available
              </p>
              <p className="text-gray-500 dark:text-gray-400">
                {isSignChartType 
                  ? `${chartTypeDisplay} is a pure sign chart that does not include house structure. This is astrologically correct.`
                  : `${chartTypeDisplay} is not available for the given birth details or is not supported by the current calculation engine.`
                }
              </p>
              <p className="text-sm text-gray-400 dark:text-gray-500">
                This is not an error - the chart may be intentionally omitted or not applicable.
              </p>
            </>
          ) : (
            <>
              <p className="text-lg font-semibold text-gray-700 dark:text-gray-300">
                Chart Data Unavailable
              </p>
              <p className="text-gray-500 dark:text-gray-400">
                Unable to extract {chartTypeDisplay} from API response.
              </p>
              <p className="text-sm text-gray-400 dark:text-gray-500">
                Please ensure birth details are submitted and try again.
              </p>
            </>
          )}
        </div>
      </div>
    );
  }

  // 🔒 CRITICAL: Detect pure sign chart FIRST (before any normalization)
  // If Houses is null, this is DEFINITELY a pure sign chart (D24-D60)
  const isPureSignChartByData = apiChart.Houses === null || apiChart.Houses === undefined;
  
  // CRITICAL: Normalize chart type - SINGLE DEFAULT for empty/undefined values
  // Map legacy chartType props to varga format, or use API chartType, or default to D1
  let normalizedVarga: string = '';
  
  // Step 1: Try to get chartType from API data first (most authoritative)
  if (apiChart.chartType && typeof apiChart.chartType === 'string' && apiChart.chartType.length > 0) {
    normalizedVarga = apiChart.chartType.toUpperCase();
  } 
  // Step 2: Map legacy chartType prop to varga format
  else if (chartType === 'navamsa') {
    normalizedVarga = 'D9';
  } else if (chartType === 'dasamsa') {
    normalizedVarga = 'D10';
  } else if (chartType === 'rasi' || !chartType) {
    // Default: rasi, undefined, null, or empty string → D1
    normalizedVarga = 'D1';
  } else {
    // Fallback: use chartType as-is if it's already in D format
    // chartType is 'rasi' | 'navamsa' | 'dasamsa' at this point, so default to D1
    normalizedVarga = 'D1';
  }
  
  // CRITICAL: Ensure normalizedVarga is never empty
  if (!normalizedVarga || normalizedVarga.length === 0) {
    normalizedVarga = 'D1'; // Final fallback
  }
  
  // 🔒 CRITICAL: If Houses is null, FORCE sign chart classification
  // This overrides any chartType detection - API data is authoritative
  if (isPureSignChartByData) {
    // If Houses is null but chartType is not a sign chart, log warning
    if (!isSignChart(normalizedVarga)) {
      console.warn(`⚠️ API returned Houses=null but chartType=${normalizedVarga} is not a sign chart. Forcing sign chart mode.`);
      // Force to D24 as default (most common pure sign chart)
      normalizedVarga = 'D24';
    }
    console.log(`🔒 PURE SIGN CHART DETECTED: Houses=null, forcing sign chart renderer for ${normalizedVarga}`);
  }
  
  // DEFENSIVE ASSERTION: D1 must NEVER be treated as sign chart
  if (normalizedVarga === 'D1' && !isHouseChart(normalizedVarga)) {
    console.error('FATAL: D1 chart incorrectly classified as non-house chart');
    throw new Error('FATAL: D1 must be a house chart');
  }
  
  // 🔒 CRITICAL: If Houses is null, FORCE sign chart mode (override classification)
  let isHouseBasedChart = isHouseChart(normalizedVarga);
  let isSignChartType = isSignChart(normalizedVarga);
  
  // HARD OVERRIDE: If API says Houses=null, this is a pure sign chart regardless of chartType
  if (isPureSignChartByData) {
    isHouseBasedChart = false;
    isSignChartType = true;
    console.log(`🔒 FORCED SIGN CHART MODE: Houses=null detected, overriding chart type classification`);
  }
  
  // DEFENSIVE ASSERTION: Chart must be either house chart or sign chart
  // Only trigger for non-empty, non-default values
  if (normalizedVarga !== 'D1' && !isHouseBasedChart && !isSignChartType) {
    console.error(`FATAL: Unknown chart type: ${normalizedVarga}`);
    throw new Error(`FATAL: Unable to determine chart type for ${normalizedVarga}. Must be house chart (D1-D20) or sign chart (D24-D60).`);
  }
  
  // DEFENSIVE ASSERTION: D24-D60 must NEVER be passed to house chart components
  if (isSignChartType && isHouseBasedChart) {
    console.error(`FATAL: Chart ${normalizedVarga} classified as both house and sign chart`);
    throw new Error(`FATAL: Chart ${normalizedVarga} cannot be both house and sign chart`);
  }
  
  // 🔒 CRITICAL: Final guard - if Houses is null, NEVER use house chart renderer
  if (isPureSignChartByData && isHouseBasedChart) {
    console.error(`FATAL: Houses=null but isHouseBasedChart=true. This should never happen.`);
    isHouseBasedChart = false;
    isSignChartType = true;
  }
  
  // Use normalizedVarga for all subsequent logic
  const chartTypeFromData = normalizedVarga;

  // CRITICAL: Ascendant sign must come ONLY from chart.Ascendant.sign
  // NO fallbacks. NO derivation from planets. NO defaults.
  const ascendantSign = apiChart.Ascendant.sign_sanskrit || apiChart.Ascendant.sign;
  const ascendantHouse = apiChart.Ascendant.house; // Only for house charts
  
  // RUNTIME ASSERTION: Ascendant sign must exist
  if (!ascendantSign) {
    throw new Error('FATAL: Ascendant sign is missing - cannot render chart');
  }

  // 🔒 CRITICAL: Final safety guards before rendering
  // SAFETY GUARD: Prevent house charts from being rendered without houses
  if (isHouseBasedChart && (!housesForChart || housesForChart.length !== 12)) {
    throw new Error(
      `FATAL: House-based chart ${chartTypeFromData} requires 12 houses, got ${housesForChart?.length || 0}`
    );
  }
  
  // SAFETY GUARD: Prevent sign charts from being passed to house chart components
  if (isSignChartType && housesForChart && housesForChart.length > 0) {
    console.warn(`WARNING: Sign chart ${chartTypeFromData} has houses data - ignoring houses`);
  }
  
  // 🔒 CRITICAL: Final guard - if Houses is null, MUST use sign chart renderer
  if (isPureSignChartByData && isHouseBasedChart) {
    console.error(`FATAL: Houses=null detected but routing to house chart renderer. Forcing sign chart renderer.`);
    isHouseBasedChart = false;
    isSignChartType = true;
  }

  return (
    <div className="glass rounded-xl p-6 border border-white/20">
      {/* Chart Orientation Toggle - Always visible for ALL charts (D1-D60) */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
            {vargaName || (chartType === 'navamsa' ? 'Navamsa Chart (D9)' : 
             chartType === 'dasamsa' ? 'Dasamsa Chart (D10)' : 
             'Kundli Chart (D1)')}
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {isSignChartType ? (
              <>Ascendant: {ascendantSign} • Pure Sign Chart</>
            ) : isHouseBasedChart && ascendantHouse !== undefined ? (
              <>Ascendant: {ascendantSign} (House {ascendantHouse})</>
            ) : (
              <>Ascendant: {ascendantSign}</>
            )}
          </p>
        </div>

        {/* Orientation Toggle - ALWAYS visible for ALL charts (D1-D60) */}
        <div className="flex items-center space-x-3">
          <span className={`text-sm font-medium ${chartStyle === 'south' ? 'text-amber-600' : 'text-gray-500'}`}>
            South
          </span>
          <button
            onClick={() => setChartStyle(chartStyle === 'north' ? 'south' : 'north')}
            className="p-2 rounded-lg glass border border-white/20 hover:border-amber-500/50 transition-smooth"
            aria-label="Toggle chart orientation"
          >
            <svg className="w-4 h-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
          </button>
          <span className={`text-sm font-medium ${chartStyle === 'north' ? 'text-amber-600' : 'text-gray-500'}`}>
            North
          </span>
        </div>
      </div>

      {/* Chart Display - STRICT SEPARATION: House charts and sign charts NEVER share renderers */}
      <div className="w-full flex justify-center items-center min-h-[500px]">
        {(() => {
          // 🔒 CRITICAL: Log routing decision for debugging
          console.log(`🔀 CHART ROUTING DECISION:`, {
            chartType: chartTypeFromData,
            isHouseBasedChart,
            isSignChartType,
            isPureSignChartByData,
            housesLength: housesForChart?.length || 0,
            chartStyle,
            apiHouses: apiChart.Houses === null ? 'null' : Array.isArray(apiChart.Houses) ? `array[${apiChart.Houses.length}]` : typeof apiChart.Houses,
          });
          
          if (isHouseBasedChart) {
            // House-based charts (D1-D20): Use house chart renderers
            console.log(`🏠 ROUTING TO HOUSE CHART RENDERER: ${chartStyle === 'north' ? 'NorthIndianChart' : 'SouthIndianChart'}`);
            return chartStyle === 'north' ? (
              <NorthIndianChart 
                houses={housesForChart}
                ascendantSign={ascendantSign}
                ascendantHouse={ascendantHouse}
              />
            ) : (
              <SouthIndianChart 
                houses={housesForChart}
              />
            );
          } else if (isSignChartType) {
            // Sign-based charts (D24-D60): Use sign chart renderers ONLY
            console.log(`🔒 ROUTING TO SIGN CHART RENDERER: ${chartStyle === 'north' ? 'NorthIndianSignChart' : 'SouthIndianSignChart'}`);
            return chartStyle === 'north' ? (
              <NorthIndianSignChart 
                chartType={chartTypeFromData}
                ascendant={{
                  sign: apiChart.Ascendant.sign,
                  sign_sanskrit: apiChart.Ascendant.sign_sanskrit,
                  sign_index: apiChart.Ascendant.sign_index,
                  degree: apiChart.Ascendant.degree,
                }}
                planets={apiChart.Planets}
              />
            ) : (
              <SouthIndianSignChart 
                ascendant={{
                  sign: apiChart.Ascendant.sign,
                  sign_sanskrit: apiChart.Ascendant.sign_sanskrit,
                  degree: apiChart.Ascendant.degree,
                }}
                planets={apiChart.Planets}
              />
            );
          } else {
            // Default to D1 (house mode) for unknown chart types
            console.warn(`⚠️ UNKNOWN CHART TYPE, DEFAULTING TO HOUSE CHART: ${chartTypeFromData}`);
            return chartStyle === 'north' ? (
          <NorthIndianChart 
            houses={housesForChart}
            ascendantSign={ascendantSign}
            ascendantHouse={ascendantHouse}
          />
        ) : (
              <SouthIndianChart 
                houses={housesForChart}
              />
            );
          }
        })()}
      </div>
    </div>
  );
};
