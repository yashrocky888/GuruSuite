/**
 * Astrology Service - HTTP API Proxy
 * 
 * This service ONLY calls the guru-api backend HTTP API.
 * NO calculations are performed here - the API is the single source of truth.
 */

import axios from 'axios';
import { BirthData, AstroCalculationResponse } from '../types';
import { validateBirthData } from '../astro-core/birthdata/validateBirthData';
import { lookupCoordinates } from '../astro-core/birthdata/geoLookup';
import { parseBirthData } from '../astro-core/birthdata/parseBirthData';

// Guru API backend URL - CANONICAL asia-south1 region (DO NOT CHANGE)
// Can be overridden via GURU_API_URL env variable if needed
const GURU_API_BASE_URL = process.env.GURU_API_URL || 'https://guru-api-660206747784.asia-south1.run.app';

export async function calculateAstroChart(
  birthData: BirthData,
  system: 'lahiri' | 'raman' | 'kp' = 'lahiri',
  houseSystem: 'placidus' | 'whole-sign' = 'placidus'
): Promise<AstroCalculationResponse> {
  // 1. Validate birth data
  const validation = validateBirthData(birthData);
  if (!validation.valid) {
    throw new Error(`Invalid birth data: ${validation.errors.join(', ')}`);
  }

  // 2. ALWAYS get coordinates from city/country (ignore manual lat/long if provided)
  // This ensures we always use location-based coordinates
  const coords = lookupCoordinates(birthData.city, birthData.country);
  if (coords) {
    birthData.latitude = coords.latitude;
    birthData.longitude = coords.longitude;
    if (!birthData.timezone) {
      birthData.timezone = coords.timezone;
    }
  } else {
    // If lookup fails, throw error - we need coordinates
    throw new Error(`Could not determine coordinates for ${birthData.city}, ${birthData.country}. Please provide a valid city and country.`);
  }

  // Validate coordinates are set
  if (!birthData.latitude || !birthData.longitude) {
    throw new Error('Could not determine coordinates for location');
  }

  // 3. Parse birth data to get formatted date/time
  const parsedData = parseBirthData(birthData);

  // 4. Format date for API (YYYY-MM-DD)
  const dateStr = `${parsedData.year}-${String(parsedData.month).padStart(2, '0')}-${String(parsedData.day).padStart(2, '0')}`;
  
  // 5. Format time for API (HH:MM)
  const timeStr = `${String(parsedData.hour).padStart(2, '0')}:${String(parsedData.minute).padStart(2, '0')}`;

  // 6. Call guru-api backend HTTP API
  // The API is the single source of truth - we do NOT perform any calculations
  try {
    const response = await axios.get(`${GURU_API_BASE_URL}/api/v1/kundli`, {
      params: {
        dob: dateStr,
        time: timeStr,
        lat: parsedData.latitude,
        lon: parsedData.longitude,
        timezone: parsedData.timezone || 'Asia/Kolkata',
      },
      timeout: 30000,
    });

    // 7. Transform API response to match expected format
    // The API returns: { D1: {...}, D2: {...}, D9: {...}, ... } directly
    const apiData = response.data;
    
    if (!apiData.D1) {
      throw new Error('Invalid response from API - D1 data missing');
    }

    const d1Data = apiData.D1;
    
    // Transform planets from API format to expected format
    const planets = Object.entries(d1Data.Planets || {}).map(([name, planetData]: [string, any]) => ({
      planet: name,
      longitude: planetData.longitude || 0,
      latitude: planetData.latitude || 0,
      distance: planetData.distance || 0,
      speed: planetData.speed || 0,
      retrograde: planetData.retrograde || false,
      sign: planetData.sign || planetData.sign_sanskrit || '',
      signNumber: planetData.sign_index !== undefined ? planetData.sign_index + 1 : 0,
      degree: planetData.degrees_in_sign || 0,
      nakshatra: planetData.nakshatra || '',
      pada: planetData.pada || 1,
      nakshatraLord: planetData.nakshatra_lord || '',
      combust: planetData.combust || false,
    }));

    // Transform houses from API format
    const houses = (d1Data.Houses || []).map((house: any) => ({
      houseNumber: house.house || 0,
      longitude: house.degree || 0,
      sign: house.sign || house.sign_sanskrit || '',
      signNumber: house.sign_index !== undefined ? house.sign_index + 1 : 0,
      degree: house.degrees_in_sign || 0,
    }));

    // Transform lagna from API format
    const ascendant = d1Data.Ascendant || {};
    const lagna = {
      longitude: ascendant.degree || 0,
      sign: ascendant.sign || ascendant.sign_sanskrit || '',
      signNumber: ascendant.sign_index !== undefined ? ascendant.sign_index + 1 : 0,
      degree: ascendant.degrees_in_sign || 0,
    };

    // Generate charts from API data (NO calculations, just formatting)
    const rashiChartNorth = generateNorthIndianChartFromAPI(d1Data);
    const rashiChartSouth = generateSouthIndianChartFromAPI(d1Data);
    const navamsaChart = apiData.D9 ? generateNavamsaChartFromAPI(apiData.D9) : undefined;

    return {
      birthData: parsedData,
      planets,
      houses,
      lagna,
      rashiChartNorth,
      rashiChartSouth,
      navamsaChart,
    };
  } catch (error: any) {
    // Preserve error structure from backend API
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data;
      
      // If backend returns structured error, preserve it
      if (data?.error || data?.success === false) {
        const apiError = new Error(data?.error?.message || data?.error || data?.detail || 'API request failed');
        (apiError as any).status = status;
        (apiError as any).response = data;
        throw apiError;
      }
      
      // Fallback for non-structured errors
      throw new Error(`API Error: ${status} - ${data?.detail || data?.error || error.message}`);
    }
    
    // Network or other errors
    throw new Error(`Failed to fetch kundli from API: ${error.message || 'Unknown error'}`);
  }
}

/**
 * Generate North Indian chart from API data (NO calculations)
 */
function generateNorthIndianChartFromAPI(d1Data: any): any {
  const houses = (d1Data.Houses || []).map((house: any, index: number) => {
    const houseNumber = house.house || index + 1;
    const signNumber = house.sign_index !== undefined ? house.sign_index + 1 : 0;
    
    // Find planets in this house from API data
    const housePlanets = Object.entries(d1Data.Planets || {})
      .filter(([_, planetData]: [string, any]) => planetData.house === houseNumber)
      .map(([name, planetData]: [string, any]) => ({
        name,
        degree: planetData.degrees_in_sign || 0,
        nakshatra: planetData.nakshatra || '',
        pada: planetData.pada || 1,
      }));

    return {
      houseNumber,
      sign: house.sign || house.sign_sanskrit || '',
      signNumber,
      planets: housePlanets,
    };
  });

  return { houses };
}

/**
 * Generate South Indian chart from API data (NO calculations)
 */
function generateSouthIndianChartFromAPI(d1Data: any): any {
  // Same as North Indian - just pass through API data
  return generateNorthIndianChartFromAPI(d1Data);
}

/**
 * Generate Navamsa chart from API data (NO calculations)
 */
function generateNavamsaChartFromAPI(d9Data: any): any {
  const houses = Array.from({ length: 12 }, (_, i) => {
    const houseNumber = i + 1;
    const signNumber = houseNumber; // For varga charts, house = sign
    
    // Find planets in this house from D9 API data
    const housePlanets = Object.entries(d9Data.planets || {})
      .filter(([_, planetData]: [string, any]) => planetData.house === houseNumber)
      .map(([name, planetData]: [string, any]) => ({
        name,
        degree: planetData.degrees_in_sign || 0,
      }));

    // Get sign name from first planet in house, or use sign number
    const firstPlanet = housePlanets.length > 0 
      ? Object.values(d9Data.planets || {}).find((p: any) => p.house === houseNumber)
      : null;

    return {
      houseNumber,
      sign: firstPlanet?.sign || firstPlanet?.sign_sanskrit || '',
      signNumber,
      planets: housePlanets,
    };
  });

  return {
    chartType: 'D9',
    houses,
  };
}

