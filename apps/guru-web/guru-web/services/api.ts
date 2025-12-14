/**
 * API Service - Frontend API Client
 * Connects to Guru API backend (Python FastAPI)
 * Updated for Drik Panchang & JHORA compatibility
 */

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://guru-api-660206747784.us-central1.run.app';
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
    // Silent in production - only log in development if needed
    if (process.env.NODE_ENV === 'development') {
      // Optional: minimal logging for debugging
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor with better error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Special handling for 404 on specific endpoints
    // Skip all error logging - let the calling functions handle it gracefully
    const is404OnHandledEndpoint = error.response?.status === 404 && 
      (error.config?.url?.includes('/birth-details') || error.config?.url?.includes('/dashboard'));
    
    if (is404OnHandledEndpoint) {
      // Return the error as-is so calling functions can handle it
      // Don't log, transform, or throw here - just pass it through
      return Promise.reject(error);
    }
    
    // Handle Pydantic validation errors
    let errorMessage = 'Unknown error';
    if (error.response?.data?.detail) {
      if (Array.isArray(error.response.data.detail)) {
        // Pydantic validation errors
        const validationErrors = error.response.data.detail.map((err: any) => 
          `${err.loc?.join('.')}: ${err.msg}`
        ).join(', ');
        errorMessage = `Validation error: ${validationErrors}`;
      } else if (typeof error.response.data.detail === 'string') {
        errorMessage = error.response.data.detail;
      } else if (error.response.data.detail?.message) {
        errorMessage = error.response.data.detail.message;
      } else {
        errorMessage = JSON.stringify(error.response.data.detail);
      }
    } else if (error.response?.data?.error) {
      errorMessage = error.response.data.error;
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    // Ensure we always have an error message
    if (!errorMessage || errorMessage === '{}' || errorMessage === '') {
      if (error.response?.status === 404) {
        errorMessage = 'Resource not found. Please check if birth details are submitted.';
      } else if (error.response?.status === 500) {
        errorMessage = 'Server error. Please try again later.';
      } else if (error.code === 'ECONNREFUSED') {
        errorMessage = 'Cannot connect to backend server. Please ensure the backend is running.';
      } else if (error.message) {
        errorMessage = error.message;
      } else {
        errorMessage = 'An unknown error occurred.';
      }
    }
    
    // Skip logging for 404/422 on specific endpoints (handled gracefully)
    const requestUrl = error.config?.url || '';
    const shouldSkipErrorLogging = 
      (error.response?.status === 404 && 
        (requestUrl.includes('/birth-details') || requestUrl.includes('/dashboard'))) ||
      (error.response?.status === 422 && requestUrl.includes('/kundli'));
    
    // Only log errors that aren't handled gracefully and have meaningful data
    if (!shouldSkipErrorLogging) {
      // Build error summary only if we have meaningful data
      const errorSummary: any = {};
      if (error.config?.url) errorSummary.url = error.config.url;
      if (error.config?.method) errorSummary.method = error.config.method;
      if (error.response?.status) errorSummary.status = error.response.status;
      if (errorMessage && errorMessage !== '{}' && errorMessage !== 'Unknown error') {
        errorSummary.message = errorMessage;
      }
      if (error.code) errorSummary.code = error.code;
      
      // Skip logging for 404 on /kundli/divisional (endpoint doesn't exist, expected)
      const isDivisional404 = error?.response?.status === 404 && 
                               error?.config?.url?.includes('/kundli/divisional');
      
      // Only log if we have meaningful error information and it's not an expected 404
      if (Object.keys(errorSummary).length > 0 && !isDivisional404 && process.env.NODE_ENV === 'development') {
        console.error('API Error:', errorSummary);
      }
    }
    
    return Promise.reject(new Error(errorMessage));
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
  D1?: DivisionalChartData; // Rashi chart (main chart)
  D2?: DivisionalChartData; // Hora chart
  D3?: DivisionalChartData; // Drekkana chart
  D4?: DivisionalChartData; // Chaturthamsa chart
  D7?: DivisionalChartData; // Saptamsa chart
  D9?: DivisionalChartData; // Navamsa chart
  D10?: DivisionalChartData; // Dasamsa chart
  D12?: DivisionalChartData; // Dwadasamsa chart
}

// Divisional chart data - Consistent structure for all charts (D2, D3, D4, D7, D9, D10, D12)
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
    if (error?.response?.status === 404) {
      // Generate user_id locally
      const userId = `user_${Date.now()}`;
      
      // Return success response - birth details are already stored in Zustand store
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

export const getDashboardData = async (userId?: string) => {
  try {
    const response = await apiClient.get('/dashboard', {
      params: userId ? { user_id: userId } : {},
    });
    return response.data;
  } catch (error: any) {
    // Handle 404 gracefully - dashboard endpoint might not exist
    if (error?.response?.status === 404) {
      return {
        success: true,
        message: 'Dashboard data not available (endpoint not found)',
        data: {
          // Return default/empty dashboard structure
          summary: {},
          upcomingEvents: [],
          recentReadings: [],
        },
      };
    }
    // For other errors, throw to be handled by the page
    throw error;
  }
};

// ==================== KUNDLI ====================

export const getKundli = async (userId?: string, birthDetails?: BirthDetails): Promise<any> => {
  // API now returns nested format with all divisional charts:
  // { success: true, data: { kundli: { D1: {...}, D2: {...}, D3: {...}, D4: {...}, D7: {...}, D9: {...}, D10: {...}, D12: {...} } } }
  
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
  }
  
  try {
    const response = await apiClient.get<any>('/kundli', { params });
    
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
    // Divisional charts are included in the main /kundli response as D2, D3, D9, etc.
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

export const searchLocations = async (query: string): Promise<LocationSuggestion[]> => {
  if (!query || query.length < 2) {
    return [];
  }
  
  try {
    const response = await axios.get<LocationSearchResponse>(
      `${LOCATION_API_BASE_URL}/location/search?q=${encodeURIComponent(query)}`
    );
    return response.data.suggestions || [];
  } catch (error) {
    // Silently return empty array on error
    return [];
  }
};

export const getLocationCoordinates = async (city: string, country: string): Promise<LocationCoordinatesResponse['data'] | undefined> => {
  try {
    const response = await axios.get<LocationCoordinatesResponse>(
      `${LOCATION_API_BASE_URL}/location/coordinates?city=${encodeURIComponent(city)}&country=${encodeURIComponent(country)}`
    );
    return response.data.data;
  } catch (error) {
    // Silently return undefined on error
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
