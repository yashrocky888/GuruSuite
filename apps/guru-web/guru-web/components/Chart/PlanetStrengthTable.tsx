'use client';

/**
 * Planet Functional Strength Table (Admin-only)
 *
 * 🔒 RENDER-ONLY:
 * - Frontend must NOT calculate or interpret astrology
 * - Uses API data from planet_functional_strength as-is
 * - No predictions, no yoga logic, no numeric scores
 *
 * This table is intended for internal/admin inspection:
 * “Is this planet eligible to speak later?”
 */

import React from 'react';

type PlanetStrengthRecord = {
  dignity?: string;
  house_type?: string;
  association?: string[] | null;
  functional_strength?: string;
  can_deliver?: boolean;
  debilitated_friend?: boolean | 'neutral' | null;
  neecha_bhanga_possible?: boolean;
  neecha_bhanga_reason?: string | null;
  [key: string]: any;
};

export type PlanetStrengthTableProps = {
  strengthData: Record<string, PlanetStrengthRecord>;
};

// Simple render helper for booleans → "Yes"/"No"
const renderBool = (value: boolean | undefined | null): string => {
  if (value === true) return 'Yes';
  if (value === false) return 'No';
  return '-';
};

// Simple render helper for generic values
const renderValue = (value: any): string => {
  if (value === null || value === undefined || value === '') return '-';
  return String(value);
};

export const PlanetStrengthTable: React.FC<PlanetStrengthTableProps> = ({
  strengthData,
}) => {
  if (!strengthData || Object.keys(strengthData).length === 0) {
    return null;
  }

  const planets = Object.entries(strengthData);

  return (
    <div className="mt-6 overflow-x-auto">
      <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">
        Planet Functional Strength (Admin)
      </h3>
      <div className="glass rounded-lg border border-white/20 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-white/5 dark:bg-gray-800/50">
            <tr>
              <th className="px-4 py-3 text-left font-semibold text-gray-700 dark:text-gray-300">
                Planet
              </th>
              <th className="px-4 py-3 text-left font-semibold text-gray-700 dark:text-gray-300">
                Dignity
              </th>
              <th className="px-4 py-3 text-left font-semibold text-gray-700 dark:text-gray-300">
                House Type
              </th>
              <th className="px-4 py-3 text-left font-semibold text-gray-700 dark:text-gray-300">
                Association
              </th>
              <th className="px-4 py-3 text-left font-semibold text-gray-700 dark:text-gray-300">
                Functional Strength
              </th>
              <th className="px-4 py-3 text-left font-semibold text-gray-700 dark:text-gray-300">
                Can Deliver
              </th>
              <th className="px-4 py-3 text-left font-semibold text-gray-700 dark:text-gray-300">
                Debilitated Friend
              </th>
              <th className="px-4 py-3 text-left font-semibold text-gray-700 dark:text-gray-300">
                Neecha Bhanga Possible
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10 dark:divide-gray-700/50">
            {planets.map(([planetName, data]) => {
              const dignity = data.dignity;
              const houseType = data.house_type;
              const associationArray = Array.isArray(data.association)
                ? data.association
                : [];
              const association =
                associationArray.length > 0
                  ? associationArray.join(', ')
                  : '-';
              const functionalStrength = data.functional_strength;
              const canDeliver = data.can_deliver;
              const debilitatedFriend = data.debilitated_friend;
              const neechaPossible = data.neecha_bhanga_possible;

              return (
                <tr
                  key={planetName}
                  className="bg-white/2 dark:bg-gray-800/20"
                >
                  <td className="px-4 py-3 text-gray-800 dark:text-gray-200 font-medium">
                    {planetName}
                  </td>
                  <td className="px-4 py-3 text-gray-700 dark:text-gray-300">
                    {renderValue(dignity)}
                  </td>
                  <td className="px-4 py-3 text-gray-700 dark:text-gray-300">
                    {renderValue(houseType)}
                  </td>
                  <td className="px-4 py-3 text-gray-700 dark:text-gray-300">
                    {association}
                  </td>
                  <td className="px-4 py-3 text-gray-700 dark:text-gray-300">
                    {renderValue(functionalStrength)}
                  </td>
                  <td className="px-4 py-3 text-gray-700 dark:text-gray-300">
                    {renderBool(canDeliver)}
                  </td>
                  <td className="px-4 py-3 text-gray-700 dark:text-gray-300">
                    {renderValue(debilitatedFriend)}
                  </td>
                  <td className="px-4 py-3 text-gray-700 dark:text-gray-300">
                    {renderBool(neechaPossible)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

