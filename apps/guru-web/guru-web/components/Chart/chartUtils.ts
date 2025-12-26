/**
 * Chart Type Utilities
 * Single source of truth for determining chart types
 * 
 * 🔒 RENDERING CONTRACT - DO NOT CHANGE MATH
 * This file determines rendering behavior only.
 * 
 * DEGREE DISPLAY RULES:
 * • House charts (D1-D20): Show degrees for planets and Ascendant
 * • Sign charts (D24-D60): DO NOT show degrees (pure sign charts)
 */

/**
 * ASC (Ascendant) Shared Style Constants
 * 
 * CRITICAL: ASC must look identical across ALL charts (D1-D60, North & South)
 * - Same color as regular planets (blue, not gold/yellow)
 * - Same font size, weight, and style
 * - Used in: SouthIndianChart, NorthIndianChart, SouthIndianSignChart, NorthIndianSignChart
 */
export const ASC_STYLE = {
  // Text color - matches regular planet color (#3b82f6)
  fill: '#3b82f6',
  
  // Font styling - matches planet text
  fontSize: '12px',
  fontWeight: 700,
  fontFamily: 'sans-serif',
  
  // Circle styling - matches regular planet circles
  circleFill: 'rgba(59, 130, 246, 0.15)',
  circleStroke: 'rgba(59, 130, 246, 0.3)',
  circleStrokeWidth: '1',
  circleRadius: 11,
  
  // Label text (for D1-D20 separate label)
  labelFontSize: '12px',
  labelFontWeight: 700,
} as const;

/**
 * HOUSE-BASED CHARTS - Use SouthIndianChart or NorthIndianChart
 * These charts require 12 houses and SHOW DEGREES
 */
export const HOUSE_CHARTS = ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20"] as const;

/**
 * SIGN-BASED CHARTS - Use SouthIndianSignChart or NorthIndianSignChart
 * These charts have NO houses (pure sign charts) and HIDE DEGREES
 */
export const SIGN_CHARTS = ["D24", "D27", "D30", "D40", "D45", "D60"] as const;

/**
 * Determine if a chart type is a house-based chart
 * 
 * @param varga - Chart type string (e.g., "D1", "D9", "D24")
 * @returns true if house-based chart, false otherwise
 */
export function isHouseChart(varga: string | undefined): boolean {
  if (!varga) return false;
  return HOUSE_CHARTS.includes(varga.toUpperCase() as any);
}

/**
 * Determine if a chart type is a pure sign chart
 * 
 * @param varga - Chart type string (e.g., "D24", "D27")
 * @returns true if pure sign chart, false otherwise
 */
export function isSignChart(varga: string | undefined): boolean {
  if (!varga) return false;
  return SIGN_CHARTS.includes(varga.toUpperCase() as any);
}

