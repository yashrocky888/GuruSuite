/**
 * Core Type Definitions for Astrology Engine
 */

export interface BirthData {
  name?: string;
  date: string; // YYYY-MM-DD or DD/MM/YYYY
  time: string; // HH:MM or HH:MM AM/PM
  city: string; // Required - will be used to fetch coordinates
  country: string; // Required - will be used to fetch coordinates
  latitude?: number; // Optional - will be auto-fetched from city/country if not provided
  longitude?: number; // Optional - will be auto-fetched from city/country if not provided
  timezone?: string; // Optional - will be auto-fetched from city/country if not provided
}

export interface ParsedBirthData {
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  second: number;
  latitude: number;
  longitude: number;
  timezone: string;
  julianDay: number;
  localSiderealTime: number;
}

export interface PlanetPosition {
  planet: string;
  longitude: number; // 0-360 degrees
  latitude: number;
  distance: number;
  speed: number;
  retrograde: boolean;
  sign: string;
  signNumber: number;
  degree: number; // Degree within sign (0-30)
  nakshatra: string;
  pada: number; // 1-4
  nakshatraLord: string;
  combust?: boolean;
}

export interface HouseCusp {
  houseNumber: number;
  longitude: number;
  sign: string;
  signNumber: number;
  degree: number;
}

export interface ChartData {
  birthData: ParsedBirthData;
  planets: PlanetPosition[];
  houses: HouseCusp[];
  lagna: {
    longitude: number;
    sign: string;
    signNumber: number;
    degree: number;
  };
}

export interface RashiChart {
  houses: Array<{
    houseNumber: number;
    sign: string;
    signNumber: number;
    planets: Array<{
      name: string;
      degree: number;
      nakshatra: string;
      pada: number;
    }>;
  }>;
}

export interface DivisionalChart {
  chartType: string; // D1, D9, etc.
  houses: Array<{
    houseNumber: number;
    sign: string;
    signNumber: number;
    planets: Array<{
      name: string;
      degree: number;
    }>;
  }>;
}

export interface AstroCalculationRequest {
  name?: string;
  dob: string;
  tob: string;
  city: string;
  country: string;
  system?: 'lahiri' | 'raman' | 'kp';
  houseSystem?: 'placidus' | 'whole-sign';
}

export interface AstroCalculationResponse {
  birthData: ParsedBirthData;
  planets: PlanetPosition[];
  houses: HouseCusp[];
  lagna: {
    longitude: number;
    sign: string;
    signNumber: number;
    degree: number;
  };
  rashiChartNorth: RashiChart;
  rashiChartSouth: RashiChart;
  navamsaChart?: DivisionalChart;
}

