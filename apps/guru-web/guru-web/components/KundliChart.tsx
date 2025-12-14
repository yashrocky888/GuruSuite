/**
 * Kundli Chart Component - Main Entry Point
 */

'use client';

import React from 'react';
import { ChartContainer } from './Chart/ChartContainer';

interface KundliChartProps {
  chartData: any;
  lagna?: number;
  chartType?: 'rasi' | 'navamsa' | 'dasamsa';
}

export default function KundliChart(props: KundliChartProps) {
  return <ChartContainer chartData={props.chartData} chartType={props.chartType} />;
}
