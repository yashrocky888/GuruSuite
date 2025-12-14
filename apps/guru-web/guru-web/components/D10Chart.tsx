'use client';

/**
 * Dasamsa Chart (D10) Component
 * Vedic Divisional Chart - Career & Profession
 * Uses same Vedic layout system as main Kundli
 */

import KundliChart from './KundliChart';

interface D10ChartProps {
  chartData: any;
  lagna?: number;
}

export default function D10Chart({ chartData, lagna = 1 }: D10ChartProps) {
  return (
    <KundliChart 
      chartData={chartData} 
      lagna={lagna}
      chartType="dasamsa"
    />
  );
}

