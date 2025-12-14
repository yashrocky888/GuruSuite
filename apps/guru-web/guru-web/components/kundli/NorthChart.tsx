/**
 * North Indian Chart Component
 * True diamond-style layout - classic North Indian Kundli
 */

'use client';

import React from 'react';
import { HouseData } from '../types/kundli';

interface NorthChartProps {
  houses: HouseData[];
}

/**
 * North Indian Diamond Chart Layout
 * 
 *        1
 *   12      2
 * 11         3
 *   10      4
 *        5
 *    9      6
 *  8         7
 * 
 * Houses positioned in diamond pattern
 */
const HOUSE_POSITIONS: Record<number, { top: string; left: string }> = {
  1: { top: '0%', left: '50%' },      // Top center
  2: { top: '15%', left: '75%' },      // Top right
  3: { top: '35%', left: '90%' },      // Right
  4: { top: '55%', left: '75%' },      // Bottom right
  5: { top: '70%', left: '50%' },     // Bottom center
  6: { top: '55%', left: '25%' },     // Bottom left
  7: { top: '35%', left: '10%' },     // Left
  8: { top: '15%', left: '25%' },     // Top left
  9: { top: '45%', left: '35%' },     // Inner bottom left
  10: { top: '45%', left: '65%' },    // Inner bottom right
  11: { top: '25%', left: '35%' },    // Inner top left
  12: { top: '25%', left: '65%' },    // Inner top right
};

export const NorthChart: React.FC<NorthChartProps> = ({ houses }) => {
  // Create a map for quick house lookup
  const houseByNumber = new Map(houses.map(h => [h.houseNumber, h]));

  return (
    <div className="north-chart-container relative w-full flex justify-center">
      <div className="relative w-[500px] h-[500px]">
        {houses.map((house) => {
          const pos = HOUSE_POSITIONS[house.houseNumber];
          if (!pos) return null;

          const isLagna = house.houseNumber === 1;

          return (
            <div
              key={house.houseNumber}
              className="north-chart-diamond absolute"
              style={{
                top: pos.top,
                left: pos.left,
                transform: 'translate(-50%, -50%) rotate(45deg)',
                width: house.houseNumber <= 8 ? '100px' : '80px',
                height: house.houseNumber <= 8 ? '100px' : '80px',
              }}
            >
              <div
                className={`
                  w-full h-full
                  border-2 rounded-lg
                  bg-white/95 dark:bg-gray-900/95
                  flex flex-col items-center justify-center
                  ${isLagna ? 'border-amber-500 shadow-lg' : 'border-amber-300/80'}
                  hover:border-amber-400 transition-all duration-200
                `}
              >
                <div
                  className="flex flex-col items-center justify-center w-full h-full p-1"
                  style={{
                    transform: 'rotate(-45deg)',
                  }}
                >
                  {/* House number */}
                  <div className="text-xs font-bold text-amber-600 dark:text-amber-400 mb-0.5">
                    {house.houseNumber}
                  </div>

                  {/* Sign name */}
                  <div className="text-xs font-semibold text-orange-600 dark:text-orange-400 mb-0.5 text-center leading-tight">
                    {house.signName}
                  </div>

                  {/* Planet abbreviations */}
                  {house.planets.length > 0 ? (
                    <div className="text-[10px] text-blue-600 dark:text-blue-400 text-center leading-tight flex flex-wrap justify-center gap-x-0.5">
                      {house.planets.map((planet, pIdx) => (
                        <span key={pIdx} className="font-medium">
                          {planet}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <div className="text-[10px] text-gray-400 dark:text-gray-500 text-center">—</div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

