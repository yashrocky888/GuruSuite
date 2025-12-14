'use client';

/**
 * Guru Page
 * AI-powered astrological interpretations
 * Calls backend API for AI interpretation
 */

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { SparklesIcon } from '@heroicons/react/24/outline';
import { FadeIn } from '@/frontend/animations';
import { useKundliStore } from '@/store/useKundliStore';
import GuruReading from '@/components/GuruReading';
import { getKundli } from '@/services/api';

export default function GuruPage() {
  const { kundliData, setKundliData } = useKundliStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchKundli = async () => {
      try {
        if (!kundliData) {
          const data = await getKundli();
          setKundliData(data);
        }
      } catch (error) {
        console.error('Failed to fetch kundli:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchKundli();
  }, [kundliData, setKundliData]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50/30 to-blue-50/30 dark:from-slate-900 dark:via-purple-900/20 dark:to-blue-900/20">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <FadeIn>
          <div className="text-center mb-12">
            <div className="w-16 h-16 mx-auto rounded-full bg-gradient-to-br from-amber-500 to-yellow-500 flex items-center justify-center mb-4 spiritual-glow">
              <SparklesIcon className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-amber-600 to-yellow-600 bg-clip-text text-transparent mb-2">
              Guru's Wisdom
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Get AI-powered interpretations of your astrological chart
            </p>
          </div>
        </FadeIn>

        <GuruReading chartData={kundliData} />
      </div>
    </div>
  );
}

