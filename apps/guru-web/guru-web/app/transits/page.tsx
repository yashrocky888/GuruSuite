'use client';

/**
 * Transits Page
 * Displays current planetary transits
 */

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ChartBarIcon } from '@heroicons/react/24/outline';
import { FadeIn, SlideUp } from '@/frontend/animations';
import { getTransits } from '@/services/api';
import VedicTransits from '@/components/VedicTransits';
import DataTable from '@/components/DataTable';

export default function TransitsPage() {
  const [transits, setTransits] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTransits = async () => {
      try {
        const data = await getTransits();
        setTransits(data.transits || data || []);
      } catch (err: any) {
        setError(err.message || 'Failed to load transits');
      } finally {
        setLoading(false);
      }
    };

    fetchTransits();
  }, []);

  const transitColumns = [
    { key: 'planet', label: 'Planet' },
    { key: 'sign', label: 'Sign' },
    { key: 'degree', label: 'Degree' },
    { key: 'house', label: 'House' },
    { key: 'speed', label: 'Speed' },
  ];

  const tableData = transits.map((transit) => ({
    planet: transit.planet,
    sign: transit.sign,
    degree: `${transit.degree}°`,
    house: transit.house,
    speed: transit.speed || '-',
  }));

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading transits...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50/30 to-blue-50/30 dark:from-slate-900 dark:via-purple-900/20 dark:to-blue-900/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <FadeIn>
          <div className="text-center mb-12">
            <div className="w-16 h-16 mx-auto rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center mb-4">
              <ChartBarIcon className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent mb-2">
              Current Transits
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Planetary positions and their current influence
            </p>
          </div>
        </FadeIn>

        {error && (
          <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 mb-6">
            {error}
          </div>
        )}

        {/* Vedic Transits */}
        <SlideUp delay={0.2}>
          <div className="mb-8">
            <VedicTransits transits={transits} />
          </div>
        </SlideUp>

        {/* Transit Table */}
        {tableData.length > 0 && (
          <SlideUp delay={0.4}>
            <DataTable
              columns={transitColumns}
              data={tableData}
              title="Transit Details"
            />
          </SlideUp>
        )}
      </div>
    </div>
  );
}

