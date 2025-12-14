/**
 * Validate Birth Data
 */

import { BirthData } from '../../types';

export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

export function validateBirthData(birthData: BirthData): ValidationResult {
  const errors: string[] = [];

  // Validate date
  if (!birthData.date || birthData.date.trim() === '') {
    errors.push('Date is required');
  } else {
    const dateRegex1 = /^\d{4}-\d{2}-\d{2}$/; // YYYY-MM-DD
    const dateRegex2 = /^\d{2}\/\d{2}\/\d{4}$/; // DD/MM/YYYY
    
    if (!dateRegex1.test(birthData.date) && !dateRegex2.test(birthData.date)) {
      errors.push('Invalid date format. Use YYYY-MM-DD or DD/MM/YYYY');
    }
  }

  // Validate time
  if (!birthData.time || birthData.time.trim() === '') {
    errors.push('Time is required');
  } else {
    const timeRegex1 = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$/; // 24-hour
    const timeRegex2 = /^([0-1]?[0-9]):[0-5][0-9](:[0-5][0-9])?\s*(AM|PM)$/i; // 12-hour
    
    if (!timeRegex1.test(birthData.time) && !timeRegex2.test(birthData.time)) {
      errors.push('Invalid time format. Use HH:MM or HH:MM AM/PM');
    }
  }

  // Validate location
  if (!birthData.city || birthData.city.trim() === '') {
    errors.push('City is required');
  }

  if (!birthData.country || birthData.country.trim() === '') {
    errors.push('Country is required');
  }

  // Note: Latitude and longitude are now automatically fetched from city/country
  // They are optional in the input and will be auto-populated
  // Only validate if manually provided (for edge cases)
  if (birthData.latitude !== undefined && (birthData.latitude < -90 || birthData.latitude > 90)) {
    errors.push('Latitude must be between -90 and 90');
  }

  if (birthData.longitude !== undefined && (birthData.longitude < -180 || birthData.longitude > 180)) {
    errors.push('Longitude must be between -180 and 180');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

