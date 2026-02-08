/**
 * API Configuration
 */

// CANONICAL API URL - asia-south1 region (DO NOT CHANGE)
const DEPLOYED_API_URL = 'https://guru-api-660206747784.asia-south1.run.app';

export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_URL || `${DEPLOYED_API_URL}/api/v1`,
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second
};

export const API_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
};

