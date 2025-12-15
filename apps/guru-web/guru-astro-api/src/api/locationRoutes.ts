/**
 * Location Autocomplete API Routes
 */

import { Router, Request, Response } from 'express';
import { lookupCoordinates } from '../astro-core/birthdata/geoLookup';
import { searchLocationsWorldwide, GeocodeResult } from '../services/geocodingService';
import { WORLD_CITIES } from '../data/worldCities';

const router = Router();

export interface LocationSuggestion {
  city: string;
  country: string;
  latitude: number;
  longitude: number;
  timezone: string;
  displayName: string;
}

// Use comprehensive world cities database (150+ cities worldwide)
// Falls back to OpenStreetMap Nominatim for unlimited worldwide coverage
const LOCATION_DATABASE: LocationSuggestion[] = WORLD_CITIES;

/**
 * GET /api/location/search?q=ban
 * Search locations by query string
 * Uses local database first, then OpenStreetMap Nominatim for worldwide search
 */
router.get('/search', async (req: Request, res: Response) => {
  try {
    const query = (req.query.q as string || '').trim();
    
    if (!query || query.length < 2) {
      return res.json({
        success: true,
        suggestions: [],
      });
    }

    // First, search local database
    const localResults = LOCATION_DATABASE.filter(location => {
      const cityMatch = location.city.toLowerCase().includes(query.toLowerCase());
      const countryMatch = location.country.toLowerCase().includes(query.toLowerCase());
      const displayMatch = location.displayName.toLowerCase().includes(query.toLowerCase());
      
      return cityMatch || countryMatch || displayMatch;
    }).slice(0, 5); // Limit local results to 5

    // Convert local results to LocationSuggestion format
    const localSuggestions: LocationSuggestion[] = localResults;

    // If we have good local results, return them
    if (localSuggestions.length >= 3) {
      return res.json({
        success: true,
        suggestions: localSuggestions,
      });
    }

    // Otherwise, search worldwide using OpenStreetMap Nominatim
    try {
      const worldwideResults = await searchLocationsWorldwide(query, 10);
      
      // Convert worldwide results to LocationSuggestion format
      const worldwideSuggestions: LocationSuggestion[] = worldwideResults.map(result => ({
        city: result.city,
        country: result.country,
        latitude: result.latitude,
        longitude: result.longitude,
        timezone: result.timezone,
        displayName: result.displayName,
      }));

      // Combine local and worldwide results, remove duplicates
      const allSuggestions = [...localSuggestions];
      for (const worldwide of worldwideSuggestions) {
        const isDuplicate = allSuggestions.some(
          local => 
            Math.abs(local.latitude - worldwide.latitude) < 0.01 &&
            Math.abs(local.longitude - worldwide.longitude) < 0.01
        );
        if (!isDuplicate) {
          allSuggestions.push(worldwide);
        }
      }

      res.json({
        success: true,
        suggestions: allSuggestions.slice(0, 15), // Limit to 15 total results
      });
    } catch (geocodingError) {
      // If geocoding fails, return local results only
      console.warn('Geocoding service unavailable, using local database only');
      res.json({
        success: true,
        suggestions: localSuggestions,
      });
    }
  } catch (error: any) {
    const statusCode = error.status || error.response?.status || 500;
    const errorResponse = error.response || error;
    
    res.status(statusCode).json({
      success: false,
      status: statusCode,
      error: {
        message: error.message || errorResponse?.error?.message || 'Location search failed',
        type: errorResponse?.error?.type || 'LocationSearchError',
        source: 'guru-astro-api'
      }
    });
  }
});

/**
 * GET /api/location/coordinates?city=bangalore&country=india
 * Get coordinates for a specific city/country
 * Uses local database first, then OpenStreetMap Nominatim
 */
router.get('/coordinates', async (req: Request, res: Response) => {
  try {
    const city = (req.query.city as string || '').trim();
    const country = (req.query.country as string || '').trim();
    
    if (!city || !country) {
      return res.status(400).json({
        success: false,
        error: 'City and country are required',
      });
    }

    // Try local database first
    const coords = lookupCoordinates(city.toLowerCase(), country.toLowerCase());
    
    if (coords) {
      return res.json({
        success: true,
        data: coords,
      });
    }

    // Try location database
    const location = LOCATION_DATABASE.find(
      loc => loc.city.toLowerCase() === city.toLowerCase() && loc.country.toLowerCase() === country.toLowerCase()
    );
    
    if (location) {
      return res.json({
        success: true,
        data: {
          latitude: location.latitude,
          longitude: location.longitude,
          timezone: location.timezone,
        },
      });
    }

    // Try worldwide geocoding as fallback
    try {
      const searchQuery = `${city}, ${country}`;
      const results = await searchLocationsWorldwide(searchQuery, 1);
      
      if (results.length > 0) {
        const result = results[0];
        return res.json({
          success: true,
          data: {
            latitude: result.latitude,
            longitude: result.longitude,
            timezone: result.timezone,
          },
        });
      }
    } catch (geocodingError) {
      console.warn('Geocoding service unavailable');
    }

    // Not found
    res.status(404).json({
      success: false,
      error: 'Location not found',
    });
  } catch (error: any) {
    const statusCode = error.status || error.response?.status || 500;
    const errorResponse = error.response || error;
    
    res.status(statusCode).json({
      success: false,
      status: statusCode,
      error: {
        message: error.message || errorResponse?.error?.message || 'Failed to get coordinates',
        type: errorResponse?.error?.type || 'CoordinatesError',
        source: 'guru-astro-api'
      }
    });
  }
});

export default router;

