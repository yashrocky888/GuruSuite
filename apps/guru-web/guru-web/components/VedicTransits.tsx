'use client';

/**
 * Vedic Transits Component
 * Displays planetary transits in Vedic format (table/list)
 * NO circular/wheel formats - Vedic only
 */

import { motion } from 'framer-motion';
import { ChartBarIcon } from '@heroicons/react/24/outline';
import DataTable from './DataTable';

interface Transit {
  planet: string;
  sign: string;
  degree: number;
  house: number;
  speed?: string;
}

interface VedicTransitsProps {
  transits: Transit[];
}

// Vedic Rashi names
const VEDIC_RASHIS = [
  'Mesha', 'Vrishabha', 'Mithuna', 'Karka',
  'Simha', 'Kanya', 'Tula', 'Vrishchika',
  'Dhanu', 'Makara', 'Kumbha', 'Meena'
];

export default function VedicTransits({ transits }: VedicTransitsProps) {
  if (!transits || transits.length === 0) {
    return (
      <div className="glass rounded-xl p-8 border border-white/20">
        <p className="text-gray-500 dark:text-gray-400 text-center">No transit data available</p>
      </div>
    );
  }

  const transitColumns = [
    { 
      key: 'planet', 
      label: 'Planet',
      render: (value: string) => (
        <span className="font-semibold text-amber-600">{value}</span>
      )
    },
    { 
      key: 'sign', 
      label: 'Rashi',
      render: (value: string) => (
        <span className="text-orange-600">{value}</span>
      )
    },
    { 
      key: 'degree', 
      label: 'Degree',
      render: (value: number) => `${value.toFixed(2)}°`
    },
    { 
      key: 'house', 
      label: 'House',
      render: (value: number) => (
        <span className="font-medium text-blue-600">House {value}</span>
      )
    },
    { 
      key: 'speed', 
      label: 'Speed',
      render: (value: string) => value || '-'
    },
  ];

  const tableData = transits.map((transit) => ({
    planet: transit.planet,
    sign: transit.sign,
    degree: transit.degree,
    house: transit.house,
    speed: transit.speed || '-',
  }));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-xl border border-white/20 overflow-hidden"
    >
      <div className="px-6 py-4 border-b border-white/10 bg-gradient-to-r from-amber-500/10 to-orange-500/10">
        <div className="flex items-center">
          <ChartBarIcon className="w-6 h-6 text-amber-600 mr-2" />
          <h3 className="text-xl font-bold text-gray-800 dark:text-gray-200">
            Current Transits (Vedic)
          </h3>
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Planetary positions in Vedic sidereal system
        </p>
      </div>
      
      <DataTable
        columns={transitColumns}
        data={tableData}
      />
    </motion.div>
  );
}

