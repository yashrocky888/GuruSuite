/**
 * Graha Drishti (Planetary Aspects) Table Component
 * 
 * Displays Parāśari Graha Drishti aspects for ALL divisional charts (D1-D60).
 * 
 * 🔒 UI ONLY - NO ASTROLOGY CALCULATIONS
 * Uses aspects data directly from API response.
 * 
 * Table Columns:
 * 1. Planet (aspecting planet)
 * 2. Aspect (aspect type: 3rd, 4th, 5th, 7th, 8th, 9th, 10th)
 * 3. Aspected Planet (planet being aspected or "Nil")
 * 4. Aspected House (sign name and house number)
 */

'use client';

import React from 'react';

// Planet icons/symbols (matching PlanetDetailsTable)
const PLANET_SYMBOLS: { [key: string]: string } = {
  'Sun': '☉',
  'Moon': '☽',
  'Mars': '♂',
  'Mercury': '☿',
  'Jupiter': '♃',
  'Venus': '♀',
  'Saturn': '♄',
  'Rahu': '☊',
  'Ketu': '☋',
};

interface Aspect {
  from: string;
  aspect: string;
  to: string;
  aspected_house?: string; // Optional: sign name and house number (e.g., "Mithuna – 2nd house")
}

interface GrahaDrishtiTableProps {
  aspects: Aspect[];
}

export const GrahaDrishtiTable: React.FC<GrahaDrishtiTableProps> = ({
  aspects,
}) => {
  // If no aspects, render nothing
  if (!aspects || aspects.length === 0) {
    return null;
  }

  return (
    <div className="mt-6 overflow-x-auto">
      <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">
        Graha Drishti (Planetary Aspects)
      </h3>
      <div className="glass rounded-lg border border-white/20 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-white/5 dark:bg-gray-800/50">
            <tr>
              <th className="px-4 py-3 text-left font-semibold text-gray-700 dark:text-gray-300">
                Planet
              </th>
              <th className="px-4 py-3 text-left font-semibold text-gray-700 dark:text-gray-300">
                Aspect
              </th>
              <th className="px-4 py-3 text-left font-semibold text-gray-700 dark:text-gray-300">
                Aspected Planet
              </th>
              <th className="px-4 py-3 text-left font-semibold text-gray-700 dark:text-gray-300">
                Aspected House
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10 dark:divide-gray-700/50">
            {aspects.map((aspect, index) => (
              <tr
                key={`${aspect.from}-${aspect.aspect}-${aspect.to}-${index}`}
                className={index % 2 === 0 ? 'bg-white/2 dark:bg-gray-800/20' : 'bg-white/5 dark:bg-gray-800/30'}
              >
                <td className="px-4 py-3 text-gray-800 dark:text-gray-200">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{PLANET_SYMBOLS[aspect.from] || aspect.from.substring(0, 2)}</span>
                    <span className="font-medium">{aspect.from}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-gray-700 dark:text-gray-300 font-medium">
                  {aspect.aspect}
                </td>
                <td className="px-4 py-3 text-gray-800 dark:text-gray-200">
                  <div className="flex items-center gap-2">
                    {aspect.to !== "Nil" && (
                      <span className="text-lg">{PLANET_SYMBOLS[aspect.to] || aspect.to.substring(0, 2)}</span>
                    )}
                    <span className="font-medium">{aspect.to}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-gray-700 dark:text-gray-300">
                  {aspect.aspected_house || '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
