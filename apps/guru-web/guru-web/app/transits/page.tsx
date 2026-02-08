'use client';

/**
 * Transits Page
 * Current planetary transits only. Transit Activation of Yogas lives on Dashboard only (no duplicate).
 */

import { useEffect, useState } from 'react';
import { ChartBarIcon } from '@heroicons/react/24/outline';
import { FadeIn, SlideUp } from '@/frontend/animations';
import { getTransitAll } from '@/services/api';
import VedicTransits from '@/components/VedicTransits';
import DataTable from '@/components/DataTable';
import { useMaxLoadTime } from '@/hooks/useMaxLoadTime';
import { useBirthStore } from '@/store/useBirthStore';

export default function TransitsPage() {
  const { birthDetails, hasHydrated } = useBirthStore();
  const [transits, setTransits] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useMaxLoadTime({
    loading,
    setLoading,
    maxTime: 8000,
    onTimeout: () => setError('Loading took too long. Please try again.'),
  });

  useEffect(() => {
    if (typeof window !== 'undefined' && !hasHydrated) {
      useBirthStore.setState({ hasHydrated: true });
    }
  }, [hasHydrated]);

  useEffect(() => {
    if (typeof window === 'undefined' || !hasHydrated) return;

    const fetch = async () => {
      setLoading(true);
      setError(null);
      try {
        if (birthDetails?.date && birthDetails?.time && birthDetails?.latitude != null && birthDetails?.longitude != null) {
          const all = await getTransitAll({
            dob: birthDetails.date,
            time: birthDetails.time,
            lat: birthDetails.latitude,
            lon: birthDetails.longitude,
            timezone: birthDetails.timezone || 'Asia/Kolkata',
          });
          const tr = all?.transits ? Object.entries(all.transits).map(([planet, data]: [string, any]) => ({
            planet,
            sign: data.sign,
            degree: data.degree,
            house: data.house,
            speed: data.speed ?? '-',
          })) : [];
          setTransits(tr);
        } else {
          setTransits([]);
        }
      } catch (err: any) {
        console.error('Transits fetch error', err);
        setError(err?.message || 'Failed to load transits');
      } finally {
        setLoading(false);
      }
    };

    fetch();
  }, [hasHydrated, birthDetails?.date, birthDetails?.time, birthDetails?.latitude, birthDetails?.longitude, birthDetails?.timezone]);

  const transitColumns = [
    { key: 'planet', label: 'Planet' },
    { key: 'sign', label: 'Sign' },
    { key: 'degree', label: 'Degree' },
    { key: 'house', label: 'House' },
    { key: 'speed', label: 'Speed' },
  ];
  const tableData = transits.map((t) => ({
    planet: t.planet,
    sign: t.sign,
    degree: typeof t.degree === 'number' ? `${t.degree}°` : t.degree,
    house: t.house,
    speed: t.speed ?? '-',
  }));

  if (!hasHydrated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading…</p>
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
              Current planetary positions (Transit Activation of Yogas is on Dashboard)
            </p>
          </div>
        </FadeIn>

        {!birthDetails && (
          <div className="p-4 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-700 dark:text-amber-300 mb-6">
            Enter birth details on the home page to see current transits.
          </div>
        )}

        {error && (
          <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 mb-6">
            {error}
          </div>
        )}

        {loading && (
          <div className="flex justify-center py-8">
            <div className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {!loading && (
          <>
            {tableData.length > 0 && (
              <SlideUp delay={0.1}>
                <div className="mb-8">
                  <VedicTransits transits={transits} />
                </div>
              </SlideUp>
            )}

            {tableData.length > 0 && (
              <SlideUp delay={0.2}>
                <DataTable
                  columns={transitColumns}
                  data={tableData}
                  title="Transit Details"
                />
              </SlideUp>
            )}
          </>
        )}
      </div>
    </div>
  );
}
