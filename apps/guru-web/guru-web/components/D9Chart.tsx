'use client';

/**
 * Navamsa Chart (D9) Component
 * Vedic Divisional Chart - Marriage & Relationships
 * Uses same Vedic layout system as main Kundli
 */

import KundliChart from './KundliChart';

interface D9ChartProps {
  chartData: any;
  lagna?: number;
}

export default function D9Chart({ chartData, lagna = 1 }: D9ChartProps) {
  return (
    <KundliChart 
      chartData={chartData} 
      lagna={lagna}
      chartType="navamsa"
    />
  );
}

