/**
 * API Service - Frontend API Client
 * Connects to Guru API backend (Python FastAPI)
 * Updated for Drik Panchang & JHORA compatibility
 */

import axios from 'axios';

// 🔒 CRITICAL: Use environment variable for API base URL
// Cloud Run URL: https://guru-api-660206747784.asia-south1.run.app
// Environment variable: NEXT_PUBLIC_API_BASE_URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://guru-api-660206747784.asia-south1.run.app/api/v1';

const LOCATION_API_BASE_URL = process.env.NEXT_PUBLIC_ASTRO_API_URL || 'http://localhost:3001/api';

// Create axios instance with default config
// 🔒 CRITICAL: Use environment-based baseURL (NOT hardcoded localhost)
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 2 minutes (predict endpoint can take 60–90s for OpenAI)
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
  name?: string;
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
  // 🔒 FIX: Skip /birth-details API call entirely - endpoint doesn't exist
  // The /birth-details endpoint doesn't exist in the backend API
  // Birth details are stored in Zustand store and used directly for kundli calculation
  // This prevents 404 errors in console and improves UX
  
  // Generate user_id locally (no backend storage needed)
  const userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  
  // Return success response immediately
  // Birth details are stored in Zustand store by the calling component
  // The kundli will be fetched directly using birth details when needed
  return {
    success: true,
    message: 'Birth details stored locally',
    user_id: userId,
    lagna: 1, // Default, will be calculated when kundli is fetched
    lagnaSign: 'Mesha', // Default, will be calculated when kundli is fetched
  };
  
  // OLD CODE (REMOVED - was causing 404 errors):
  // The /birth-details endpoint doesn't exist, so we skip the API call entirely
  // Instead, we generate a local user_id and return success immediately
  // Birth details are stored in Zustand store by the calling component
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
    // 🔒 DATE PRESERVATION: Treat date as pure string - NEVER parse or convert
    // Date must remain EXACTLY as user entered it (YYYY-MM-DD format)
    
    // 🔒 HARD ASSERTION: Date must be a string
    if (typeof birthDetails.date !== 'string') {
      console.error('❌ FATAL: birthDetails.date is not a string!', {
        type: typeof birthDetails.date,
        value: birthDetails.date,
      });
      throw new Error('Date must be a string - never use Date objects or parsed dates');
    }
    
    // 🔒 HARD ASSERTION: Validate date format (YYYY-MM-DD)
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(birthDetails.date)) {
      console.error('❌ FATAL: Invalid date format!', {
        date: birthDetails.date,
        expectedFormat: 'YYYY-MM-DD',
      });
      throw new Error(`Invalid date format: ${birthDetails.date}. Must be YYYY-MM-DD`);
    }
    
    // 🔒 INPUT VALIDATION: Preserve user-entered date and time exactly
    params.dob = birthDetails.date; // 🔒 PURE STRING ASSIGNMENT - NO PARSING, NO CONVERSION
    params.time = birthDetails.time; // 🔒 PURE STRING ASSIGNMENT - NO PARSING, NO CONVERSION
    
    params.lat = birthDetails.latitude;
    params.lon = birthDetails.longitude;
    
    // 🔒 TIMEZONE FIX: Ensure Indian locations use Asia/Kolkata, not UTC
    let timezone = birthDetails.timezone;
    
    // Validate: If country is India and timezone is UTC, fix it
    if (birthDetails.country && 
        (birthDetails.country.toLowerCase().includes('india') || 
         birthDetails.country.toLowerCase() === 'in') &&
        (!timezone || timezone === 'UTC' || timezone === 'utc')) {
      console.warn('⚠️ Indian location detected with UTC timezone. Fixing to Asia/Kolkata.');
      timezone = 'Asia/Kolkata';
    }
    
    // Default to Asia/Kolkata if timezone is missing (safer than UTC)
    if (!timezone) {
      console.warn('⚠️ Timezone missing. Defaulting to Asia/Kolkata.');
      timezone = 'Asia/Kolkata';
    }
    
    params.timezone = timezone;
    
    // 🧪 INPUT DEBUG: Log exact params being sent to API
    console.log('🧪 API INPUT DEBUG — Birth Details Sent to Backend:', {
      dob: params.dob,
      time: params.time,
      lat: params.lat,
      lon: params.lon,
      timezone: params.timezone,
      country: birthDetails.country,
      city: birthDetails.city,
      // 🔒 VERIFICATION: Show that date is unchanged
      dateUnchanged: params.dob === birthDetails.date,
      originalDate: birthDetails.date,
      sentDate: params.dob,
    });
    
    // 🔒 HARD ASSERTION: Validate date/time are unchanged (byte-for-byte)
    if (params.dob !== birthDetails.date) {
      console.error('❌ FATAL: Date was modified before API call!', {
        original: birthDetails.date,
        modified: params.dob,
        originalType: typeof birthDetails.date,
        modifiedType: typeof params.dob,
      });
      throw new Error('Date modification detected - this is a bug');
    }
    
    // 🔒 HARD ASSERTION: Validate timezone for Indian locations
    if (birthDetails.country && 
        (birthDetails.country.toLowerCase().includes('india') || 
         birthDetails.country.toLowerCase() === 'in') &&
        params.timezone === 'UTC') {
      console.error('❌ FATAL: Indian location with UTC timezone!', {
        country: birthDetails.country,
        timezone: params.timezone,
      });
      throw new Error('Indian location must use Asia/Kolkata timezone, not UTC');
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
    
    // 🔒 CRITICAL FIX: Backend returns charts directly at top level: { D1: {...}, D2: {...}, ... }
    // NOT nested format: { success: true, data: { kundli: { D1: {...} } } }
    // Check for direct format first (production API format)
    if (response.data && typeof response.data === 'object' && 'D1' in response.data) {
      // Direct format: { D1: {...}, D2: {...}, D3: {...}, ... }
      return response.data;
    }
    
    // Check for nested format (legacy/alternative format)
    if (response.data && response.data.success && response.data.data?.kundli) {
      return response.data.data.kundli; // Extract kundli object from nested structure
    }
    
    // Check for alternative nested format: { data: { D1: {...}, D2: {...} } }
    if (response.data && response.data.data && typeof response.data.data === 'object' && 'D1' in response.data.data) {
      return response.data.data;
    }
    
    // Fallback: return as-is
    return response.data;
  } catch (error: any) {
    // Handle 404 - user_id not found in database, try with birth details
    if (error?.response?.status === 404 && userId && birthDetails) {
      console.warn('⚠️ User ID not found in database, retrying with birth details...');
      const retryParams = {
        dob: birthDetails.date,
        time: birthDetails.time,
        lat: birthDetails.latitude,
        lon: birthDetails.longitude,
        ...(birthDetails.timezone && { timezone: birthDetails.timezone }),
        _t: Date.now(),
      };
      try {
        const retryResponse = await apiClient.get<any>('/kundli', { 
          params: retryParams,
          headers: {
            'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
          },
        });
        
        // Normalize retry response (same logic as above)
        if (retryResponse.data && typeof retryResponse.data === 'object' && 'D1' in retryResponse.data) {
          return retryResponse.data;
        }
        if (retryResponse.data && retryResponse.data.success && retryResponse.data.data?.kundli) {
          return retryResponse.data.data.kundli;
        }
        if (retryResponse.data && retryResponse.data.data && typeof retryResponse.data.data === 'object' && 'D1' in retryResponse.data.data) {
          return retryResponse.data.data;
        }
        return retryResponse.data;
      } catch (retryError: any) {
        throw new Error(retryError?.message || 'Failed to fetch kundli data. Please check your birth details.');
      }
    }
    
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
          _t: Date.now(),
        };
        try {
          const retryResponse = await apiClient.get<any>('/kundli', { 
            params: retryParams,
            headers: {
              'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
              'Pragma': 'no-cache',
              'Expires': '0',
            },
          });
          
          // Normalize retry response (same logic as above)
          if (retryResponse.data && typeof retryResponse.data === 'object' && 'D1' in retryResponse.data) {
            return retryResponse.data;
          }
          if (retryResponse.data && retryResponse.data.success && retryResponse.data.data?.kundli) {
            return retryResponse.data.data.kundli;
          }
          if (retryResponse.data && retryResponse.data.data && typeof retryResponse.data.data === 'object' && 'D1' in retryResponse.data.data) {
            return retryResponse.data.data;
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
  // DEPRECATED: Use getVimshottariDasha instead
  // This function is kept for backward compatibility
  const response = await apiClient.get('/dasha/timeline', {
    params: userId ? { user_id: userId } : {},
  });
  return response.data;
};

export const getVimshottariDasha = async (
  date: string,
  time: string,
  lat: number,
  lon: number,
  tz: string
) => {
  const response = await apiClient.get('/dasha/vimshottari', {
    params: {
      date,
      time,
      lat,
      lon,
      tz,
    },
  });
  return response.data;
};

export const getShadbala = async (
  date: string,
  time: string,
  lat: number,
  lon: number,
  timezone?: string
) => {
  // Shadbala endpoint is at /strength/shadbala (not under /api/v1)
  const baseURL = process.env.NEXT_PUBLIC_API_BASE_URL?.replace('/api/v1', '') || 'https://guru-api-660206747784.asia-south1.run.app';
  const response = await axios.get(`${baseURL}/strength/shadbala`, {
    params: {
      dob: date,
      time,
      lat,
      lon,
      ...(timezone ? { timezone } : {}),
    },
    timeout: 30000,
  });
  return response.data;
};

export const getYogas = async (
  date: string,
  time: string,
  lat: number,
  lon: number,
  timezone?: string
) => {
  // Yoga endpoint is at /strength/yogas (not under /api/v1)
  const baseURL = process.env.NEXT_PUBLIC_API_BASE_URL?.replace('/api/v1', '') || 'https://guru-api-660206747784.asia-south1.run.app';
  const response = await axios.get(`${baseURL}/strength/yogas`, {
    params: {
      dob: date,
      time,
      lat,
      lon,
      ...(timezone ? { timezone } : {}),
    },
    timeout: 30000,
  });
  return response.data;
};

export const getYogasTimeline = async (
  date: string,
  time: string,
  lat: number,
  lon: number,
  timezone?: string
) => {
  // Yoga timeline endpoint is at /strength/yogas/timeline (not under /api/v1)
  const baseURL = process.env.NEXT_PUBLIC_API_BASE_URL?.replace('/api/v1', '') || 'https://guru-api-660206747784.asia-south1.run.app';
  const response = await axios.get(`${baseURL}/strength/yogas/timeline`, {
    params: {
      dob: date,
      time,
      lat,
      lon,
      ...(timezone ? { timezone } : {}),
    },
    timeout: 30000,
  });
  return response.data;
};

// ==================== TRANSITS / YOGA ACTIVATION ====================

/** Yoga Transit Activation — backend-only. Call ONLY this for yoga activation on /transits. */
export const getYogaActivation = async (
  params: {
    dob: string;
    time: string;
    lat: number;
    lon: number;
    timezone?: string;
    mode?: 'summary' | 'forecast';
    years?: number;
  }
): Promise<{ transit_activation: any[]; forecast: any[]; error: string | null }> => {
  const response = await apiClient.get('/yoga-activation', {
    params: {
      dob: params.dob,
      time: params.time,
      lat: params.lat,
      lon: params.lon,
      timezone: params.timezone || 'Asia/Kolkata',
      mode: params.mode || 'summary',
      ...(params.mode === 'forecast' && params.years != null && { years: params.years }),
    },
  });
  return response.data;
};

/** Guru Context AI prediction — POST /api/v1/predict. Returns guidance + technical breakdown. */
export const getPredict = async (
  birthDetails: BirthDetails,
  timescale: 'daily' | 'monthly' | 'yearly' = 'daily',
  seekerName?: string
): Promise<{ message?: string; guidance?: string; structured?: Record<string, string>; context: any; technical_breakdown: any }> => {
  const name = seekerName ?? birthDetails.name ?? 'Seeker';
  const t0 = Date.now();
  if (process.env.NODE_ENV === 'development') {
    console.log('[getPredict] Request starting', { timescale });
  }
  const response = await apiClient.post('/predict', {
    birth_details: {
      name,
      dob: birthDetails.date,
      time: birthDetails.time,
      lat: birthDetails.latitude,
      lon: birthDetails.longitude,
      timezone: birthDetails.timezone || 'Asia/Kolkata',
    },
    timescale,
  }, { timeout: 120000 });
  const elapsed = Date.now() - t0;
  if (process.env.NODE_ENV === 'development') {
    console.log('[getPredict] Response received in', elapsed, 'ms');
  }
  return response.data;
};

/** Current planetary transit positions (requires birth details). Uses GET /api/v1/all. */
export const getTransitAll = async (params: {
  dob: string;
  time: string;
  lat: number;
  lon: number;
  timezone?: string;
  current_date?: string;
  current_time?: string;
}): Promise<any> => {
  const response = await apiClient.get('/all', {
    params: {
      dob: params.dob,
      time: params.time,
      lat: params.lat,
      lon: params.lon,
      timezone: params.timezone || 'Asia/Kolkata',
      ...(params.current_date && { current_date: params.current_date }),
      ...(params.current_time && { current_time: params.current_time }),
    },
  });
  return response.data;
};

export const getTransits = async (date?: string, userId?: string) => {
  const response = await apiClient.get('/transits', {
    params: {
      date: date || new Date().toISOString().split('T')[0],
      ...(userId && { user_id: userId }),
    },
  });
  return response.data;
};

export const getKundliTransits = async (
  userId?: string, 
  datetime?: string,
  lat?: number, 
  lon?: number, 
  timezone?: string
): Promise<any> => {
  const response = await apiClient.get('/kundli/transits', {
    params: {
      ...(userId && { user_id: userId }),
      ...(datetime && { datetime }),
      ...(lat !== undefined && { lat }),
      ...(lon !== undefined && { lon }),
      ...(timezone && { timezone }),
    },
  });
  return response.data;
};

// ==================== PANCHANG ====================

export const getPanchang = async (date?: string, location?: { lat: number; lng: number }) => {
  // DEPRECATED: Use getPanchanga instead with proper timezone support
  // This function is kept for backward compatibility but uses the new endpoint
  const dateStr = date || new Date().toISOString().split('T')[0];
  const lat = location?.lat || 12.9716; // Default: Bangalore
  const lon = location?.lng || 77.5946;
  const tz = 'Asia/Kolkata'; // Default timezone
  
  const response = await apiClient.get('/panchanga', {
    params: {
      date: dateStr,
      lat,
      lon,
      tz,
    },
  });
  return response.data;
};

export const getPanchanga = async (date: string, lat: number, lon: number, tz: string) => {
  const response = await apiClient.get('/panchanga', {
    params: {
      date,
      lat,
      lon,
      tz,
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
    const makeRequest = async () =>
      axios.get("/api/location/search", {
        params: { q: query },
        timeout: 15000, // 15 seconds
      });

    let res;
    let attempt = 0;

    while (true) {
      try {
        res = await makeRequest();
        break;
      } catch (error: any) {
        const isTimeout =
          error?.code === "ECONNABORTED" ||
          /timeout/i.test(error?.message || "");
        if (isTimeout && attempt === 0) {
          attempt += 1;
          console.warn("⚠️ Location search timeout, retrying once", {
            query,
          });
          continue;
        }
        // Properly classify error - this is an Axios error (axios.get call)
        const { message } = handleError(error, "searchLocation");
        console.warn("⚠️ Location search failed, returning empty results", {
          query,
          message,
        });
        return [];
      }
    }

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
    // Fallback safety (should rarely be hit)
    const { message } = handleError(error, "searchLocation.fallback");
    console.warn("⚠️ Location search fallback error, returning empty results", {
      query,
      message,
    });
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
    const makeRequest = async () =>
      axios.get('/api/location/search', {
        params: {
          q: query,
        },
        timeout: 15000, // 15 seconds (Next.js route handles longer timeouts)
      });

    let response;
    let attempt = 0;
    while (true) {
      try {
        response = await makeRequest();
        break;
      } catch (error: any) {
        const isTimeout =
          error?.code === "ECONNABORTED" ||
          /timeout/i.test(error?.message || "");
        if (isTimeout && attempt === 0) {
          attempt += 1;
          console.warn("⚠️ Location search proxy timeout, retrying once", {
            query,
          });
          continue;
        }
        console.warn('⚠️ Location search proxy failed, returning empty suggestions', {
          query,
          message: error?.message || 'Unknown error',
        });
        return [];
      }
    }
    
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
    console.warn('⚠️ Location search unexpected error, returning empty suggestions', {
      query,
      message: error?.message || 'Unknown error',
    });
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
    const makeRequest = async () =>
      axios.get('/api/location/search', {
        params: {
          q: searchQuery,
        },
        timeout: 15000, // 15 seconds (Next.js route handles longer timeouts)
      });

    let response;
    let attempt = 0;
    while (true) {
      try {
        response = await makeRequest();
        break;
      } catch (error: any) {
        const isTimeout =
          error?.code === "ECONNABORTED" ||
          /timeout/i.test(error?.message || "");
        if (isTimeout && attempt === 0) {
          attempt += 1;
          console.warn("⚠️ Get coordinates timeout, retrying once", {
            searchQuery,
          });
          continue;
        }
        console.warn('⚠️ Get coordinates failed, returning undefined', {
          searchQuery,
          message: error?.message || 'Unknown error',
        });
        return undefined;
      }
    }
    
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
    console.warn('⚠️ Get coordinates unexpected error, returning undefined', {
      city,
      country,
      message: error?.message || 'Unknown error',
    });
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
