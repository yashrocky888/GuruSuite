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
import { PlanetDetailsTable } from './PlanetDetailsTable';
import { GrahaDrishtiTable } from './GrahaDrishtiTable';
import { PlanetStrengthTable } from './PlanetStrengthTable';

interface ChartContainerProps {
  chartData: any; // Raw API data
  chartType?: string; // Chart type (e.g., "D1", "D4", "D9", "D10", "rasi", "navamsa", "dasamsa", etc.)
  vargaName?: string; // Optional varga name for display (e.g., "D16 - Shodasamsa Chart")
  planetFunctionalStrength?: Record<string, any>; // Planet functional strength data (admin-only, D1-only)
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
  Aspects?: Array<{
    from: string;
    aspect: string;
    to: string;
  }>; // Graha Drishti (Planetary Aspects) - optional, computed per varga
}

export const ChartContainer: React.FC<ChartContainerProps> = ({ 
  chartData, 
  chartType = 'rasi',
  vargaName,
  planetFunctionalStrength
}) => {
  const [chartStyle, setChartStyle] = useState<ChartStyle>('south');
  // 🔒 ADMIN VIEW FLAG: Temporary hard-coded gate for internal tools
  // This flag is the ONLY gate controlling the Planet Functional Strength table.
  // Future: Replace with real auth/role-based logic.
  const IS_ADMIN_VIEW = true;
  // 🔒 CONTEXT FLAG: True when rendering from /kundli/divisional
  // D1 HARD LOCK must apply ONLY to main Rāśi D1 view, NOT divisional context.
  const isDivisionalContext =
    typeof window !== 'undefined' && window.location.pathname.startsWith('/kundli/divisional');
  
  // ═══════════════════════════════════════════════════════════════════════════
  // 🔒 D1 HARD LOCK — NO NORMALIZATION, NO FALLBACK, NO TRANSFORMATION
  // ═══════════════════════════════════════════════════════════════════════════
  // D1 (Rāśi) is SACRED. It must NEVER pass through generalized chart logic.
  // D1 is a DIRECT PIPE: API → Renderer
  // ═══════════════════════════════════════════════════════════════════════════
  if (chartType === 'D1' && !isDivisionalContext) {
    if (!chartData?.Ascendant || !chartData?.Planets || !chartData?.Houses) {
      console.error('❌ D1 HARD LOCK VIOLATION: Missing Ascendant / Planets / Houses');
      return null;
    }

    const apiChart = chartData; // DIRECT PIPE — DO NOT TOUCH

    // 🧪 D1 DEBUG — RAW API DATA VERIFICATION
    console.log("🧪 D1 DEBUG — RAW API ASCENDANT", apiChart.Ascendant);
    console.log("🧪 D1 DEBUG — HOUSE 1", apiChart.Houses.find((h: any) => h.house === 1));
    console.log("🧪 D1 DEBUG — ALL HOUSES", apiChart.Houses.map((h: any) => ({
      house: h.house,
      sign: h.sign_sanskrit || h.sign,
      sign_index: h.sign_index
    })));
    console.log("🧪 D1 DEBUG — PLANETS", Object.fromEntries(
      Object.entries(apiChart.Planets).map(([k, p]: [string, any]) => [
        k,
        { sign: p.sign_sanskrit || p.sign, house: p.house, sign_index: p.sign_index }
      ])
    ));

    const housesForChart = apiChart.Houses.map((house: any) => {
      const planetsInHouse = Object.entries(apiChart.Planets)
        .filter(([_, p]: [string, any]) => (p as any).house === house.house)
        .map(([name, planet]: [string, any]) => ({
          name,
          abbr: name.substring(0, 2),
          sign: planet.sign_sanskrit || planet.sign,
          degree: planet.degrees_in_sign,
          degree_dms: planet.degree_dms,
          degree_minutes: planet.arcminutes,
          degree_seconds: planet.arcseconds,
        }));

      if (house.house === 1) {
        planetsInHouse.push({
          name: 'Ascendant',
          abbr: 'ASC',
          sign: apiChart.Ascendant.sign_sanskrit || apiChart.Ascendant.sign,
          degree: apiChart.Ascendant.degrees_in_sign,
          degree_dms: apiChart.Ascendant.degree_dms,
          degree_minutes: apiChart.Ascendant.arcminutes,
          degree_seconds: apiChart.Ascendant.arcseconds,
        });
      }

      return {
        houseNumber: house.house,
        // 🔒 REQUIRED BY CHART RENDERERS (SouthIndianChart / NorthIndianChart)
        // Both expect signName and use signName.toLowerCase() internally.
        // D1 HARD LOCK must provide the same shape as other chart paths.
        signName: house.sign_sanskrit || house.sign,
        sign: house.sign_sanskrit || house.sign,
        planets: planetsInHouse,
      };
    });

    // 🧪 D1 FUNCTIONAL STRENGTH PAYLOAD DEBUG (TEMP - VERIFY API DATA)
    console.log('🧪 D1 FUNCTIONAL STRENGTH PAYLOAD', {
      hasPlanetFunctionalStrength: !!planetFunctionalStrength,
      planetFunctionalStrengthType: typeof planetFunctionalStrength,
      planetFunctionalStrengthKeys: planetFunctionalStrength ? Object.keys(planetFunctionalStrength) : [],
      planetFunctionalStrengthSample: planetFunctionalStrength ? Object.entries(planetFunctionalStrength).slice(0, 2) : [],
      apiPlanetKeys: Object.keys(apiChart.Planets || {}),
      // 🔒 KEY MATCHING VERIFICATION: Compare API planet keys with functional strength keys
      keyMatchStatus: planetFunctionalStrength && apiChart.Planets
        ? {
            apiPlanets: Object.keys(apiChart.Planets),
            strengthPlanets: Object.keys(planetFunctionalStrength),
            missingInStrength: Object.keys(apiChart.Planets).filter(p => !planetFunctionalStrength[p]),
            extraInStrength: Object.keys(planetFunctionalStrength).filter(p => !apiChart.Planets[p]),
          }
        : null,
    });

    return (
      <div className="glass rounded-xl p-6 border border-white/20">
        <SouthIndianChart houses={housesForChart} />

        <PlanetDetailsTable
          chartType="D1"
          ascendant={apiChart.Ascendant}
          planets={apiChart.Planets}
          planetFunctionalStrength={planetFunctionalStrength}
        />

        {/* Admin-only, render-only — MUST NOT AFFECT D1 */}
        {IS_ADMIN_VIEW && planetFunctionalStrength && Object.keys(planetFunctionalStrength).length > 0 && (
          <PlanetStrengthTable strengthData={planetFunctionalStrength} />
        )}

        <GrahaDrishtiTable aspects={apiChart.Aspects || []} />
      </div>
    );
  }
  
  // 🔒 TRANSIT CHART FIX: Treat TRANSIT exactly like D1 for rendering purposes
  // Transit charts are standalone D1-equivalent charts (not vargas)
  // Map TRANSIT to D1 before any chart-type branching
  // NOTE: D1 itself is already handled above and will never reach this code
  const effectiveChartType = chartType === 'TRANSIT' ? 'D1' : chartType;

  // Extract chart data directly from API - NO NORMALIZATION
  // 🔒 CHART-TYPE AGNOSTIC: All charts (D9, D10, etc.) follow the same structure
  // NOTE: D1 is handled above and will never reach this code
  const apiChart = useMemo((): DirectApiChart | null => {
    if (!chartData) {
      return null;
    }
    
    // 🔒 CRITICAL FIX: Extract chart from chartData based on chartType
    // chartData structure: { D1: {...}, D2: {...}, D4: {...}, etc. }
    // For D4: chartData.D4
    // For all others: chartData[chartType] (e.g., chartData.D1, chartData.D9)
    // 🔒 TRANSIT FIX: Use effectiveChartType (TRANSIT → D1) for extraction
    const chartTypeFromProp = effectiveChartType || '';
    const isD4 = chartTypeFromProp === 'D4';
    
    // 🔒 STEP 1: Extract chart from chartData based on chartType
    let chartRoot: any = null;
    
    if (isD4) {
      // D4: Extract from chartData.D4
      const d4Data = (chartData as any)?.D4;
      if (!d4Data) {
        console.error("=".repeat(80));
        console.error("❌ D4 FATAL: chartData.D4 is missing. D4 MUST fail loudly.");
        console.error("D4 Rules:");
        console.error("  - NO fallback to D1");
        console.error("  - NO fallback to generic D-chart handler");
        console.error("  - NO fallback to chartData.houses");
        console.error("  - NO fallback to derived sign sequences");
        console.error("If D4 missing → LOG ERROR → RETURN NULL");
        console.error("=".repeat(80));
        return null; // Fail loudly for D4 - NO fallbacks
      }
      
      // Deep clone D4 data to prevent contamination
      chartRoot = structuredClone(d4Data);
      
      // 🔒 STEP 2: HARD RESET PLANET SOURCE - Verify D4 data integrity
      console.log("=".repeat(80));
      console.log("🔒 STEP 2: HARD RESET PLANET SOURCE - D4 DATA VERIFICATION");
      console.log("=".repeat(80));
      console.log("chartRoot.Ascendant:", chartRoot.Ascendant);
      console.log("chartRoot.Planets:", Object.keys(chartRoot.Planets || {}));
      console.log("chartRoot.Houses:", Array.isArray(chartRoot.Houses) ? chartRoot.Houses.length : chartRoot.Houses);
      console.log("");
      console.log("🚫 DO NOT:");
      console.log("  - Infer house from sign");
      console.log("  - Infer sign from house");
      console.log("  - Use sign_index");
      console.log("  - Use house arrays to relocate planets");
      console.log("");
      
      // Assert: Every planet must have sign and house
      Object.entries(chartRoot.Planets || {}).forEach(([name, planet]: [string, any]) => {
        if (!planet.sign && !planet.sign_sanskrit) {
          console.error(`❌ D4 DATA MISMATCH: Planet ${name} missing sign`);
        }
        if (planet.house === undefined || planet.house < 1 || planet.house > 12) {
          console.error(`❌ D4 DATA MISMATCH: Planet ${name} has invalid house: ${planet.house}`);
        }
        console.log(`  ${name}: sign=${planet.sign_sanskrit || planet.sign}, house=${planet.house}`);
      });
      
      // Assert: House 1 sign MUST equal Ascendant.sign (verify, do NOT recalc)
      const house1 = chartRoot.Houses?.find((h: any) => h.house === 1);
      const ascSign = chartRoot.Ascendant?.sign_sanskrit || chartRoot.Ascendant?.sign;
      const house1Sign = house1?.sign_sanskrit || house1?.sign;
      if (house1 && ascSign && house1Sign !== ascSign) {
        console.error(`❌ D4 DATA MISMATCH: House 1 sign (${house1Sign}) !== Ascendant sign (${ascSign})`);
      } else if (house1 && ascSign) {
        console.log(`✅ D4 VERIFIED: House 1 sign (${house1Sign}) === Ascendant sign (${ascSign})`);
      }
      
      console.log("=".repeat(80));
    } else {
      // All other charts: Extract from chartData[chartType]
      // chartData structure: { D1: {...}, D2: {...}, D9: {...}, etc. }
      // OR chartData is already the chart object (when passed from kundli page)
      
      // 🔒 D1 FIX: Check if chartData is already the chart object (has Ascendant)
      // This happens when kundli page extracts D1 and passes it directly
      if ((chartData as any)?.Ascendant && (chartData as any)?.Planets) {
        // chartData is already the chart object - use it directly
        chartRoot = chartData;
      } else {
        // chartData is the full response object - extract by chartType
        chartRoot = (chartData as any)?.[chartTypeFromProp];
        
        if (!chartRoot) {
          console.warn(`⚠️ Chart ${chartTypeFromProp} not found in chartData. Available keys:`, Object.keys(chartData || {}));
          return null;
        }
      }
    }
    
    // If chartRoot missing, fail silently (except D4 which fails loudly above)
    if (!chartRoot) {
      return null; // UI will show "No chart data available"
    }
    
    // Validate chartRoot has required structure
    if (!chartRoot.Ascendant) {
      return null;
    }
    
    // 🔍 QUICK VERIFICATION: Log chartRoot.Houses structure
    if (chartRoot.Houses && Array.isArray(chartRoot.Houses) && chartRoot.Houses.length > 0) {
      console.log("=".repeat(80));
      console.log("🔍 VERIFICATION: chartRoot.Houses structure");
      console.log("=".repeat(80));
      console.log("Sample house object:", chartRoot.Houses[0]);
      console.log("Field names in house object:", Object.keys(chartRoot.Houses[0]));
      console.log("House field check:");
      console.log("  - house:", chartRoot.Houses[0].house);
      console.log("  - houseNumber:", chartRoot.Houses[0].houseNumber);
      console.log("  - house_index:", chartRoot.Houses[0].house_index);
      console.log("Full Houses array:", chartRoot.Houses.map((h: any) => ({
        house: h.house,
        houseNumber: h.houseNumber,
        house_index: h.house_index,
        sign: h.sign || h.sign_sanskrit,
        planets: "N/A (not in house object)"
      })));
      console.log("=".repeat(80));
    }
    
    // chartRoot is now the chart object - use it directly
    const chart = chartRoot;

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
      console.error(`❌ Ascendant.house must be 1 for house-based charts, got ${chart.Ascendant.house}. Returning null.`);
      return null; // Fail silently - UI will show "No chart data available"
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
  }, [chartData, chartType]);

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
    
    // 🔍 D4 RAW API DATA DIAGNOSTICS (BEFORE ANY TRANSFORMATIONS)
    // Log raw API data to determine if sign_index is absolute or Lagna-relative
    if (chartTypeFromChart === 'D4') {
      console.log("=".repeat(80));
      console.log("🔍 D4 RAW API DATA DIAGNOSTICS (BEFORE UI TRANSFORMATIONS)");
      console.log("=".repeat(80));
      console.log("Chart Type:", chartTypeFromChart);
      console.log("");
      console.log("ASCENDANT (RAW API DATA):");
      console.log("  sign:", apiChart.Ascendant?.sign_sanskrit || apiChart.Ascendant?.sign);
      console.log("  sign_index:", apiChart.Ascendant?.sign_index);
      console.log("");
      console.log("HOUSES ARRAY (RAW API DATA - NO TRANSFORMATIONS):");
      apiChart.Houses.forEach((house: any) => {
        console.log(`  House ${house.house}:`);
        console.log("    sign:", house.sign_sanskrit || house.sign);
        console.log("    sign_index:", house.sign_index);
      });
      console.log("");
      console.log("ANALYSIS:");
      console.log("  - If House 1 sign_index == Ascendant sign_index → Lagna-relative");
      console.log("  - If House 1 sign_index != Ascendant sign_index → Absolute zodiac");
      const house1SignIndex = apiChart.Houses.find((h: any) => h.house === 1)?.sign_index;
      const ascendantSignIndex = apiChart.Ascendant?.sign_index;
      if (house1SignIndex !== undefined && ascendantSignIndex !== undefined) {
        if (house1SignIndex === ascendantSignIndex) {
          console.log("  ✅ CONFIRMED: Houses are LAGNA-RELATIVE (House 1 sign_index == Ascendant sign_index)");
        } else {
          console.log("  ⚠️  Houses appear to be ABSOLUTE ZODIAC (House 1 sign_index != Ascendant sign_index)");
          console.log(`     House 1 sign_index: ${house1SignIndex}, Ascendant sign_index: ${ascendantSignIndex}`);
        }
      }
      console.log("=".repeat(80));
    }
    
    // 🔍 MANDATORY: Log which object is used to build houses
    console.log("=".repeat(80));
    console.log("🔍 HOUSE CONSTRUCTION DATA SOURCE");
    console.log("=".repeat(80));
    console.log("apiChart.Houses source:", apiChart.Houses);
    console.log("apiChart.Houses type:", Array.isArray(apiChart.Houses) ? "Array" : typeof apiChart.Houses);
    console.log("apiChart.Houses length:", Array.isArray(apiChart.Houses) ? apiChart.Houses.length : "N/A");
    if (Array.isArray(apiChart.Houses) && apiChart.Houses.length > 0) {
      console.log("First house sample:", apiChart.Houses[0]);
      console.log("All houses sign_index values:", apiChart.Houses.map((h: any) => ({ house: h.house, sign_index: h.sign_index, sign: h.sign })));
    }
    console.log("=".repeat(80));
    
    // Build houses array directly from API Houses[]
    // Reuse chartTypeFromChart from earlier scope (already declared)
    const isD4 = (apiChart.chartType || '') === 'D4';
    
    // 🔒 STEP 5: FINAL VERIFICATION LOG (MANDATORY) - D4 TRUTH TABLE
    // Compare this line-by-line with reference (JHora / Prokerala)
    // If mismatch → BUG EXISTS
    if (isD4) {
      console.log("=".repeat(80));
      console.log("🔒 FINAL D4 TRUTH TABLE");
      console.log("=".repeat(80));
      console.log("Planet | API Sign | API House");
      console.log("-".repeat(80));
      Object.entries(apiChart.Planets).forEach(([name, planet]: [string, any]) => {
        const planetSign = planet.sign_sanskrit || planet.sign;
        const planetHouse = planet.house;
        console.log(`${name.padEnd(12)} | ${(planetSign || 'N/A').padEnd(15)} | ${planetHouse !== undefined ? planetHouse : 'N/A'}`);
      });
      console.log("-".repeat(80));
      console.log("D4 ASCENDANT:");
      console.log(`  Sign: ${apiChart.Ascendant?.sign_sanskrit || apiChart.Ascendant?.sign}`);
      console.log(`  House: ${apiChart.Ascendant?.house !== undefined ? apiChart.Ascendant.house : 'N/A'}`);
      console.log("");
      console.log("🔒 VERIFICATION: Compare above table line-by-line with reference D4");
      console.log("If ANY mismatch → BUG EXISTS (data contamination or wrong source)");
      console.log("=".repeat(80));
    }
    
    // 🔒 CRITICAL D4 FIX: D4 MUST NOT pass through house-based pre-grouping
    // For D4: Build houses array for LABELS ONLY, but planets come DIRECTLY from API
    // For other charts: Use standard house-based grouping
    const houses = isD4 
      ? (() => {
          // 🔒 STEP 2: HARD RESET PLANET SOURCE - D4 uses DIRECT planet data
          // Build houses array for labels only (NOT for planet placement)
          // Planets will be grouped by sign in SouthIndianChart, NOT by house
          console.log("=".repeat(80));
          console.log("🔒 STEP 2 — HARD RESET PLANET SOURCE (D4 DIRECT)");
          console.log("=".repeat(80));
          console.log("D4 Rule: Planets come DIRECTLY from apiChart.Planets");
          console.log("Houses array is for LABELS ONLY, NOT for planet placement");
          console.log("");
          console.log("D4 PLANETS (Name | sign | house):");
          Object.entries(apiChart.Planets).forEach(([name, planet]: [string, any]) => {
            const planetSign = planet.sign_sanskrit || planet.sign;
            const planetHouse = planet.house;
            console.log(`  ${name.padEnd(12)} | ${(planetSign || 'N/A').padEnd(15)} | ${planetHouse !== undefined ? planetHouse : 'N/A'}`);
          });
          console.log("=".repeat(80));
          
          // Build houses array with labels only (planets will be grouped by sign, not house)
          return apiChart.Houses.map((apiHouse) => {
            // For D4, we still need to match planets to houses for the data structure
            // BUT SouthIndianChart will ignore house grouping and group by sign instead
            const planetsInHouse = Object.entries(apiChart.Planets)
              .filter(([name, planet]: [string, any]) => {
                const house = planet.house;
                if (house === undefined || house < 1 || house > 12) {
                  console.error(`❌ D4 FATAL: Planet ${name} has invalid house: ${house} - MUST be 1-12`);
                  return false;
                }
                return house === apiHouse.house;
              })
              .map(([name, planet]) => {
                // 🔒 ABSOLUTE RULE: Use planet.sign EXACTLY as provided by API
                // DO NOT use house sign, DO NOT infer, DO NOT recompute
                const planetSign = planet.sign_sanskrit || planet.sign;
                
                if (!planetSign) {
                  console.error(`❌ D4 DATA MISMATCH: Planet ${name} missing sign`);
                }
                
                return {
                  name,
                  abbr: name.substring(0, 2),
                  sign: planetSign, // D4 planet.sign EXACTLY as provided by API
                  degree: planet.degrees_in_sign ?? undefined,
                  degree_dms: planet.degree_dms ?? undefined,
                  degree_minutes: planet.arcminutes ?? undefined,
                  degree_seconds: planet.arcseconds ?? undefined,
                };
              });

            // Add Ascendant if this is house 1
            if (apiHouse.house === 1) {
              const ascSign = apiChart.Ascendant?.sign_sanskrit || apiChart.Ascendant?.sign;
              if (ascSign) {
                planetsInHouse.push({
                  name: 'Ascendant',
                  abbr: 'ASC',
                  sign: ascSign, // D4 Ascendant.sign EXACTLY as provided by API
                  degree: apiChart.Ascendant.degrees_in_sign ?? undefined,
                  degree_dms: apiChart.Ascendant.degree_dms ?? undefined,
                  degree_minutes: apiChart.Ascendant.arcminutes ?? undefined,
                  degree_seconds: apiChart.Ascendant.arcseconds ?? undefined,
                });
              }
            }

            return {
              houseNumber: apiHouse.house,
              signNumber: (apiHouse.sign_index ?? 0) + 1,
              signName: apiHouse.sign_sanskrit || apiHouse.sign,
              sign: apiHouse.sign_sanskrit || apiHouse.sign,
              sign_sanskrit: apiHouse.sign_sanskrit,
              planets: planetsInHouse, // For D4, this is for structure only - SouthIndianChart groups by sign
            };
          });
        })()
      : (() => {
          // Standard house-based grouping for non-D4 charts
          return apiChart.Houses.map((apiHouse) => {
            const planetsInHouse = Object.entries(apiChart.Planets)
              .filter(([name, planet]: [string, any]) => {
                const house = planet.house;
                if (house === undefined || house < 1 || house > 12) {
                  return false;
                }
                return house === apiHouse.house;
              })
              .map(([name, planet]) => {
                return {
                  name,
                  abbr: name.substring(0, 2),
                  sign: planet.sign_sanskrit || planet.sign,
                  degree: planet.degrees_in_sign ?? undefined,
                  degree_dms: planet.degree_dms ?? undefined,
                  degree_minutes: planet.arcminutes ?? undefined,
                  degree_seconds: planet.arcseconds ?? undefined,
                };
              });

            // Add Ascendant if this is house 1
            if (apiHouse.house === 1) {
              const ascSign = apiChart.Ascendant?.sign_sanskrit || apiChart.Ascendant?.sign;
              if (ascSign) {
                planetsInHouse.push({
                  name: 'Ascendant',
                  abbr: 'ASC',
                  sign: ascSign,
                  // PURE API MAPPING - NO CALCULATIONS
                  // Use degrees_in_sign ONLY if provided - NO fallback to degree
                  degree: apiChart.Ascendant.degrees_in_sign ?? undefined,
                  degree_dms: apiChart.Ascendant.degree_dms ?? undefined,
                  degree_minutes: apiChart.Ascendant.arcminutes ?? undefined,
                  degree_seconds: apiChart.Ascendant.arcseconds ?? undefined,
                });
              }
            }

            return {
              houseNumber: apiHouse.house,
              signNumber: (apiHouse.sign_index ?? 0) + 1,
              signName: apiHouse.sign_sanskrit || apiHouse.sign,
              sign: apiHouse.sign_sanskrit || apiHouse.sign,
              sign_sanskrit: apiHouse.sign_sanskrit,
              planets: planetsInHouse,
            };
          });
        })();

    // Filter out null values (invalid houses)
    return houses.filter((h): h is NonNullable<typeof h> => h !== null);
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
  // Step 2: Map legacy chartType prop to varga format (use effectiveChartType for TRANSIT handling)
  else if (effectiveChartType === 'navamsa') {
    normalizedVarga = 'D9';
  } else if (effectiveChartType === 'dasamsa') {
    normalizedVarga = 'D10';
  } else if (effectiveChartType === 'rasi' || !effectiveChartType) {
    // Default: rasi, undefined, null, or empty string → D1
    // NOTE: If chartType was 'D1', it would have been handled above and never reached here
    normalizedVarga = 'D1';
  } else {
    // Fallback: use chartType as-is if it's already in D format
    // NOTE: D1 is handled above and will never reach here
    normalizedVarga = effectiveChartType.toUpperCase();
  }
  
  // CRITICAL: Ensure normalizedVarga is never empty
  if (!normalizedVarga || normalizedVarga.length === 0) {
    // NOTE: D1 is handled above and will never reach here
    normalizedVarga = effectiveChartType?.toUpperCase() || 'D9'; // Default to D9 instead of D1
  }
  
  // 🔒 TRANSIT CHART FIX: Treat TRANSIT exactly like D1 for rendering purposes
  // Transit charts are standalone D1-equivalent charts (not vargas)
  // They use the same house-based rendering logic as D1
  // NOTE: D1 itself is handled above and will never reach this code
  if (normalizedVarga === 'TRANSIT') {
    normalizedVarga = 'D1';
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
  
  // NOTE: D1 is handled above and will never reach this code
  // This assertion is for other charts that might be incorrectly classified
  
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
    console.error(`❌ Unable to determine chart type for ${normalizedVarga}. Must be house chart (D1-D20) or sign chart (D24-D60). Returning null.`);
    return null; // Fail silently
  }
  
  // DEFENSIVE ASSERTION: D24-D60 must NEVER be passed to house chart components
  if (isSignChartType && isHouseBasedChart) {
    console.error(`FATAL: Chart ${normalizedVarga} classified as both house and sign chart`);
    console.error(`❌ Chart ${normalizedVarga} cannot be both house and sign chart. Returning null.`);
    return null; // Fail silently
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
    console.error('❌ Ascendant sign is missing - cannot render chart. Returning null.');
    return null; // Fail silently
  }

  // 🔒 CRITICAL: Final safety guards before rendering
  // SAFETY GUARD: Prevent house charts from being rendered without houses
  if (isHouseBasedChart && (!housesForChart || housesForChart.length !== 12)) {
    console.error(
      `❌ House-based chart ${chartTypeFromData} requires 12 houses, got ${housesForChart?.length || 0}. Returning null.`
    );
    return null; // Fail silently
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
            // 🔒 CRITICAL: South Indian chart is SIGN-FIXED (signs never move)
            // 🔒 CRITICAL: North Indian chart is LAGNA-ROTATED (houses rotate by Ascendant)
            // This applies to ALL charts: D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, etc.
            console.log(`🏠 ROUTING TO HOUSE CHART RENDERER: ${chartStyle === 'north' ? 'NorthIndianChart (LAGNA-ROTATED)' : 'SouthIndianChart (SIGN-FIXED)'}`);
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

      {/* Planetary Details Table - Prokerala-style */}
      {apiChart && (
        <PlanetDetailsTable
          chartType={chartTypeFromData}
          ascendant={apiChart.Ascendant}
          planets={apiChart.Planets}
          planetFunctionalStrength={chartTypeFromData === 'D1' ? planetFunctionalStrength : undefined}
        />
      )}

      {/* Planet Functional Strength Table (Admin-only, D1-only, render-only) */}
      {IS_ADMIN_VIEW &&
        chartTypeFromData === 'D1' &&
        planetFunctionalStrength &&
        Object.keys(planetFunctionalStrength).length > 0 && (
          <PlanetStrengthTable strengthData={planetFunctionalStrength} />
        )}

      {/* Graha Drishti (Planetary Aspects) Table - Render-only from API */}
      {apiChart && (
        <GrahaDrishtiTable aspects={apiChart.Aspects || []} />
      )}
    </div>
  );
};
