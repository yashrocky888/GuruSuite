/**
 * Parse Birth Data
 * Handles date/time parsing and conversion to Julian Day
 */

import moment from 'moment-timezone';
import { BirthData, ParsedBirthData } from '../../types';

export function parseBirthData(birthData: BirthData): ParsedBirthData {
  // Parse date (handle both formats)
  let dateMoment: moment.Moment;
  
  if (birthData.date.includes('/')) {
    // DD/MM/YYYY format
    const parts = birthData.date.split('/');
    if (parts.length === 3) {
      const [day, month, year] = parts.map(Number);
      dateMoment = moment({ year, month: month - 1, day });
    } else {
      throw new Error('Invalid date format. Use DD/MM/YYYY or YYYY-MM-DD');
    }
  } else if (birthData.date.includes('-')) {
    // YYYY-MM-DD format
    dateMoment = moment(birthData.date, 'YYYY-MM-DD');
  } else {
    throw new Error('Invalid date format. Use DD/MM/YYYY or YYYY-MM-DD');
  }

  if (!dateMoment.isValid()) {
    throw new Error('Invalid date');
  }

  // Parse time
  let hour: number, minute: number, second: number = 0;
  const timeStr = birthData.time.trim().toUpperCase();
  const isPM = timeStr.includes('PM');
  const isAM = timeStr.includes('AM');
  
  const timeOnly = timeStr.replace(/[AP]M/g, '').trim();
  const timeParts = timeOnly.split(':');
  
  if (timeParts.length >= 2) {
    hour = parseInt(timeParts[0], 10);
    minute = parseInt(timeParts[1], 10);
    second = timeParts[2] ? parseInt(timeParts[2], 10) : 0;
  } else {
    throw new Error('Invalid time format. Use HH:MM or HH:MM:SS');
  }

  // Convert to 24-hour format
  if (isPM && hour !== 12) {
    hour += 12;
  } else if (isAM && hour === 12) {
    hour = 0;
  }

  // Set time on date
  dateMoment.hour(hour).minute(minute).second(second);

  // Get timezone
  let timezone = birthData.timezone;
  if (!timezone && birthData.city && birthData.country) {
    // Try to get timezone from city/country
    timezone = getTimezoneFromLocation(birthData.city, birthData.country);
  }
  if (!timezone) {
    // Default to UTC if not found
    timezone = 'UTC';
  }

  // Convert to timezone
  const tzMoment = dateMoment.tz(timezone);

  // Get coordinates
  const latitude = birthData.latitude ?? 0;
  const longitude = birthData.longitude ?? 0;

  // Calculate Julian Day
  const julianDay = calculateJulianDay(
    tzMoment.year(),
    tzMoment.month() + 1,
    tzMoment.date(),
    tzMoment.hour(),
    tzMoment.minute(),
    tzMoment.second()
  );

  // Calculate Local Sidereal Time
  const localSiderealTime = calculateLocalSiderealTime(
    julianDay,
    longitude,
    tzMoment.hour(),
    tzMoment.minute(),
    tzMoment.second()
  );

  return {
    year: tzMoment.year(),
    month: tzMoment.month() + 1,
    day: tzMoment.date(),
    hour: tzMoment.hour(),
    minute: tzMoment.minute(),
    second: tzMoment.second(),
    latitude,
    longitude,
    timezone,
    julianDay,
    localSiderealTime,
  };
}

/**
 * Get timezone from city and country
 * Simplified - in production use proper geocoding API
 */
function getTimezoneFromLocation(city: string, country: string): string {
  // Common timezone mappings
  const timezoneMap: Record<string, string> = {
    'india': 'Asia/Kolkata',
    'bangalore': 'Asia/Kolkata',
    'mumbai': 'Asia/Kolkata',
    'delhi': 'Asia/Kolkata',
    'chennai': 'Asia/Kolkata',
    'kolkata': 'Asia/Kolkata',
    'hyderabad': 'Asia/Kolkata',
    'pune': 'Asia/Kolkata',
    'usa': 'America/New_York',
    'uk': 'Europe/London',
    'london': 'Europe/London',
  };

  const key = `${city.toLowerCase()}_${country.toLowerCase()}`;
  const cityKey = city.toLowerCase();
  const countryKey = country.toLowerCase();

  return timezoneMap[cityKey] || timezoneMap[countryKey] || 'UTC';
}

/**
 * Calculate Julian Day Number
 */
function calculateJulianDay(
  year: number,
  month: number,
  day: number,
  hour: number,
  minute: number,
  second: number
): number {
  if (month <= 2) {
    year -= 1;
    month += 12;
  }

  const a = Math.floor(year / 100);
  const b = 2 - a + Math.floor(a / 4);
  
  const dayFraction = (hour + minute / 60 + second / 3600) / 24;
  
  const jd = Math.floor(365.25 * (year + 4716)) +
    Math.floor(30.6001 * (month + 1)) +
    day + dayFraction + b - 1524.5;

  return jd;
}

/**
 * Calculate Local Sidereal Time
 */
function calculateLocalSiderealTime(
  julianDay: number,
  longitude: number,
  hour: number,
  minute: number,
  second: number
): number {
  const T = (julianDay - 2451545.0) / 36525.0;
  
  // Greenwich Mean Sidereal Time
  const GMST = 280.46061837 + 360.98564736629 * (julianDay - 2451545.0) +
    0.000387933 * T * T - T * T * T / 38710000.0;
  
  // Local Sidereal Time = GMST + longitude
  const LST = (GMST + longitude) % 360;
  
  return LST < 0 ? LST + 360 : LST;
}

