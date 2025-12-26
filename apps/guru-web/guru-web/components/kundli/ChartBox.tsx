/**
 * Chart Box Component
 * Wrapper for chart display with North/South toggle
 */

'use client';

import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { ArrowsRightLeftIcon } from '@heroicons/react/24/outline';
import { SouthChart } from './SouthChart';
import { NorthChart } from './NorthChart';
import { RawKundliData } from '../types/kundli';
import { ChartContainer } from '../Chart/ChartContainer';

interface ChartBoxProps {
  chartData: RawKundliData | null | undefined;
  chartType?: 'rasi' | 'navamsa' | 'dasamsa';
}

type ChartStyle = 'north' | 'south';

export const ChartBox: React.FC<ChartBoxProps> = ({ chartData, chartType = 'rasi' }) => {
  const [chartStyle, setChartStyle] = useState<ChartStyle>('south');

  // DEPRECATED: This component should use ChartContainer directly
  // ChartContainer handles API format with proper structure
  if (!chartData) {
    return (
      <div className="flex items-center justify-center h-[500px] glass rounded-xl border border-white/20">
        <p className="text-gray-500 dark:text-gray-400">No chart data available</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="glass rounded-xl p-6 border border-white/20"
    >
      {/* Chart Style Toggle */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
          {chartType === 'navamsa' ? 'Navamsa Chart (D9)' : 
           chartType === 'dasamsa' ? 'Dasamsa Chart (D10)' : 
           'Kundli Chart'}
        </h3>
        
        <div className="flex items-center space-x-3">
          <span className={`text-sm font-medium ${chartStyle === 'south' ? 'text-amber-600' : 'text-gray-500'}`}>
            South
          </span>
          <button
            onClick={() => setChartStyle(chartStyle === 'north' ? 'south' : 'north')}
            className="p-2 rounded-lg glass border border-white/20 hover:border-amber-500/50 transition-smooth"
            aria-label="Toggle chart style"
          >
            <ArrowsRightLeftIcon className="w-4 h-4 text-amber-600" />
          </button>
          <span className={`text-sm font-medium ${chartStyle === 'north' ? 'text-amber-600' : 'text-gray-500'}`}>
            North
          </span>
        </div>
      </div>

      {/* Chart Display Container */}
      <div className="w-full bg-gradient-to-br from-amber-50/30 to-orange-50/30 dark:from-amber-900/10 dark:to-orange-900/10 rounded-lg p-6 border border-amber-200/30 dark:border-amber-800/30 flex justify-center items-center min-h-[500px]">
        <ChartContainer chartData={chartData} chartType={chartType} />
      </div>

      {/* Chart Info */}
      <div className="mt-4 text-xs text-gray-600 dark:text-gray-400 text-center space-y-1">
        <p className="font-semibold">
          Lagna: {chartData?.lagnaSign || 'Mesha'} | Style: {chartStyle === 'north' ? 'North Indian (Diamond)' : 'South Indian (Rectangular)'}
        </p>
        <p>Vedic Sidereal System | Lahiri Ayanamsa | Text Only (No Symbols)</p>
      </div>
    </motion.div>
  );
};

