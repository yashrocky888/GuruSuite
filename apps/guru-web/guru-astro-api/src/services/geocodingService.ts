/**
 * Geocoding Service
 * Uses OpenStreetMap Nominatim API for worldwide location search
 * Free, no API key required
 */

import axios from 'axios';

export interface NominatimResult {
  place_id: number;
  licence: string;
  powered_by: string;
  osm_type: string;
  osm_id: number;
  boundingbox: string[];
  lat: string;
  lon: string;
  display_name: string;
  class: string;
  type: string;
  importance: number;
  address?: {
    city?: string;
    town?: string;
    village?: string;
    state?: string;
    country?: string;
    country_code?: string;
  };
}

export interface GeocodeResult {
  city: string;
  country: string;
  latitude: number;
  longitude: number;
  timezone: string;
  displayName: string;
  state?: string;
}

/**
 * Search locations worldwide using OpenStreetMap Nominatim
 */
export async function searchLocationsWorldwide(query: string, limit: number = 10): Promise<GeocodeResult[]> {
  if (!query || query.length < 2) {
    return [];
  }

  try {
    // Use Nominatim API (free, no API key)
    const response = await axios.get<NominatimResult[]>('https://nominatim.openstreetmap.org/search', {
      params: {
        q: query,
        format: 'json',
        limit: limit,
        addressdetails: 1,
        extratags: 1,
      },
      headers: {
        'User-Agent': 'GuruAstrologyApp/1.0', // Required by Nominatim
      },
      timeout: 5000,
    });

    const results: GeocodeResult[] = [];

    for (const item of response.data) {
      // Filter for cities, towns, villages (not countries or states)
      if (item.class === 'place' && ['city', 'town', 'village', 'hamlet'].includes(item.type)) {
        const address = item.address || {};
        const city = address.city || address.town || address.village || '';
        const country = address.country || '';
        const state = address.state || '';

        if (city && country) {
          // Get timezone from coordinates
          const timezone = getTimezoneFromCoordinates(
            parseFloat(item.lat),
            parseFloat(item.lon)
          );

          results.push({
            city: city.toLowerCase(),
            country: country.toLowerCase(),
            latitude: parseFloat(item.lat),
            longitude: parseFloat(item.lon),
            timezone,
            displayName: `${city}${state ? `, ${state}` : ''}, ${country}`,
            state: state || undefined,
          });
        }
      }
    }

    return results;
  } catch (error: any) {
    console.error('Geocoding error:', error.message);
    return [];
  }
}

/**
 * Get timezone from coordinates using tz-lookup
 */
function getTimezoneFromCoordinates(latitude: number, longitude: number): string {
  try {
    const tzLookup = require('tz-lookup');
    return tzLookup(latitude, longitude) || 'UTC';
  } catch (error) {
    // Fallback timezone mapping by coordinates
    return getTimezoneByCoordinates(latitude, longitude);
  }
}

/**
 * Fallback timezone calculation by coordinates
 */
function getTimezoneByCoordinates(lat: number, lon: number): string {
  // Simplified timezone mapping by longitude
  // In production, use proper timezone library
  const timezoneMap: Record<string, { latRange: [number, number]; lonRange: [number, number]; tz: string }> = {
    'india': { latRange: [6, 37], lonRange: [68, 97], tz: 'Asia/Kolkata' },
    'usa_east': { latRange: [24, 50], lonRange: [-85, -67], tz: 'America/New_York' },
    'usa_central': { latRange: [24, 50], lonRange: [-102, -85], tz: 'America/Chicago' },
    'usa_west': { latRange: [24, 50], lonRange: [-125, -102], tz: 'America/Los_Angeles' },
    'uk': { latRange: [50, 61], lonRange: [-8, 2], tz: 'Europe/London' },
    'europe': { latRange: [35, 72], lonRange: [-10, 40], tz: 'Europe/Paris' },
    'china': { latRange: [18, 54], lonRange: [73, 135], tz: 'Asia/Shanghai' },
    'japan': { latRange: [24, 46], lonRange: [123, 146], tz: 'Asia/Tokyo' },
    'australia': { latRange: [-44, -10], lonRange: [113, 154], tz: 'Australia/Sydney' },
  };

  for (const [key, value] of Object.entries(timezoneMap)) {
    if (
      lat >= value.latRange[0] && lat <= value.latRange[1] &&
      lon >= value.lonRange[0] && lon <= value.lonRange[1]
    ) {
      return value.tz;
    }
  }

  return 'UTC';
}

