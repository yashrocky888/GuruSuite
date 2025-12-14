/**
 * South Indian Chart Component
 * Fixed 4x4 grid layout - classic South Indian style
 */

'use client';

import React from 'react';
import { HouseData } from '../types/kundli';

interface SouthChartProps {
  houses: HouseData[];
}

/**
 * South Indian Chart Grid Layout
 * 
 * Row 1: [4][5][6][7]
 * Row 2: [3][ ][ ][8]
 * Row 3: [2][ ][ ][9]
 * Row 4: [1][12][11][10]
 * 
 * Signs are fixed in these positions
 * Houses rotate based on Lagna
 */
const SOUTH_POSITIONS: number[][] = [
  [4, 5, 6, 7],
  [3, 0, 0, 8],
  [2, 0, 0, 9],
  [1, 12, 11, 10],
];

export const SouthChart: React.FC<SouthChartProps> = ({ houses }) => {
  // Create a map for quick house lookup
  const houseByNumber = new Map(houses.map(h => [h.houseNumber, h]));

  return (
    <div className="south-chart-grid w-full flex justify-center">
      <div className="grid grid-cols-4 grid-rows-4 w-[420px] h-[420px] gap-1">
        {SOUTH_POSITIONS.flat().map((houseNumber, idx) => {
          if (houseNumber === 0) {
            return (
              <div
                key={idx}
                className="south-chart-empty opacity-0 pointer-events-none"
              />
            );
          }

          const house = houseByNumber.get(houseNumber);
          if (!house) {
            return (
              <div
                key={idx}
                className="south-chart-cell border-2 border-amber-300/80 rounded-lg p-2 bg-white/95 dark:bg-gray-900/95"
              >
                <div className="text-xs font-bold text-amber-600">{houseNumber}</div>
                <div className="text-xs text-gray-400">—</div>
              </div>
            );
          }

          const isLagna = houseNumber === 1;

          return (
            <div
              key={houseNumber}
              className={`
                south-chart-cell
                flex flex-col items-center justify-center
                border-2 rounded-lg p-2 min-h-[100px]
                bg-white/95 dark:bg-gray-900/95
                ${isLagna ? 'border-amber-500 shadow-lg' : 'border-amber-300/80'}
                hover:border-amber-400 transition-all duration-200
              `}
            >
              {/* House number */}
              <div className="text-xs font-bold text-amber-600 dark:text-amber-400 mb-1">
                {houseNumber}
              </div>

              {/* Sign name */}
              <div className="text-sm font-semibold text-orange-600 dark:text-orange-400 mb-1 text-center">
                {house.signName}
              </div>

              {/* Planet abbreviations */}
              {house.planets.length > 0 ? (
                <div className="text-xs text-blue-600 dark:text-blue-400 text-center leading-tight flex flex-wrap justify-center gap-x-1">
                  {house.planets.map((planet, pIdx) => (
                    <span key={pIdx} className="font-medium">
                      {planet}
                    </span>
                  ))}
                </div>
              ) : (
                <div className="text-xs text-gray-400 dark:text-gray-500 text-center">—</div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

