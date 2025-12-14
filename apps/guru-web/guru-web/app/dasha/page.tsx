'use client';

/**
 * Dasha Timeline Page
 * Displays planetary periods timeline
 */

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ClockIcon } from '@heroicons/react/24/outline';
import { FadeIn } from '@/frontend/animations';
import { getDashaTimeline } from '@/services/api';
import DashaTimeline from '@/components/DashaTimeline';

export default function DashaPage() {
  const [periods, setPeriods] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDasha = async () => {
      try {
        // Get userId from store if available
        const { useBirthStore } = await import('@/store/useBirthStore');
        const userId = useBirthStore.getState().userId;
        
        const data = await getDashaTimeline(userId || undefined);
        setPeriods(data.periods || data || []);
      } catch (err: any) {
        setError(err.message || 'Failed to load dasha timeline');
      } finally {
        setLoading(false);
      }
    };

    fetchDasha();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading dasha timeline...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50/30 to-blue-50/30 dark:from-slate-900 dark:via-purple-900/20 dark:to-blue-900/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <FadeIn>
          <div className="text-center mb-12">
            <div className="w-16 h-16 mx-auto rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center mb-4">
              <ClockIcon className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-2">
              Dasha Timeline
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Planetary periods and their influence on your life
            </p>
          </div>
        </FadeIn>

        {error && (
          <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 mb-6">
            {error}
          </div>
        )}

        <DashaTimeline periods={periods} />
      </div>
    </div>
  );
}
