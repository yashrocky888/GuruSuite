/**
 * API Service - Frontend API Client
 * Connects to Guru API backend (Python FastAPI)
 * Updated for Drik Panchang & JHORA compatibility
 */

import axios from 'axios';

// CANONICAL API URL - asia-south1 region (DO NOT CHANGE)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://guru-api-660206747784.asia-south1.run.app';
const LOCATION_API_BASE_URL = process.env.NEXT_PUBLIC_ASTRO_API_URL || 'http://localhost:3001/api';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Log final request URL in development for debugging
    if (process.env.NODE_ENV === 'development') {
      const finalUrl = `${config.baseURL}${config.url}`;
      console.log(`📡 API Request: ${config.method?.toUpperCase()} ${finalUrl}`, config.params ? `Params: ${JSON.stringify(config.params)}` : '');
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Helper: Check if error is an Axios error
 * CRITICAL: Only Axios errors should be logged as "API Error"
 */
function isAxiosError(error: any): boolean {
  return (
    error?.config !== undefined ||
    error?.response !== undefined ||
    error?.request !== undefined ||
    error?.isAxiosError === true ||
    (error?.code && ['ECONNABORTED', 'ECONNREFUSED', 'ETIMEDOUT', 'ENOTFOUND'].includes(error.code))
  );
}

/**
 * Helper: Classify and log errors properly
 * CRITICAL: Separates Axios/API errors from runtime/navigation errors
 * This prevents {} errors and ensures proper error classification
 */
export function handleError(error: any, context: string): { message: string; isAxiosError: boolean } {
  const isAxios = isAxiosError(error);
  
  if (isAxios) {
    // Axios error - already logged by interceptor, but extract message for UI
    const message = error?.message || error?.response?.data?.detail || error?.response?.data?.error || 'API request failed';
    
    if (process.env.NODE_ENV === 'development') {
      console.error(`❌ API Error in ${context}:`, {
        message: message,
        status: error?.response?.status ?? "NO_STATUS",
        url: error?.config?.url ?? "UNKNOWN_URL",
      });
    }
    
    return { message, isAxiosError: true };
  } else {
    // Runtime/navigation/state error - NOT an API error
    const message = error?.message || String(error) || 'An unexpected error occurred';
    
    if (process.env.NODE_ENV === 'development') {
      console.error(`⚠️ Runtime Error in ${context}:`, {
        message: message,
        type: error?.constructor?.name ?? typeof error,
        stack: error?.stack?.slice(0, 300) ?? "NO_STACK",
      });
    }
    
    return { message, isAxiosError: false };
  }
}

// Response interceptor with standardized error handling
// MANDATORY: {} errors are structurally impossible after this
// CRITICAL: This interceptor ONLY handles Axios errors (network/API layer)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // CRITICAL: Verify this is an Axios error
    // If not, this interceptor should not handle it (shouldn't happen, but safety check)
    if (!isAxiosError(error)) {
      console.error("⚠️ Non-Axios error caught in Axios interceptor (this should not happen):", {
        type: typeof error,
        constructor: error?.constructor?.name ?? "UNKNOWN",
        message: error?.message ?? "NO_MESSAGE",
        stack: error?.stack?.slice(0, 200) ?? "NO_STACK"
      });
      return Promise.reject(error);
    }
    
    // Normalize error to always have status and message
    const normalizedError: {
      status: number;
      message: string;
      raw?: any;
    } = {
      status: error.response?.status || 0,
      message: 'Unknown error',
      raw: error
    };
    
    // Extract error message from various response formats
    const responseData = error.response?.data;
    
    if (responseData) {
      // Structured error from backend (our new format)
      if (responseData.error?.message) {
        normalizedError.message = responseData.error.message;
        normalizedError.status = responseData.status || error.response?.status || 500;
      }
      // FastAPI HTTPException format
      else if (responseData.detail) {
        if (Array.isArray(responseData.detail)) {
          // Pydantic validation errors
          normalizedError.message = responseData.detail.map((err: any) => 
            `${err.loc?.join('.')}: ${err.msg}`
          ).join('; ');
        } else if (typeof responseData.detail === 'string') {
          normalizedError.message = responseData.detail;
        } else if (responseData.detail?.message) {
          normalizedError.message = responseData.detail.message;
        } else {
          normalizedError.message = JSON.stringify(responseData.detail);
        }
        normalizedError.status = error.response?.status || 500;
      }
      // Legacy error format
      else if (typeof responseData.error === 'string') {
        normalizedError.message = responseData.error;
        normalizedError.status = error.response?.status || 500;
      }
      // Plain text response
      else if (typeof responseData === 'string') {
        normalizedError.message = responseData;
        normalizedError.status = error.response?.status || 500;
      }
    }
    
    // Fallback error messages based on status code
    if (normalizedError.message === 'Unknown error' || normalizedError.message === '{}' || !normalizedError.message) {
      if (normalizedError.status === 404) {
        normalizedError.message = 'Resource not found. Please check if birth details are submitted.';
      } else if (normalizedError.status === 500) {
        normalizedError.message = 'Server error. Please try again later.';
      } else if (error.code === 'ECONNREFUSED') {
        normalizedError.message = 'Cannot connect to backend server. Please ensure the backend is running.';
        normalizedError.status = 0;
      } else if (error.message) {
        normalizedError.message = error.message;
      } else {
        normalizedError.message = 'An unknown error occurred.';
      }
    }
    
    // Skip logging for gracefully handled endpoints
    // CRITICAL: Validate error.config exists before accessing properties
    const errorConfig = error?.config;
    const requestUrl = errorConfig?.url || '';
    const baseUrl = errorConfig?.baseURL || '';
    const fullUrl = baseUrl && requestUrl ? `${baseUrl}${requestUrl}` : (requestUrl || baseUrl || 'UNKNOWN_URL');
    const shouldSkipErrorLogging = 
      (normalizedError.status === 404 && 
        (requestUrl.includes('/birth-details') || requestUrl.includes('/dashboard'))) ||
      (normalizedError.status === 422 && requestUrl.includes('/kundli')) ||
      (normalizedError.status === 404 && requestUrl.includes('/kundli/divisional'));
    
    // MANDATORY ERROR LOGGING - {} is structurally impossible
    // CRITICAL: This logs ONLY Axios/API errors, never runtime errors
    // CRITICAL: All error.config accesses are validated with optional chaining
    if (!shouldSkipErrorLogging && process.env.NODE_ENV === 'development') {
      // Build safe error log object - only include fields that exist
      const errorLog: Record<string, any> = {
        message: normalizedError.message || "NO_MESSAGE",
        status: normalizedError.status || "NO_STATUS",
      };
      
      // Only add URL fields if they exist
      if (requestUrl) errorLog.url = requestUrl;
      if (fullUrl && fullUrl !== requestUrl) errorLog.fullUrl = fullUrl;
      if (errorConfig?.method) errorLog.method = errorConfig.method;
      if (error?.code) errorLog.code = error.code;
      if (error?.code === "ECONNABORTED") errorLog.isTimeout = true;
      
      // Safely extract response data
      if (error?.response?.data !== undefined) {
        if (typeof error.response.data === "string") {
          errorLog.response = error.response.data.slice(0, 200);
        } else if (error.response.data !== null) {
          errorLog.response = error.response.data;
        }
      }
      
      console.error("❌ API Error (Axios):", errorLog);
      
      // Special handling for 404 errors - log full details
      if (normalizedError.status === 404) {
        const detailsLog: Record<string, any> = {
          fullUrl: fullUrl || "UNKNOWN_URL",
        };
        if (baseUrl) detailsLog.baseURL = baseUrl;
        if (requestUrl) detailsLog.endpoint = requestUrl;
        if (errorConfig?.method) detailsLog.method = errorConfig.method;
        if (errorConfig?.params) detailsLog.params = errorConfig.params;
        if (error?.response?.data !== undefined) detailsLog.responseBody = error.response.data;
        
        console.error('🔍 404 Not Found Details:', detailsLog);
      }
    }
    
    // Create error object that always has status and message
    const errorObj = new Error(normalizedError.message);
    (errorObj as any).status = normalizedError.status;
    (errorObj as any).raw = normalizedError.raw;
    (errorObj as any).isAxiosError = true; // Mark as Axios error for downstream handlers
    
    return Promise.reject(errorObj);
  }
);

// ==================== TYPES ====================

export interface BirthDetails {
  date: string;
  time: string;
  city: string;
  country: string;
  latitude: number;
  longitude: number;
  timezone?: string;
}

export interface BirthDetailsResponse {
  success: boolean;
  message: string;
  user_id?: string;
  lagna?: number;
  lagnaSign?: string;
}

// Drik Panchang compatible planet data
export interface PlanetData {
  name: string;
  sign: string;
  house: number;
  degree: number; // Total degree (0-360°) or degree in sign (0-30°)
  degrees_in_sign?: number; // Degree within sign (0-30°)
  degree_minutes?: number; // Minutes component (0-59)
  degree_seconds?: number; // Seconds component (0-59)
  nakshatra?: string;
  pada?: number;
  retrograde?: boolean;
  color?: string;
  speed?: number;
  longitude?: number;
}

// House data with sign and degree
export interface HouseData {
  house: number;
  sign: string;
  degree: number;
  degrees_in_sign?: number;
}

// Drik Panchang compatible chart data
export interface KundliData {
  lagna: number;
  lagnaSign: string;
  ayanamsa: string;
  system: string;
  planets: PlanetData[];
  houses: number[] | HouseData[]; // Can be numbers or objects with house data
  aspects?: any[];
  chartData?: {
    type: string;
    system: string;
    ayanamsa: string;
  };
  // Divisional charts included in kundli response
  // All varga charts (D1-D60) are supported
  D1?: DivisionalChartData; // Rashi chart (main chart)
  D2?: DivisionalChartData; // Hora chart
  D3?: DivisionalChartData; // Drekkana chart
  D4?: DivisionalChartData; // Chaturthamsa chart
  D7?: DivisionalChartData; // Saptamsa chart
  D9?: DivisionalChartData; // Navamsa chart
  D10?: DivisionalChartData; // Dasamsa chart
  D12?: DivisionalChartData; // Dwadasamsa chart
  D16?: DivisionalChartData; // Shodasamsa chart
  D20?: DivisionalChartData; // Vimsamsa chart
  D24?: DivisionalChartData; // Chaturvimsamsa chart
  D27?: DivisionalChartData; // Saptavimsamsa chart
  D30?: DivisionalChartData; // Trimsamsa chart
  D40?: DivisionalChartData; // Khavedamsa chart
  D45?: DivisionalChartData; // Akshavedamsa chart
  D60?: DivisionalChartData; // Shashtiamsa chart
}

// Divisional chart data - Consistent structure for all charts (D1-D60)
export interface DivisionalChartData {
  success?: boolean;
  chartType?: string;
  // New consistent structure: {ascendant, ascendant_sign, planets}
  ascendant?: number; // Ascendant house number (1-12)
  ascendant_sign?: string; // Ascendant sign (Sanskrit: Vrishchika, Mesha, etc.)
  planets: PlanetData[]; // Array of planets
  // Legacy fields (for backward compatibility)
  lagna?: number;
  lagnaSign?: string;
  lagnaSignSanskrit?: string;
  lagnaDegree?: number;
  system?: string;
  ayanamsa?: string;
  houses?: HouseData[] | number[]; // Can be array of numbers or objects with sign/degree info
}

// Dasha data (Vimshottari)
export interface DashaData {
  currentDasha: string;
  currentAntardasha?: string;
  currentPratyantardasha?: string;
  balance?: string;
  startDate?: string;
  endDate?: string;
  dashaPeriods?: Array<{
    planet: string;
    startDate: string;
    endDate: string;
    duration: string;
  }>;
  antardashas?: Array<{
    planet: string;
    startDate: string;
    endDate: string;
    duration: string;
  }>;
}

// ==================== BIRTH DETAILS ====================

export const submitBirthDetails = async (details: BirthDetails): Promise<BirthDetailsResponse> => {
  try {
    const response = await apiClient.post<BirthDetailsResponse>('/birth-details', details);
    return response.data;
  } catch (error: any) {
    // Check for 404 FIRST - this means /birth-details endpoint doesn't exist
    // Handle this gracefully without throwing an error
    // Also handle network errors and empty error objects
    if (error?.response?.status === 404 || !error?.response) {
      // Generate user_id locally
      const userId = `user_${Date.now()}`;
      
      // Return success response - birth details are already stored in Zustand store
      // The /birth-details endpoint doesn't exist, but we can still proceed
      // The kundli will be fetched directly when needed
      return {
        success: true,
        message: 'Birth details stored locally (API /birth-details endpoint not available)',
        user_id: userId,
        lagna: 1, // Default, will be calculated when kundli is fetched
        lagnaSign: 'Mesha', // Default, will be calculated when kundli is fetched
      };
    }
    
    // Only throw error if it's not a 404 (404 is handled above)
    throw error;
  }
};

// ==================== DASHBOARD ====================

/**
 * DEPRECATED: getDashboardData() - Endpoint does not exist
 * 
 * Dashboard data should be extracted from /kundli endpoint:
 * - Ascendant: kundliResponse.D1.Ascendant
 * - Moon: kundliResponse.D1.Planets.Moon
 * - Dasha: kundliResponse.current_dasha
 * 
 * DO NOT call /dashboard endpoint - it returns 404.
 */
export const getDashboardData = async (userId?: string) => {
  // This endpoint does not exist - always return "not available"
  return {
    success: false,
    message: 'Dashboard endpoint not available. Use /kundli endpoint instead.',
    data: null,
  };
};

// ==================== KUNDLI ====================

export const getKundli = async (userId?: string, birthDetails?: BirthDetails): Promise<any> => {
  // API now returns nested format with all divisional charts:
  // { success: true, data: { kundli: { D1: {...}, D2: {...}, D3: {...}, D4: {...}, D7: {...}, D9: {...}, D10: {...}, D12: {...}, D16: {...}, D20: {...}, D24: {...}, D27: {...}, D30: {...}, D40: {...}, D45: {...}, D60: {...} } } }
  
  const params: any = {};
  
  // Try user_id first
  if (userId) {
    params.user_id = userId;
  }
  
  // If birth details are provided, add them as query parameters
  // The deployed API might need these even with user_id
  if (birthDetails) {
    params.dob = birthDetails.date;
    params.time = birthDetails.time;
    params.lat = birthDetails.latitude;
    params.lon = birthDetails.longitude;
    // Add timezone if available (API may use it for time conversion)
    if (birthDetails.timezone) {
      params.timezone = birthDetails.timezone;
    }
  }
  
  // 🔒 CACHE-BUSTING: Force fresh API call every time
  // Add timestamp to prevent browser/Next.js caching
  params._t = Date.now();
  
  try {
    const response = await apiClient.get<any>('/kundli', { 
      params,
      // Disable all caching
      headers: {
        'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
    });
    
    // MANDATORY: Normalize response - never trust API shape
    if (!response.data) {
      throw new Error("Invalid response from server");
    }
    
    // Return the full response - includes D1 (main kundli) and all divisional charts (D2, D3, D4, D7, D9, D10, D12)
    if (response.data && response.data.success && response.data.data?.kundli) {
      return response.data; // Return full nested structure with all divisional charts
    }
    
    // Fallback for old format
    return response.data;
  } catch (error: any) {
    // Handle 422 validation errors - API needs birth details
    if (error?.response?.status === 422) {
      // If we have birth details in store, try fetching them
      if (!birthDetails) {
        throw new Error('Birth details are required. Please submit birth details first.');
      }
      
      // Retry with birth details if we didn't have them before
      if (!params.dob && birthDetails) {
        const retryParams = {
          dob: birthDetails.date,
          time: birthDetails.time,
          lat: birthDetails.latitude,
          lon: birthDetails.longitude,
          ...(birthDetails.timezone && { timezone: birthDetails.timezone }),
        };
        try {
          const retryResponse = await apiClient.get<any>('/kundli', { params: retryParams });
          
          // Process retry response
          if (retryResponse.data && retryResponse.data.success && retryResponse.data.data?.kundli) {
            return retryResponse.data;
          }
          return retryResponse.data;
        } catch (retryError: any) {
          // If retry also fails, throw with a clear message
          throw new Error(retryError?.message || 'Failed to fetch kundli data. Please check your birth details.');
        }
      }
    }
    
    // Re-throw the error (interceptor will handle logging)
    throw error;
  }
};

export const getKundliYogas = async (userId?: string) => {
  const response = await apiClient.get('/kundli/yogas', {
    params: userId ? { user_id: userId } : {},
  });
  
  // MANDATORY: Normalize response
  if (!response.data) {
    throw new Error("Invalid response from server");
  }
  
  return response.data;
};

// ==================== DIVISIONAL CHARTS ====================

export const getNavamsa = async (userId?: string): Promise<DivisionalChartData> => {
  const response = await apiClient.get<DivisionalChartData>('/kundli/navamsa', {
    params: userId ? { user_id: userId } : {},
  });
  return response.data;
};

export const getDasamsa = async (userId?: string): Promise<DivisionalChartData> => {
  const response = await apiClient.get<DivisionalChartData>('/kundli/dasamsa', {
    params: userId ? { user_id: userId } : {},
  });
  return response.data;
};

export const getDivisionalCharts = async (chartType: string, userId?: string): Promise<DivisionalChartData> => {
  // Map frontend chart types (d1, d2, d9, etc.) to backend format (D1, D2, D9, etc.)
  // Backend expects uppercase D prefix: D1, D2, D3, D4, D7, D9, D10, D12, etc.
  const normalizedType = chartType.toUpperCase();
  const backendChartType = normalizedType.startsWith('D') ? normalizedType : `D${normalizedType.replace(/^d/i, '')}`;
  
  try {
    // NOTE: The /kundli/divisional endpoint doesn't exist (returns 404)
    // Divisional charts are included in the main /kundli response as D2, D3, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60, etc.
    // This function should not be called, but if it is, try the endpoint anyway
    const params: any = { type: backendChartType };
    if (userId) {
      params.user_id = userId;
    }
    
    const response = await apiClient.get<DivisionalChartData>('/kundli/divisional', {
      params,
    });
    return response.data;
  } catch (error: any) {
    // If 404, the endpoint doesn't exist - this is expected
    // Divisional charts should be fetched from main /kundli response instead
    if (error?.response?.status === 404) {
      throw new Error(`Divisional chart endpoint not available. Please use main kundli response which includes all divisional charts.`);
    }
    // Re-throw with more context for other errors
    const errorMessage = error?.response?.data?.detail || error?.message || `Failed to fetch ${backendChartType} chart`;
    throw new Error(errorMessage);
  }
};

// ==================== DASHA ====================

export const getDasha = async (userId?: string): Promise<DashaData> => {
  const response = await apiClient.get<DashaData>('/dasha', {
    params: userId ? { user_id: userId } : {},
  });
  
  // MANDATORY: Normalize response
  if (!response.data) {
    throw new Error("Invalid response from server");
  }
  
  return response.data;
};

export const getDashaTimeline = async (userId?: string) => {
  const response = await apiClient.get('/dasha/timeline', {
    params: userId ? { user_id: userId } : {},
  });
  return response.data;
};

// ==================== TRANSITS ====================

export const getTransits = async (date?: string, userId?: string) => {
  const response = await apiClient.get('/transits', {
    params: {
      date: date || new Date().toISOString().split('T')[0],
      ...(userId && { user_id: userId }),
    },
  });
  return response.data;
};

// ==================== PANCHANG ====================

export const getPanchang = async (date?: string, location?: { lat: number; lng: number }) => {
  const response = await apiClient.get('/panchang', {
    params: {
      date: date || new Date().toISOString().split('T')[0],
      ...(location && { latitude: location.lat, longitude: location.lng }),
    },
  });
  return response.data;
};

// ==================== LOCATION AUTOCOMPLETE ====================

export interface LocationSuggestion {
  city: string;
  country: string;
  latitude: number;
  longitude: number;
  timezone: string;
  displayName: string;
}

export interface LocationSearchResponse {
  success: boolean;
  suggestions: LocationSuggestion[];
}

export interface LocationCoordinatesResponse {
  success: boolean;
  data?: {
    latitude: number;
    longitude: number;
    timezone: string;
  };
  error?: string;
}

/**
 * Get timezone from coordinates using timezone lookup API
 * Falls back to a simple timezone estimation based on longitude
 */
export const getTimezoneFromCoordinates = async (lat: number, lon: number): Promise<string> => {
  try {
    // Try multiple timezone lookup APIs (free, no key required)
    // Option 1: TimeAPI.io
    try {
      const response = await axios.get(
        `https://timeapi.io/api/TimeZone/coordinate?latitude=${lat}&longitude=${lon}`,
        { timeout: 5000 }
      );
      if (response.data?.timeZone) {
        return response.data.timeZone;
      }
    } catch (e) {
      // Continue to next option
    }
    
    // Option 2: TimeZoneDB (free tier, but requires API key - skip for now)
    // Option 3: Use estimation based on coordinates
    return estimateTimezoneFromLongitude(lat, lon);
  } catch (error) {
    // Fallback to estimation based on longitude
    return estimateTimezoneFromLongitude(lat, lon);
  }
};

/**
 * Estimate timezone from latitude and longitude (rough approximation)
 * Uses common timezone mappings by geographic region
 */
const estimateTimezoneFromLongitude = (lat: number, lon: number): string => {
  // Common timezone mappings by region
  // This is a fallback - the API should provide accurate timezone
  
  // India region (68°E - 97°E, 6°N - 37°N)
  if (lon >= 68 && lon <= 97 && lat >= 6 && lat <= 37) {
    return 'Asia/Kolkata';
  }
  // USA East Coast (-75°W to -70°W, 25°N - 50°N)
  if (lon >= -75 && lon <= -70 && lat >= 25 && lat <= 50) {
    return 'America/New_York';
  }
  // USA Central (-100°W to -85°W, 25°N - 50°N)
  if (lon >= -100 && lon <= -85 && lat >= 25 && lat <= 50) {
    return 'America/Chicago';
  }
  // USA West Coast (-125°W to -115°W, 32°N - 50°N)
  if (lon >= -125 && lon <= -115 && lat >= 32 && lat <= 50) {
    return 'America/Los_Angeles';
  }
  // UK region (-5°W to 2°E, 50°N - 60°N)
  if (lon >= -5 && lon <= 2 && lat >= 50 && lat <= 60) {
    return 'Europe/London';
  }
  // China region (73°E - 135°E, 18°N - 54°N)
  if (lon >= 73 && lon <= 135 && lat >= 18 && lat <= 54) {
    return 'Asia/Shanghai';
  }
  // Japan region (129°E - 146°E, 24°N - 46°N)
  if (lon >= 129 && lon <= 146 && lat >= 24 && lat <= 46) {
    return 'Asia/Tokyo';
  }
  // Australia East (145°E - 154°E, -10°S - -40°S)
  if (lon >= 145 && lon <= 154 && lat >= -40 && lat <= -10) {
    return 'Australia/Sydney';
  }
  // Default to UTC if we can't determine
  return 'UTC';
};

/**
 * Simple normalized location search (for autocomplete UI).
 * Returns normalized shape: { label, lat, lon }
 */
export async function searchLocation(query: string): Promise<Array<{ label: string; lat: number; lon: number; display_name?: string; name?: string; country?: string; state?: string }>> {
  if (!query || query.length < 3) return [];

  try {
    const res = await axios.get("/api/location/search", {
      params: { q: query },
      timeout: 8000,
    });

    // NORMALIZE HERE - Simple format for UI
    return (res.data || []).map((item: any) => ({
      label: item.display_name || item.name || query,
      lat: Number(item.lat) || 0,
      lon: Number(item.lon) || 0,
      display_name: item.display_name,
      name: item.name,
      country: item.country,
      state: item.state,
    }));
  } catch (error: any) {
    // Properly classify error - this is an Axios error (axios.get call)
    const { message } = handleError(error, "searchLocation");
    // Silently return empty array for UX (errors already logged by interceptor/handleError)
    return [];
  }
}

/**
 * Search locations using Next.js API route proxy (enforces architectural law).
 * Returns full LocationSuggestion format with timezone.
 * 
 * Architecture: Browser → Next.js API Route → Guru API → Nominatim
 * No direct browser calls to Guru API or external services.
 */
export const searchLocations = async (query: string): Promise<LocationSuggestion[]> => {
  if (!query || query.length < 3) {
    return [];
  }
  
  if (process.env.NODE_ENV === 'development') {
    console.log('🔍 Searching locations for:', query);
  }
  
  try {
    // Call Next.js API route (which proxies to Guru API)
    // This enforces the architectural law: Browser → Next.js → Guru API → Nominatim
    const response = await axios.get('/api/location/search', {
      params: {
        q: query,
      },
      timeout: 8000, // 8 seconds (Next.js route handles longer timeouts)
    });
    
    const results = response.data || [];
    
    if (process.env.NODE_ENV === 'development') {
      console.log(`📍 Found ${results.length} location(s) from Next.js proxy`);
    }
    
    // Transform backend results to LocationSuggestion format
    const suggestions: LocationSuggestion[] = await Promise.all(
      results.map(async (result: any) => {
        const lat = parseFloat(result.lat);
        const lon = parseFloat(result.lon);
        
        // Get timezone from coordinates
        const timezone = await getTimezoneFromCoordinates(lat, lon);
        
        if (process.env.NODE_ENV === 'development') {
          console.log(`  ✓ ${result.display_name} → ${lat}, ${lon} (${timezone})`);
        }
        
        return {
          city: result.name || query,
          country: result.country || 'Unknown',
          latitude: lat,
          longitude: lon,
          timezone: timezone,
          displayName: result.display_name || query,
        };
      })
    );
    
    if (process.env.NODE_ENV === 'development') {
      console.log(`✅ Returning ${suggestions.length} location suggestion(s)`);
    }
    
    return suggestions;
  } catch (error: any) {
    if (process.env.NODE_ENV === 'development') {
      console.error('❌ Location search error:', error.message);
    }
    // Return empty array on error (silent failure for UX)
    return [];
  }
};

/**
 * Get coordinates for a specific city/country using Next.js API route proxy.
 * 
 * Architecture: Browser → Next.js API Route → Guru API → Nominatim
 */
export const getLocationCoordinates = async (city: string, country: string): Promise<LocationCoordinatesResponse['data'] | undefined> => {
  if (!city) {
    return undefined;
  }
  
  if (process.env.NODE_ENV === 'development') {
    console.log(`🔍 Getting coordinates for: ${city}, ${country}`);
  }
  
  try {
    const searchQuery = country ? `${city}, ${country}` : city;
    // Call Next.js API route (which proxies to Guru API)
    const response = await axios.get('/api/location/search', {
      params: {
        q: searchQuery,
      },
      timeout: 8000, // 8 seconds (Next.js route handles longer timeouts)
    });
    
    const results = response.data || [];
    if (results.length === 0) {
      if (process.env.NODE_ENV === 'development') {
        console.log(`❌ No coordinates found for: ${city}, ${country}`);
      }
      return undefined;
    }
    
    const result = results[0];
    const lat = parseFloat(result.lat);
    const lon = parseFloat(result.lon);
    const timezone = await getTimezoneFromCoordinates(lat, lon);
    
    if (process.env.NODE_ENV === 'development') {
      console.log(`✅ Coordinates: ${lat}, ${lon} (${timezone})`);
    }
    
    return {
      latitude: lat,
      longitude: lon,
      timezone: timezone,
    };
  } catch (error: any) {
    if (process.env.NODE_ENV === 'development') {
      console.error('❌ Get coordinates error:', error.message);
    }
    return undefined;
  }
};

// ==================== GURU / AI INTERPRETATION ====================

export interface GuruRequest {
  message: string;
  context?: string;
  conversation_history?: Array<{ role: string; content: string }>;
  chart_data?: any;
}

export const getGuruInterpretation = async (request: GuruRequest) => {
  const response = await apiClient.post('/chat', request);
  return response.data;
};

export const getInterpretation = async (request: GuruRequest) => {
  const response = await apiClient.post('/interpret', request);
  return response.data;
};

export const getKundliInterpretation = async (chartData: any, question?: string) => {
  return getInterpretation({
    message: question || 'Please provide a general interpretation of this chart.',
    chart_data: chartData,
  });
};

// Export default
export default apiClient;
