/**
 * Geo Lookup - Get coordinates from city/country
 * Simplified implementation - in production use proper geocoding API
 */

export interface GeoCoordinates {
  latitude: number;
  longitude: number;
  timezone: string;
}

// Common city coordinates database
const CITY_COORDINATES: Record<string, GeoCoordinates> = {
  // India
  'bangalore': { latitude: 12.9716, longitude: 77.5946, timezone: 'Asia/Kolkata' },
  'mumbai': { latitude: 19.0760, longitude: 72.8777, timezone: 'Asia/Kolkata' },
  'delhi': { latitude: 28.6139, longitude: 77.2090, timezone: 'Asia/Kolkata' },
  'chennai': { latitude: 13.0827, longitude: 80.2707, timezone: 'Asia/Kolkata' },
  'kolkata': { latitude: 22.5726, longitude: 88.3639, timezone: 'Asia/Kolkata' },
  'hyderabad': { latitude: 17.3850, longitude: 78.4867, timezone: 'Asia/Kolkata' },
  'pune': { latitude: 18.5204, longitude: 73.8567, timezone: 'Asia/Kolkata' },
  'ahmedabad': { latitude: 23.0225, longitude: 72.5714, timezone: 'Asia/Kolkata' },
  'surat': { latitude: 21.1702, longitude: 72.8311, timezone: 'Asia/Kolkata' },
  'jaipur': { latitude: 26.9124, longitude: 75.7873, timezone: 'Asia/Kolkata' },
  
  // USA
  'new york': { latitude: 40.7128, longitude: -74.0060, timezone: 'America/New_York' },
  'los angeles': { latitude: 34.0522, longitude: -118.2437, timezone: 'America/Los_Angeles' },
  'chicago': { latitude: 41.8781, longitude: -87.6298, timezone: 'America/Chicago' },
  'houston': { latitude: 29.7604, longitude: -95.3698, timezone: 'America/Chicago' },
  
  // UK
  'london': { latitude: 51.5074, longitude: -0.1278, timezone: 'Europe/London' },
  
  // Other
  'singapore': { latitude: 1.3521, longitude: 103.8198, timezone: 'Asia/Singapore' },
  'dubai': { latitude: 25.2048, longitude: 55.2708, timezone: 'Asia/Dubai' },
};

export function lookupCoordinates(city: string, country: string): GeoCoordinates | null {
  const cityKey = city.toLowerCase().trim();
  const countryKey = country.toLowerCase().trim();
  
  // Try exact city match
  if (CITY_COORDINATES[cityKey]) {
    return CITY_COORDINATES[cityKey];
  }
  
  // Try city with common variations
  const cityVariations = [
    cityKey,
    cityKey.replace(/\s+/g, ''), // Remove spaces
    cityKey.replace(/\s+/g, '_'), // Replace spaces with underscore
  ];
  
  for (const variation of cityVariations) {
    if (CITY_COORDINATES[variation]) {
      return CITY_COORDINATES[variation];
    }
  }
  
  // Try city_country combination
  const combinedKey = `${cityKey}_${countryKey}`;
  if (CITY_COORDINATES[combinedKey]) {
    return CITY_COORDINATES[combinedKey];
  }
  
  // Try using geolib for approximate coordinates based on country center
  try {
    const geolib = require('geolib');
    const countryCenters: Record<string, { latitude: number; longitude: number }> = {
      'india': { latitude: 20.5937, longitude: 78.9629 },
      'usa': { latitude: 39.8283, longitude: -98.5795 },
      'united states': { latitude: 39.8283, longitude: -98.5795 },
      'uk': { latitude: 55.3781, longitude: -3.4360 },
      'united kingdom': { latitude: 55.3781, longitude: -3.4360 },
      'canada': { latitude: 56.1304, longitude: -106.3468 },
      'australia': { latitude: -25.2744, longitude: 133.7751 },
      'germany': { latitude: 51.1657, longitude: 10.4515 },
      'france': { latitude: 46.2276, longitude: 2.2137 },
      'japan': { latitude: 36.2048, longitude: 138.2529 },
      'china': { latitude: 35.8617, longitude: 104.1954 },
      'brazil': { latitude: -14.2350, longitude: -51.9253 },
    };
    
    const countryCenter = countryCenters[countryKey];
    if (countryCenter) {
      // Default timezone by country
      const countryTimezones: Record<string, string> = {
        'india': 'Asia/Kolkata',
        'usa': 'America/New_York',
        'united states': 'America/New_York',
        'uk': 'Europe/London',
        'united kingdom': 'Europe/London',
        'canada': 'America/Toronto',
        'australia': 'Australia/Sydney',
        'germany': 'Europe/Berlin',
        'france': 'Europe/Paris',
        'japan': 'Asia/Tokyo',
        'china': 'Asia/Shanghai',
        'brazil': 'America/Sao_Paulo',
      };
      
      const timezone = countryTimezones[countryKey] || 'UTC';
      
      // Return country center as fallback
      return {
        latitude: countryCenter.latitude,
        longitude: countryCenter.longitude,
        timezone,
      };
    }
  } catch (error) {
    // geolib not available, continue with null
  }
  
  // Default timezone by country
  const countryTimezones: Record<string, string> = {
    'india': 'Asia/Kolkata',
    'usa': 'America/New_York',
    'united states': 'America/New_York',
    'uk': 'Europe/London',
    'united kingdom': 'Europe/London',
  };
  
  const timezone = countryTimezones[countryKey] || 'UTC';
  
  // Last resort: return country center if we have it, otherwise null
  return null;
}

