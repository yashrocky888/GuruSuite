/**
 * Kundli Chart Component - Main Entry Point
 */

'use client';

import React from 'react';
import { ChartContainer } from './Chart/ChartContainer';

interface KundliChartProps {
  chartData: any;
  lagna?: number;
  chartType?: 'rasi' | 'navamsa' | 'dasamsa' | 'D1';
  planetFunctionalStrength?: Record<string, any>;
}

export default function KundliChart(props: KundliChartProps) {
  // 🧪 PROP FLOW DEBUG (TEMP - VERIFY PROP PASSING)
  if (props.chartType === 'D1') {
    console.log('🧪 KundliChart - D1 PROP FLOW', {
      hasPlanetFunctionalStrength: !!props.planetFunctionalStrength,
      planetFunctionalStrengthType: typeof props.planetFunctionalStrength,
      planetFunctionalStrengthKeys: props.planetFunctionalStrength ? Object.keys(props.planetFunctionalStrength) : [],
      planetFunctionalStrengthSample: props.planetFunctionalStrength ? Object.entries(props.planetFunctionalStrength).slice(0, 2) : [],
    });
  }
  
  return (
    <ChartContainer
      chartData={props.chartData}
      chartType={props.chartType}
      planetFunctionalStrength={props.planetFunctionalStrength}
    />
  );
}
