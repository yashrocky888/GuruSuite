/**
 * Chart Container - Wrapper with North/South toggle
 * Modern glassmorphic styling
 * FIXED: Better API data debugging
 * 
 * API Calculation Method:
 * - Uses FLG_SIDEREAL flag for direct sidereal positions (no manual ayanamsa subtraction)
 * - Uses swe.houses_ex() with FLG_SIDEREAL for sidereal ascendant (no manual conversion)
 * - All positions are already in sidereal zodiac format from API
 */

'use client';

import React, { useState, useMemo } from 'react';
import SouthIndianChart from './SouthIndianChart';
import { NorthIndianChart } from './NorthIndianChart';
import { normalizeKundliData, ApiKundliData, convertToSanskritSign, SIGN_TO_NUM, getSignNum, getSignForHouse, getSignName } from './utils';

interface ChartContainerProps {
  chartData: any; // Raw API data
  chartType?: 'rasi' | 'navamsa' | 'dasamsa';
}

type ChartStyle = 'north' | 'south';

export const ChartContainer: React.FC<ChartContainerProps> = ({ 
  chartData, 
  chartType = 'rasi' 
}) => {
  const [chartStyle, setChartStyle] = useState<ChartStyle>('south');

  // Normalize API data to houses
  const houses = useMemo(() => {
    if (!chartData) {
      console.warn('ChartContainer: No chartData provided');
      return [];
    }
    
    // Handle multiple API formats
    let planetsArray: any[] = [];
    let ascendantData: any = null;
    let housesArray: any[] = [];
    
    // Check if it's the new nested format: { success: true, data: { kundli: { Ascendant: {...}, Planets: {...}, Houses: [...] } } }
    // OR direct nested: { data: { kundli: {...} } }
    // OR already extracted: { Ascendant: {...}, Planets: {...}, Houses: [...] }
    // OR API returns D1 directly: { D1: { Ascendant: {...}, Planets: {...}, Houses: [...] }, D2: {...}, ... }
    // OR divisional chart format: { chartType: "D9", lagnaSign: "...", planets: [...], houses: [...] }
    // OR old format: { lagnaSign: "...", planets: [...], houses: [...] }
    let kundli = null;
    if ((chartData as any).success && (chartData as any).data?.kundli) {
      // Full nested format: { success: true, data: { kundli: {...} } }
      kundli = (chartData as any).data.kundli;
      console.log('✅ Using nested format: success.data.kundli', {
        hasPlanets: !!(kundli as any).Planets,
        planetsType: typeof (kundli as any).Planets,
        planetsKeys: (kundli as any).Planets ? Object.keys((kundli as any).Planets) : []
      });
    } else if ((chartData as any).data?.kundli) {
      // Direct nested: { data: { kundli: {...} } }
      kundli = (chartData as any).data.kundli;
      console.log('✅ Using nested format: data.kundli', {
        hasPlanets: !!(kundli as any).Planets,
        planetsType: typeof (kundli as any).Planets,
        planetsKeys: (kundli as any).Planets ? Object.keys((kundli as any).Planets) : []
      });
    } else if ((chartData as any).D1) {
      // API returns D1 directly: { D1: { Ascendant: {...}, Planets: {...}, Houses: [...] }, D2: {...}, ... }
      // D1 is the main Rashi chart
      kundli = (chartData as any).D1;
      console.log('✅ Using D1 format (main chart from API)', {
        hasPlanets: !!(kundli as any).Planets,
        planetsType: typeof (kundli as any).Planets,
        planetsKeys: (kundli as any).Planets ? Object.keys((kundli as any).Planets) : [],
        allKeys: Object.keys(chartData as any)
      });
    } else if ((chartData as any).Ascendant || (chartData as any).Planets || (chartData as any).Houses) {
      // Already extracted kundli object: { Ascendant: {...}, Planets: {...}, Houses: [...] }
      kundli = chartData;
      console.log('✅ Using extracted kundli format', {
        hasPlanets: !!(kundli as any).Planets,
        planetsType: typeof (kundli as any).Planets,
        planetsKeys: (kundli as any).Planets ? Object.keys((kundli as any).Planets) : []
      });
    } else if ((chartData as any).chartType || ((chartData as any).planets && Array.isArray((chartData as any).planets))) {
      // Divisional chart format: { chartType: "D9", lagnaSign: "...", planets: [...], houses: [...] }
      // Use chartData directly as it already has planets array and houses
      kundli = null; // Will be handled in the else block below
      console.log('✅ Using divisional chart format', {
        hasPlanets: !!(chartData as any).planets,
        planetsCount: Array.isArray((chartData as any).planets) ? (chartData as any).planets.length : 0
      });
    } else {
      console.warn('⚠️ Unknown chart data format:', Object.keys(chartData as any));
    }
    
    if (kundli) {
      
      // Extract Ascendant - Use exact API fields
      if (kundli.Ascendant) {
        ascendantData = {
          sign: kundli.Ascendant.sign_sanskrit || kundli.Ascendant.sign, // Use sign_sanskrit (Sanskrit name)
          sign_sanskrit: kundli.Ascendant.sign_sanskrit, // Keep sign_sanskrit
          degree: kundli.Ascendant.degree, // Full longitude (0-360)
          degree_dms: kundli.Ascendant.degree_dms, // Degree part (int)
          arcminutes: kundli.Ascendant.arcminutes, // Minutes part (int)
          arcseconds: kundli.Ascendant.arcseconds, // Seconds part (int)
          degrees_in_sign: kundli.Ascendant.degrees_in_sign, // Degrees in sign (0-29.999)
          house: kundli.Ascendant.house, // House number (1-12)
          nakshatra: kundli.Ascendant.nakshatra,
          pada: kundli.Ascendant.pada,
        };
      }
      
      // Extract Planets from object to array - Use sign_sanskrit, retro, and degrees_in_sign
      if (kundli.Planets && typeof kundli.Planets === 'object') {
        const planetsEntries = Object.entries(kundli.Planets);
        console.log(`📦 Extracting ${planetsEntries.length} planets from Planets object`);
        
        planetsArray = planetsEntries.map(([name, data]: [string, any]) => {
          // For chart display, use degrees_in_sign (0-30°) for positioning
          // But keep total degree for reference
          const displayDegree = data.degrees_in_sign !== undefined 
            ? data.degrees_in_sign 
            : (data.degree % 30); // Calculate degrees in sign from total degree
          
          // Extract house number - API uses 'house' field (EXACT from API)
          const houseNumber = data.house !== undefined ? data.house : 1;
          
          // CRITICAL: Calculate DMS from degrees_in_sign (0-30°), NOT from degree_dms (which is 0-360°)
          // API returns degree_dms as total degree, but we need DMS in 0-30° format
          const degreeInSign = displayDegree; // Already in 0-30° range from degrees_in_sign
          const degreeDms = Math.floor(degreeInSign); // Integer part of degrees in sign (0-29)
          const minutes = Math.floor((degreeInSign - degreeDms) * 60); // Minutes from fractional part
          const seconds = Math.floor(((degreeInSign - degreeDms) * 60 - minutes) * 60); // Seconds
          
          // Use calculated DMS from degrees_in_sign (0-30° format)
          const degreeMinutes = minutes;
          const degreeSeconds = seconds;
          
          // Special logging for Venus to debug missing planet issue
          if (name === 'Venus') {
            console.log(`  🔍 VENUS DEBUG:`, {
              name,
              house: houseNumber,
              sign: data.sign_sanskrit || data.sign,
              degree: displayDegree,
              total_degree: data.degree,
              degrees_in_sign: data.degrees_in_sign,
              has_house: data.house !== undefined,
              has_sign: !!(data.sign_sanskrit || data.sign),
              has_degree: data.degree !== undefined
            });
          }
          
          console.log(`  📍 ${name}: House=${houseNumber}, Sign=${data.sign_sanskrit || data.sign}, Degree=${displayDegree}° (${data.degree}° total), DMS=${degreeDms}°${degreeMinutes}'${degreeSeconds}"`);
          
          return {
            name,
            sign: data.sign_sanskrit || data.sign, // Use sign_sanskrit (Sanskrit name) - EXACT from API
            house: houseNumber, // Use house field from API - EXACT from API
            degree: displayDegree, // Degrees in sign (0-30°) for chart positioning - EXACT from API
            total_degree: data.degree, // Keep total degree (0-360°) for calculations - EXACT from API
            degree_dms: degreeDms, // Degree part (int) from API - EXACT from API
            degree_minutes: degreeMinutes, // Minutes component from arcminutes (API field name)
            degree_seconds: degreeSeconds, // Seconds component from arcseconds (API field name)
            degrees_in_sign: data.degrees_in_sign, // Keep degrees_in_sign for reference
            nakshatra: data.nakshatra,
            pada: data.pada,
            retrograde: data.retro === true || data.retrograde === true, // Check retro as boolean (API field name)
            speed: data.speed,
            color: data.color,
          };
        });
        console.log(`✅ Extracted ${planetsArray.length} planets:`, planetsArray.map(p => `${p.name} (${p.sign}, H${p.house})`).join(', '));
        
        // Check if Venus is in the array
        const venusPlanet = planetsArray.find(p => p.name === 'Venus');
        if (!venusPlanet) {
          console.error('❌ VENUS NOT FOUND in extracted planets array!');
        } else {
          console.log(`✅ Venus found: House=${venusPlanet.house}, Sign=${venusPlanet.sign}, Degree=${venusPlanet.degree}°`);
        }
      } else {
        console.warn('⚠️ No Planets object found in kundli:', {
          hasPlanets: !!(kundli as any).Planets,
          planetsType: typeof (kundli as any).Planets,
          allKeys: Object.keys(kundli as any)
        });
      }
      
      // Extract Houses array - use sign_sanskrit if available
      if (Array.isArray(kundli.Houses)) {
        housesArray = kundli.Houses.map((h: any) => ({
          house: h.house,
          sign: h.sign_sanskrit || h.sign, // Prefer Sanskrit
          degree: h.degree,
          degrees_in_sign: h.degrees_in_sign,
        }));
      }
    } else {
      // Direct format: { lagnaSign: "Vrishchika", planets: [...], houses: [...] }
      // OR divisional chart format: { chartType: "D9", lagnaSign: "...", planets: [...], houses: [...] }
      // OR new consistent format: { ascendant, ascendant_sign, planets }
      // OR divisional chart API format: { ascendant: float, ascendant_sign: "English", planets: {...} }
      
      // Handle divisional chart format: { ascendant: float, ascendant_sign: "English", ascendant_sign_sanskrit: "Karka", planets: {...} }
      if ((chartData as any).ascendant !== undefined && typeof (chartData as any).ascendant === 'number') {
        // Divisional chart format: ascendant is a float, need to convert
        const ascendantDegree = (chartData as any).ascendant;
        // Prefer ascendant_sign_sanskrit if available (from API), else convert English
        const sanskritSign = (chartData as any).ascendant_sign_sanskrit 
          || convertToSanskritSign((chartData as any).ascendant_sign || 'Aries');
        const signIndex = getSignNum(sanskritSign);
        const degreesInSign = ascendantDegree % 30;
        
        // Calculate DMS from degrees_in_sign
        const degreeDms = Math.floor(degreesInSign);
        const minutes = Math.floor((degreesInSign - degreeDms) * 60);
        const seconds = Math.floor(((degreesInSign - degreeDms) * 60 - minutes) * 60);
        
        // CRITICAL: For varga charts, use ascendant_house from API
        // API provides ascendant_house = ascendant sign (Whole Sign system)
        const ascendantHouse = (chartData as any).ascendant_house !== undefined
          ? (chartData as any).ascendant_house  // Use API's ascendant_house value
          : (signIndex + 1); // Fallback: house = sign (should not happen)
        
        ascendantData = {
          sign: sanskritSign,
          sign_sanskrit: sanskritSign,
          degree: ascendantDegree,
          degree_dms: degreeDms,
          arcminutes: minutes,
          arcseconds: seconds,
          degrees_in_sign: degreesInSign,
          house: ascendantHouse, // Use API's ascendant_house (house = sign for varga charts)
        };
        
        // Extract planets from object - convert English signs to Sanskrit
        if ((chartData as any).planets && typeof (chartData as any).planets === 'object') {
          const planetsEntries = Object.entries((chartData as any).planets);
          console.log(`📦 Extracting ${planetsEntries.length} planets from divisional chart format`);
          
          planetsArray = planetsEntries.map(([name, data]: [string, any]) => {
            // Convert English sign to Sanskrit
            const englishSign = data.sign || '';
            const sanskritSign = convertToSanskritSign(englishSign);
            const displayDegree = data.degrees_in_sign !== undefined 
              ? data.degrees_in_sign 
              : (data.degree % 30);
            
            // Calculate DMS from degrees_in_sign
            const degreeInSign = displayDegree;
            const degreeDms = Math.floor(degreeInSign);
            const minutes = Math.floor((degreeInSign - degreeDms) * 60);
            const seconds = Math.floor(((degreeInSign - degreeDms) * 60 - minutes) * 60);
            
            // CRITICAL: For varga charts, use house directly from API
            // API provides house = sign (Whole Sign system)
            // DO NOT calculate or infer house
            const planetHouse = data.house !== undefined && data.house >= 1 && data.house <= 12
              ? data.house  // Use API's house value directly
              : (getSignNum(sanskritSign)); // Fallback: should not happen
            
            return {
              name,
              sign: sanskritSign,
              house: planetHouse, // Use API house value (house = sign for varga charts)
              degree: displayDegree,
              degrees_in_sign: displayDegree,
              degree_dms: degreeDms,
              degree_minutes: minutes,
              degree_seconds: seconds,
              total_degree: data.degree,
              retrograde: data.retro || false,
              nakshatra: data.nakshatra,
              pada: data.pada,
            };
          });
        }
        
        // For varga charts: Use fixed sign grid (house = sign number)
        // Do NOT rotate by ascendant - Whole Sign system means house = sign
        const isVargaChart = (chartData as any).chartType && (chartData as any).chartType !== 'D1';
        
        if (isVargaChart) {
          // Fixed sign grid: House 1 = Mesha, House 2 = Vrishabha, ..., House 12 = Meena
          for (let i = 1; i <= 12; i++) {
            housesArray.push({
              house: i,
              sign: getSignName(i),
              sign_sanskrit: getSignName(i),
              degree: 0,
              degrees_in_sign: 0,
            });
          }
        } else {
          // For D1: Generate houses from ascendant sign (whole sign system)
          const lagnaSignNum = signIndex;
          for (let i = 1; i <= 12; i++) {
            const houseSignNum = getSignForHouse(i, lagnaSignNum);
            housesArray.push({
              house: i,
              sign: getSignName(houseSignNum),
              sign_sanskrit: getSignName(houseSignNum),
              degree: 0,
              degrees_in_sign: 0,
            });
          }
        }
      } else if ((chartData as any).ascendant_sign !== undefined) {
        // New consistent format (already Sanskrit)
        ascendantData = {
          sign: (chartData as any).ascendant_sign,
          sign_sanskrit: (chartData as any).ascendant_sign,
          degree: (chartData as any).lagnaDegree || 0,
        };
        planetsArray = (chartData as any).planets || [];
      } else {
        // Legacy format
        ascendantData = (chartData as any).Ascendant || { 
          sign: (chartData as any).lagnaSignSanskrit || (chartData as any).lagnaSign || (chartData as any).ascendantSign,
          degree: (chartData as any).lagnaDegree,
          sign_sanskrit: (chartData as any).lagnaSignSanskrit || (chartData as any).lagnaSign
        };
        planetsArray = (chartData as any).planets || [];
      }
      
      // Handle houses - could be array of numbers or array of objects
      if (Array.isArray((chartData as any).houses)) {
        housesArray = (chartData as any).houses;
      } else if ((chartData as any).houses) {
        // If houses is an object, convert to array
        housesArray = Object.values((chartData as any).houses);
      } else {
        housesArray = [];
      }
    }
    
    // Convert to ApiKundliData format - API now returns Sanskrit names directly, but convert if English for backward compatibility
    // Handle new consistent structure: {ascendant, ascendant_sign, planets}
    // PRIORITY: Use ascendantData.sign_sanskrit first (already converted), then check other sources
    const ascendantSign = ascendantData?.sign_sanskrit 
      ? ascendantData.sign_sanskrit // Highest priority: Already converted Sanskrit from ascendantData
      : (ascendantData?.sign 
        ? (SIGN_TO_NUM[ascendantData.sign] ? ascendantData.sign : convertToSanskritSign(ascendantData.sign))
        : ((chartData as any).ascendant_sign 
          ? (SIGN_TO_NUM[(chartData as any).ascendant_sign] ? (chartData as any).ascendant_sign : convertToSanskritSign((chartData as any).ascendant_sign))
          : ((chartData as any).lagnaSignSanskrit
            ? (chartData as any).lagnaSignSanskrit
            : ((chartData as any).lagnaSign 
              ? (SIGN_TO_NUM[(chartData as any).lagnaSign] ? (chartData as any).lagnaSign : convertToSanskritSign((chartData as any).lagnaSign))
              : ((chartData as any).ascendantSign 
                ? (SIGN_TO_NUM[(chartData as any).ascendantSign] ? (chartData as any).ascendantSign : convertToSanskritSign((chartData as any).ascendantSign))
                : undefined)))));
    
    // Extract lagna degree - use degrees_in_sign for Ascendant if available
    const lagnaDegree = (chartData as any).lagnaDegree 
      || (ascendantData?.degrees_in_sign !== undefined 
        ? (ascendantData.degrees_in_sign + (getSignNum(ascendantData.sign_sanskrit || ascendantData.sign || 'Mesha') * 30))
        : ascendantData?.degree);

    // Determine chart type from various sources
    // Priority: 1. chartType from API, 2. chartType prop, 3. detect from structure
    let detectedChartType = (chartData as any).chartType;
    if (!detectedChartType) {
      // Check if it's a divisional chart by looking at the structure
      if ((chartData as any).D2 || (chartData as any).D3 || (chartData as any).D7 || 
          (chartData as any).D9 || (chartData as any).D10 || (chartData as any).D12) {
        // This is the main kundli response with multiple charts, not a specific chart
        detectedChartType = 'D1';
      } else if ((chartData as any).ascendant !== undefined && typeof (chartData as any).ascendant === 'number' && 
                 (chartData as any).ascendant_sign && !(chartData as any).Planets) {
        // Divisional chart format: { ascendant: float, ascendant_sign: "English", chartType: "D12", planets: {...} }
        // API now provides chartType, but fallback to detection if missing
        detectedChartType = (chartData as any).chartType || 
                           (chartType === 'navamsa' ? 'D9' : chartType === 'dasamsa' ? 'D10' : 'D9');
      }
    }
    
    const apiData: ApiKundliData = {
      lagna: (chartData as any).ascendant ?? chartData.lagna ?? undefined, // New format uses 'ascendant', legacy uses 'lagna'
      lagnaSign: ascendantSign,
      lagnaSignSanskrit: ascendantData?.sign_sanskrit || (chartData as any).lagnaSignSanskrit || (ascendantSign ? (SIGN_TO_NUM[ascendantSign] ? ascendantSign : convertToSanskritSign(ascendantSign)) : undefined),
      lagnaDegree: lagnaDegree, // Full longitude (0-360°) for Ascendant
      lagnaDegreeInSign: ascendantData?.degrees_in_sign, // Degrees in sign (0-30°) for Ascendant
      lagnaDegreeDms: ascendantData?.degree_dms, // Degree part (int) for Ascendant
      lagnaArcminutes: ascendantData?.arcminutes, // Minutes part (int) for Ascendant
      lagnaArcseconds: ascendantData?.arcseconds, // Seconds part (int) for Ascendant
      ascendantHouse: (chartData as any).ascendant_house !== undefined
        ? (chartData as any).ascendant_house  // From divisional chart format: { ascendant_house: 4 }
        : (ascendantData?.house !== undefined
          ? ascendantData.house  // From D1 format: { Ascendant: { house: 1 } }
          : undefined), // CRITICAL: Use API's ascendant_house (house = sign for varga charts)
      chartType: detectedChartType,
      planets: planetsArray.map((p: any) => {
        // Use sign_sanskrit if available, else convert sign to Sanskrit
        const sign = p.sign_sanskrit 
          ? p.sign_sanskrit 
          : (p.sign ? (SIGN_TO_NUM[p.sign] ? p.sign : convertToSanskritSign(p.sign)) : '');
        
        // Use degrees_in_sign for display (0-30°), fallback to degree
        const displayDegree = p.degrees_in_sign !== undefined ? p.degrees_in_sign : (p.degree || 0);
        
        const planetData = {
          name: p.name,
          sign: sign, // Sanskrit sign
          house: p.house || 1,
          degree: displayDegree, // Degrees in sign (0-30°) for display
          degrees_in_sign: p.degrees_in_sign !== undefined ? p.degrees_in_sign : displayDegree, // Keep degrees_in_sign for normalization
          total_degree: p.total_degree || p.degree, // Total longitude (0-360°) for calculations
          degree_dms: p.degree_dms, // Pass through DMS components
          degree_minutes: p.degree_minutes, // Pass through arcminutes (from API: arcminutes)
          degree_seconds: p.degree_seconds, // Pass through arcseconds (from API: arcseconds)
          nakshatra: p.nakshatra,
          pada: p.pada,
          retrograde: p.retrograde || p.retro || false, // Map 'retro' to 'retrograde'
          color: p.color,
          speed: p.speed,
          longitude: p.total_degree || p.degree, // Use total degree as longitude
        };
        
        // Debug: Log if planet is missing required fields
        if (!planetData.name || !planetData.sign || planetData.house === undefined || planetData.degree === undefined) {
          console.warn('⚠️ Planet missing required fields:', {
            name: planetData.name,
            sign: planetData.sign,
            house: planetData.house,
            degree: planetData.degree,
            original: p
          });
        }
        
        return planetData;
      }).filter((p: any) => {
        const isValid = p.name && p.sign && p.house !== undefined && p.degree !== undefined;
        if (!isValid) {
          console.warn('❌ Filtering out invalid planet:', p);
        }
        return isValid;
      }) as any,
      ayanamsa: chartData.ayanamsa,
      system: chartData.system,
      houses: housesArray,
    };

    console.log('📊 Final apiData before normalization:', {
      planetsCount: apiData.planets.length,
      planets: apiData.planets.map(p => `${p.name}: ${p.sign} H${p.house}`),
      housesCount: apiData.houses?.length || 0
    });

    const normalizedHouses = normalizeKundliData(apiData);
    
    console.log('✅ Normalized houses:', normalizedHouses.map(h => ({
      house: h.houseNumber,
      sign: h.signName,
      planets: h.planets.map(p => p.abbr)
    })));
    
    return normalizedHouses;
  }, [chartData]);

  if (!chartData || houses.length === 0) {
    return (
      <div className="glass rounded-xl p-10 text-center">
        <p className="text-gray-500 dark:text-gray-400">No chart data available</p>
      </div>
    );
  }

  // Get ascendant info for display - use actual ascendant sign from API, not house 1's sign
  // For South Indian charts, house 1 always = Mesha (fixed grid), but ascendant can be in any sign
  // Priority order for D1 and divisional charts:
  // 1. D1: Ascendant.sign_sanskrit (from D1.Ascendant)
  // 2. Divisional: ascendant_sign_sanskrit (from D2/D9/etc)
  // 3. Ascendant planet's sign (from normalized houses)
  // 4. lagnaSignSanskrit
  // 5. Convert ascendant_sign (English) to Sanskrit
  const ascendantHouseObj = houses.find(h => h.planets.some(p => p.name === 'Ascendant'));
  
  // Check D1 format first: { D1: { Ascendant: { sign_sanskrit: "Vrishchika" } } }
  let ascendantSignName = (chartData as any).D1?.Ascendant?.sign_sanskrit
    // Then check direct format: { Ascendant: { sign_sanskrit: "Vrishchika" } }
    || (chartData as any).Ascendant?.sign_sanskrit
    // Then check divisional format: { ascendant_sign_sanskrit: "Karka" }
    || (chartData as any).ascendant_sign_sanskrit
    // Then check Ascendant planet in normalized houses
    || ascendantHouseObj?.planets.find(p => p.name === 'Ascendant')?.sign
    // Then check lagnaSignSanskrit
    || (chartData as any).lagnaSignSanskrit
    || (chartData as any).lagnaSign;
  
  // If we got ascendant_sign (English), convert to Sanskrit
  if (!ascendantSignName && (chartData as any).ascendant_sign) {
    ascendantSignName = SIGN_TO_NUM[(chartData as any).ascendant_sign] 
      ? (chartData as any).ascendant_sign 
      : convertToSanskritSign((chartData as any).ascendant_sign);
  }
  
  // Final fallback
  if (!ascendantSignName) {
    ascendantSignName = houses.find(h => h.houseNumber === 1)?.signName || 'Mesha';
  }

  // Extract ascendant_house from API (for varga charts: house = sign)
  // Priority: 1. ascendant_house from divisional chart format, 2. Ascendant.house from D1 format
  const ascendantHouse = (chartData as any).ascendant_house !== undefined
    ? (chartData as any).ascendant_house  // From divisional chart format: { ascendant_house: 4 }
    : ((chartData as any).D1?.Ascendant?.house !== undefined
      ? (chartData as any).D1.Ascendant.house  // From D1 format: { D1: { Ascendant: { house: 1 } } }
      : ((chartData as any).Ascendant?.house !== undefined
        ? (chartData as any).Ascendant.house  // From direct format: { Ascendant: { house: 1 } }
        : undefined));

  return (
    <div className="glass rounded-xl p-6 border border-white/20">
      {/* Toggle */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-white/10">
        <div>
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
            {chartType === 'navamsa' ? 'Navamsa Chart (D9)' : 
             chartType === 'dasamsa' ? 'Dasamsa Chart (D10)' : 
             (chartData as any)?.chartType ? `${(chartData as any).chartType} Chart` :
             'Kundli Chart'}
          </h3>
          {chartData && ((chartData as any).lagnaSign || (chartData as any).lagnaSignSanskrit) && (
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Lagna: {(chartData as any).lagnaSignSanskrit || (chartData as any).lagnaSign}
              {((chartData as any).lagnaDegree !== undefined) && ` (${((chartData as any).lagnaDegree).toFixed(2)}°)`}
            </p>
          )}
        </div>

        <div className="flex items-center space-x-3">
          <span className={`text-sm font-medium transition-colors ${
            chartStyle === 'south' ? 'text-amber-600 dark:text-amber-400' : 'text-gray-500'
          }`}>
            South
          </span>
          <button
            onClick={() => setChartStyle(chartStyle === 'north' ? 'south' : 'north')}
            className="p-2 rounded-lg glass border border-white/20 hover:border-amber-500/50 transition-smooth"
            aria-label="Toggle chart style"
          >
            <svg className="w-4 h-4 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
          </button>
          <span className={`text-sm font-medium transition-colors ${
            chartStyle === 'north' ? 'text-amber-600 dark:text-amber-400' : 'text-gray-500'
          }`}>
            North
          </span>
        </div>
      </div>

      {/* Chart Display */}
      <div className="w-full bg-gradient-to-br from-amber-50/30 to-orange-50/30 dark:from-amber-900/10 dark:to-orange-900/10 rounded-lg p-6 border border-amber-200/30 dark:border-amber-800/30 flex justify-center items-center min-h-[400px]">
        {chartStyle === 'north' ? (
          <NorthIndianChart 
            houses={houses} 
            ascendantSign={ascendantSignName}
            ascendantHouse={ascendantHouse} // Pass API's ascendant_house for varga charts
          />
        ) : (
          <SouthIndianChart houses={houses} />
        )}
      </div>

      {/* Chart Info */}
      <div className="mt-4 text-xs text-gray-600 dark:text-gray-400 text-center space-y-1">
        <p className="font-semibold">
          Lagna: {ascendantSignName} | Style: {chartStyle === 'north' ? 'North Indian (Diamond)' : 'South Indian (Rectangular)'}
        </p>
        <p>Vedic Sidereal System | {chartData.ayanamsa || 'Lahiri'} Ayanamsa | Planets: {chartData.planets?.length || 0}</p>
        <p className="text-xs opacity-75">API Lagna: {chartData.lagnaSign || chartData.lagna || 'N/A'}</p>
      </div>
    </div>
  );
};
