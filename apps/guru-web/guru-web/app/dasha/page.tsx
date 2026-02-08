'use client';

/**
 * Dasha Timeline Page
 * Displays Vimshottari Dasha periods (Mahadasha, Antardasha, Pratyantar)
 * Render-only - No calculations, No AI
 */

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ClockIcon, ChevronDownIcon, ChevronRightIcon } from '@heroicons/react/24/outline';
import { FadeIn, SlideUp } from '@/frontend/animations';
import { getVimshottariDasha } from '@/services/api';
import { useBirthStore } from '@/store/useBirthStore';
import { useMaxLoadTime } from '@/hooks/useMaxLoadTime';

interface Mahadasha {
  planet: string;
  start: string;
  end: string;
}

interface Antardasha {
  planet: string;
  start: string;
  end: string;
}

interface Pratyantar {
  planet: string;
  start: string;
  end: string;
}

interface DashaData {
  current_dasha: {
    mahadasha: string;
    antardasha: string;
    pratyantar: string | null;
    start: string;
    end: string;
  };
  mahadashas: Mahadasha[];
  antardashas: Record<string, Antardasha[]>;
  pratyantardashas: Record<string, Pratyantar[]>;
}

export default function DashaPage() {
  const { birthDetails, hasHydrated } = useBirthStore();
  const [dashaData, setDashaData] = useState<DashaData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedMahadashas, setExpandedMahadashas] = useState<Set<string>>(new Set());
  const [expandedAntardashas, setExpandedAntardashas] = useState<Set<string>>(new Set());

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
    // 🔒 RACE CONDITION FIX: Client-side only
    if (typeof window === 'undefined') return;

    // 🔒 RACE CONDITION FIX: Hydration complete
    if (!hasHydrated) return;

    const fetchDasha = async () => {
      try {
        setLoading(true);
        setError(null);

        if (!birthDetails) {
          throw new Error('Birth details not available');
        }

        // Parse birth date and time
        const birthDate = birthDetails.date || '';
        const birthTime = birthDetails.time || '00:00';
        const lat = birthDetails.latitude || 0;
        const lon = birthDetails.longitude || 0;
        const tz = birthDetails.timezone || 'Asia/Kolkata';

        if (!birthDate) {
          throw new Error('Birth date is required');
        }

        const data = await getVimshottariDasha(birthDate, birthTime, lat, lon, tz);

        // 🔒 HARD FAILSAFE: Validate data
        if (!data) {
          throw new Error("API returned null or undefined response");
        }

        setDashaData(data);
      } catch (err: any) {
        console.error("🔍 DASHA FETCH ERROR", err);
        setError(err.message || 'Failed to load dasha timeline');
      } finally {
        setLoading(false);
      }
    };

    fetchDasha();
  }, [birthDetails, hasHydrated]);

  const toggleMahadasha = (planet: string) => {
    const newExpanded = new Set(expandedMahadashas);
    if (newExpanded.has(planet)) {
      newExpanded.delete(planet);
      // Also collapse all antardashas for this mahadasha
      const newAntardashaExpanded = new Set(expandedAntardashas);
      dashaData?.antardashas[planet]?.forEach((ad) => {
        const key = `${planet}-${ad.planet}`;
        newAntardashaExpanded.delete(key);
      });
      setExpandedAntardashas(newAntardashaExpanded);
    } else {
      newExpanded.add(planet);
    }
    setExpandedMahadashas(newExpanded);
  };

  const toggleAntardasha = (mahaPlanet: string, antaraPlanet: string) => {
    const key = `${mahaPlanet}-${antaraPlanet}`;
    const newExpanded = new Set(expandedAntardashas);
    if (newExpanded.has(key)) {
      newExpanded.delete(key);
    } else {
      newExpanded.add(key);
    }
    setExpandedAntardashas(newExpanded);
  };

  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return dateStr;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-purple-50/30 to-blue-50/30 dark:from-slate-900 dark:via-purple-900/20 dark:to-blue-900/20">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading dasha timeline...</p>
          <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">This will timeout after 8 seconds</p>
        </div>
      </div>
    );
  }

  // 🔒 HARD FAILSAFE: Show error if no data
  if (error && !dashaData) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-purple-50/30 to-blue-50/30 dark:from-slate-900 dark:via-purple-900/20 dark:to-blue-900/20">
        <div className="text-center max-w-md">
          <div className="p-6 rounded-lg bg-red-500/10 border border-red-500/20">
            <p className="text-red-600 dark:text-red-400">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!dashaData) {
    return null;
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
              Vimshottari Dasha
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

        {/* Current Dasha */}
        {dashaData.current_dasha && (
          <SlideUp delay={0.1}>
            <div className="mb-8 glass rounded-xl p-6 border border-white/20">
              <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">
                Current Dasha
              </h2>
              <div className="space-y-2">
                <div className="text-lg font-medium text-gray-800 dark:text-gray-200">
                  {dashaData.current_dasha.mahadasha} Mahadasha
                  {dashaData.current_dasha.antardasha && (
                    <> – {dashaData.current_dasha.antardasha} Antardasha</>
                  )}
                  {dashaData.current_dasha.pratyantar && (
                    <> – {dashaData.current_dasha.pratyantar} Pratyantar</>
                  )}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {formatDate(dashaData.current_dasha.start)} – {formatDate(dashaData.current_dasha.end)}
                </div>
              </div>
            </div>
          </SlideUp>
        )}

        {/* Mahadasha Table */}
        <SlideUp delay={0.2}>
          <div className="mb-8 glass rounded-xl p-6 border border-white/20">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">
              Mahadasha Timeline
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/20">
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-700 dark:text-gray-300">Mahadasha</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-700 dark:text-gray-300">Start</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-700 dark:text-gray-300">End</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-700 dark:text-gray-300"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/10">
                  {dashaData.mahadashas.map((maha, index) => {
                    const isExpanded = expandedMahadashas.has(maha.planet);
                    const antardashas = dashaData.antardashas[maha.planet] || [];
                    const isCurrent = dashaData.current_dasha.mahadasha === maha.planet;

                    return (
                      <React.Fragment key={index}>
                        <tr
                          className={`hover:bg-white/5 transition-colors cursor-pointer ${isCurrent ? 'bg-purple-500/10' : ''}`}
                          onClick={() => toggleMahadasha(maha.planet)}
                        >
                          <td className="px-4 py-3 text-gray-800 dark:text-gray-200 font-medium">
                            {maha.planet}
                          </td>
                          <td className="px-4 py-3 text-gray-600 dark:text-gray-400">
                            {formatDate(maha.start)}
                          </td>
                          <td className="px-4 py-3 text-gray-600 dark:text-gray-400">
                            {formatDate(maha.end)}
                          </td>
                          <td className="px-4 py-3">
                            {isExpanded ? (
                              <ChevronDownIcon className="w-5 h-5 text-gray-400" />
                            ) : (
                              <ChevronRightIcon className="w-5 h-5 text-gray-400" />
                            )}
                          </td>
                        </tr>
                        {isExpanded && antardashas.length > 0 && (
                          <tr>
                            <td colSpan={4} className="px-4 py-4 bg-white/5">
                              <div className="ml-4">
                                <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                                  Antardashas
                                </h3>
                                <table className="w-full">
                                  <thead>
                                    <tr className="border-b border-white/10">
                                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-600 dark:text-gray-400">Antardasha</th>
                                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-600 dark:text-gray-400">Start</th>
                                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-600 dark:text-gray-400">End</th>
                                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-600 dark:text-gray-400"></th>
                                    </tr>
                                  </thead>
                                  <tbody className="divide-y divide-white/5">
                                    {antardashas.map((antara, adIndex) => {
                                      const key = `${maha.planet}-${antara.planet}`;
                                      const isAntaraExpanded = expandedAntardashas.has(key);
                                      const pratyantardashas = dashaData.pratyantardashas[key] || [];
                                      const isCurrentAntara = dashaData.current_dasha.antardasha === antara.planet && isCurrent;

                                      return (
                                        <React.Fragment key={adIndex}>
                                          <tr
                                            className={`hover:bg-white/5 transition-colors cursor-pointer ${isCurrentAntara ? 'bg-purple-500/10' : ''}`}
                                            onClick={(e) => {
                                              e.stopPropagation();
                                              toggleAntardasha(maha.planet, antara.planet);
                                            }}
                                          >
                                            <td className="px-3 py-2 text-sm text-gray-700 dark:text-gray-300">
                                              {antara.planet}
                                            </td>
                                            <td className="px-3 py-2 text-sm text-gray-600 dark:text-gray-400">
                                              {formatDate(antara.start)}
                                            </td>
                                            <td className="px-3 py-2 text-sm text-gray-600 dark:text-gray-400">
                                              {formatDate(antara.end)}
                                            </td>
                                            <td className="px-3 py-2">
                                              {pratyantardashas.length > 0 && (
                                                isAntaraExpanded ? (
                                                  <ChevronDownIcon className="w-4 h-4 text-gray-400" />
                                                ) : (
                                                  <ChevronRightIcon className="w-4 h-4 text-gray-400" />
                                                )
                                              )}
                                            </td>
                                          </tr>
                                          {isAntaraExpanded && pratyantardashas.length > 0 && (
                                            <tr>
                                              <td colSpan={4} className="px-3 py-3 bg-white/5">
                                                <div className="ml-4">
                                                  <h4 className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2">
                                                    Pratyantar Dashas
                                                  </h4>
                                                  <div className="space-y-1">
                                                    {pratyantardashas.map((pratyantar, pdIndex) => (
                                                      <div
                                                        key={pdIndex}
                                                        className="text-xs text-gray-500 dark:text-gray-500 flex justify-between"
                                                      >
                                                        <span>{pratyantar.planet}</span>
                                                        <span>{formatDate(pratyantar.start)} – {formatDate(pratyantar.end)}</span>
                                                      </div>
                                                    ))}
                                                  </div>
                                                </div>
                                              </td>
                                            </tr>
                                          )}
                                        </React.Fragment>
                                      );
                                    })}
                                  </tbody>
                                </table>
                              </div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </SlideUp>
      </div>
    </div>
  );
}
