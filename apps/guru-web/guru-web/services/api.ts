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

// Response interceptor with standardized error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
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
    const requestUrl = error.config?.url || '';
    const shouldSkipErrorLogging = 
      (normalizedError.status === 404 && 
        (requestUrl.includes('/birth-details') || requestUrl.includes('/dashboard'))) ||
      (normalizedError.status === 422 && requestUrl.includes('/kundli')) ||
      (normalizedError.status === 404 && requestUrl.includes('/kundli/divisional'));
    
    // Log errors in development (with structured format)
    if (!shouldSkipErrorLogging && process.env.NODE_ENV === 'development') {
      console.error('API Error:', {
        url: error.config?.url,
        method: error.config?.method,
        status: normalizedError.status,
        message: normalizedError.message,
        code: error.code
      });
    }
    
    // Create error object that always has status and message
    const errorObj = new Error(normalizedError.message);
    (errorObj as any).status = normalizedError.status;
    (errorObj as any).raw = normalizedError.raw;
    
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
