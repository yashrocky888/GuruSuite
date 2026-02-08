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
import { useBirthStore } from '@/store/useBirthStore';
import GuruReading from '@/components/GuruReading';
import { getKundli } from '@/services/api';
import apiClient from '@/services/api';
import { useMaxLoadTime } from '@/hooks/useMaxLoadTime';

export default function GuruPage() {
  const { kundliData, setKundliData } = useKundliStore();
  const { hasHydrated } = useBirthStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 🔒 MAX LOAD TIME: Auto-stop spinner after 8 seconds
  useMaxLoadTime({
    loading,
    setLoading,
    maxTime: 8000,
    onTimeout: () => {
      setError('Loading took too long. Please try again.');
    },
  });

  useEffect(() => {
    // 🔒 RACE CONDITION FIX 1: Client-side only
    if (typeof window === 'undefined') return;

    // 🔒 RACE CONDITION FIX 2: Hydration complete
    if (!hasHydrated) return;

    // 🔒 RACE CONDITION FIX 3: Prevent duplicate calls
    if (loading && kundliData) return;

    // 🔒 RACE CONDITION FIX 4: Ensure API client is ready
    if (!apiClient || !apiClient.defaults?.baseURL) {
      console.warn('⚠️ API client not ready, waiting...');
      return;
    }

    const fetchKundli = async () => {
      try {
        setLoading(true);
        setError(null);
        if (!kundliData) {
          const data = await getKundli();
          // 🔒 HARD FAILSAFE: Validate data
          if (!data) {
            throw new Error("API returned null or undefined response");
          }
          setKundliData(data);
        }
      } catch (error: any) {
        console.error('Failed to fetch kundli:', error);
        setError(error?.message || 'Failed to load kundli data');
      } finally {
        setLoading(false);
      }
    };

    fetchKundli();
  }, [kundliData, setKundliData, hasHydrated, loading]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
          <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">This will timeout after 8 seconds</p>
        </div>
      </div>
    );
  }

  // 🔒 HARD FAILSAFE: Show error state
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="p-6 rounded-lg bg-red-500/10 border border-red-500/20">
            <p className="text-red-600 dark:text-red-400">{error}</p>
          </div>
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

