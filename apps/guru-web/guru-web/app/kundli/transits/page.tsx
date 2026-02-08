'use client';

/**
 * Transit (Gochar) Chart Page
 * Displays planetary transits with user-controlled date/time/location
 */

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ChartBarIcon, ArrowLeftIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { FadeIn, SlideUp } from '@/frontend/animations';
import { useBirthStore } from '@/store/useBirthStore';
import { getKundliTransits } from '@/services/api';
import apiClient from '@/services/api';
import { ChartContainer } from '@/components/Chart/ChartContainer';

export default function TransitsPage() {
  const { userId, birthDetails, hasHydrated } = useBirthStore();
  const [transitData, setTransitData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Transit input state - default to birth date/time/location
  const [transitDate, setTransitDate] = useState<string>('');
  const [transitTime, setTransitTime] = useState<string>('');
  const [transitLat, setTransitLat] = useState<number | undefined>(undefined);
  const [transitLon, setTransitLon] = useState<number | undefined>(undefined);
  const [transitLocation, setTransitLocation] = useState<string>('');

  // Initialize defaults: location from birth details, date/time from current time
  useEffect(() => {
    if (birthDetails && !transitDate) {
      // 🔒 TRANSIT LOGIC: Default location from birth details, date/time from CURRENT time
      // Transit (Gochar) = current planetary positions, not birth positions
      
      // Default location from birth details
      setTransitLat(birthDetails.latitude);
      setTransitLon(birthDetails.longitude);
      setTransitLocation(''); // Location name is optional, user can enter manually
      
      // Default date/time to CURRENT date/time (not birth date/time)
      const now = new Date();
      const yyyy = now.getFullYear();
      const mm = String(now.getMonth() + 1).padStart(2, '0');
      const dd = String(now.getDate()).padStart(2, '0');
      const hh = String(now.getHours()).padStart(2, '0');
      const min = String(now.getMinutes()).padStart(2, '0');
      
      setTransitDate(`${yyyy}-${mm}-${dd}`);
      setTransitTime(`${hh}:${min}`);
    }
  }, [birthDetails, transitDate]);

  // Fetch transit chart
  const fetchTransits = async () => {
    // Validate inputs
    if (!transitDate || !transitTime) {
      setError('Please provide transit date and time');
      return;
    }

    if (transitLat === undefined || transitLon === undefined) {
      setError('Please provide transit location (latitude and longitude)');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Format datetime as ISO string: YYYY-MM-DDTHH:MM:SS
      const [hours, minutes] = transitTime.split(':');
      const datetimeISO = `${transitDate}T${hours || '00'}:${minutes || '00'}:00`;
      
      const response = await getKundliTransits(
        userId || undefined,
        datetimeISO,
        transitLat,
        transitLon,
        birthDetails?.timezone
      );
      
      // 🔒 HARD FAILSAFE: Validate API response
      if (!response) {
        throw new Error("API returned null or undefined response");
      }
      
      // Transit response should match D1 structure
      setTransitData(response);
    } catch (err: any) {
      console.error("🔍 TRANSITS FETCH ERROR", err);
      const errorMessage = err?.response?.data?.detail?.message || err?.message || 'Failed to load transit chart';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Auto-fetch on mount with default values (only once)
  const [hasAutoFetched, setHasAutoFetched] = useState(false);

  useEffect(() => {
    // 🔒 RACE CONDITION FIX 1: Client-side only
    if (typeof window === 'undefined') return;

    // 🔒 RACE CONDITION FIX 2: Hydration complete
    if (!hasHydrated) return;

    // 🔒 RACE CONDITION FIX 3: Ensure API client is ready
    if (!apiClient || !apiClient.defaults?.baseURL) {
      console.warn('⚠️ API client not ready, waiting...');
      return;
    }

    // Only auto-fetch once when defaults are set
    if (transitDate && transitTime && transitLat !== undefined && transitLon !== undefined && !hasAutoFetched) {
      setHasAutoFetched(true);
      
      const autoFetch = async () => {
        setLoading(true);
        setError(null);

        try {
          const [hours, minutes] = transitTime.split(':');
          const datetimeISO = `${transitDate}T${hours || '00'}:${minutes || '00'}:00`;
          
          const response = await getKundliTransits(
            userId || undefined,
            datetimeISO,
            transitLat,
            transitLon,
            birthDetails?.timezone
          );
          
          if (!response) {
            throw new Error("API returned null or undefined response");
          }
          
          setTransitData(response);
        } catch (err: any) {
          console.error("🔍 TRANSITS AUTO-FETCH ERROR", err);
          const errorMessage = err?.response?.data?.detail?.message || err?.message || 'Failed to load transit chart';
          setError(errorMessage);
        } finally {
          setLoading(false);
        }
      };

      autoFetch();
    }
  }, [hasHydrated, transitDate, transitTime, transitLat, transitLon, hasAutoFetched, userId, birthDetails?.timezone]);

  if (loading && !transitData) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-purple-50/30 to-blue-50/30 dark:from-slate-900 dark:via-purple-900/20 dark:to-blue-900/20">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center mb-4 animate-pulse">
            <ChartBarIcon className="w-8 h-8 text-white" />
          </div>
          <p className="text-gray-600 dark:text-gray-400">Loading transit chart...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50/30 to-blue-50/30 dark:from-slate-900 dark:via-purple-900/20 dark:to-blue-900/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <FadeIn>
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <Link
                href="/"
                className="flex items-center px-4 py-2 rounded-lg glass border border-white/20 hover:border-purple-500/50 transition-smooth text-gray-700 dark:text-gray-300"
              >
                <ArrowLeftIcon className="w-5 h-5 mr-2" />
                <span>Back to Dashboard</span>
              </Link>
            </div>
            <div>
              <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent mb-2">
                Transit Chart
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Planetary positions for specified date, time, and location
              </p>
            </div>
          </div>
        </FadeIn>

        {error && (
          <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 mb-6">
            {error}
          </div>
        )}

        {/* Transit Controls */}
        <SlideUp delay={0.1}>
          <div className="mb-8 glass rounded-xl p-6 border border-white/20">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">
              Transit Settings
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
              {/* Date */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Date
                </label>
                <input
                  type="date"
                  value={transitDate}
                  onChange={(e) => setTransitDate(e.target.value)}
                  className="w-full px-4 py-2 rounded-lg glass border border-white/20 focus:border-blue-500/50 focus:outline-none text-gray-800 dark:text-gray-200 bg-white/50 dark:bg-gray-800/50"
                />
              </div>

              {/* Time */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Time
                </label>
                <input
                  type="time"
                  value={transitTime}
                  onChange={(e) => setTransitTime(e.target.value)}
                  className="w-full px-4 py-2 rounded-lg glass border border-white/20 focus:border-blue-500/50 focus:outline-none text-gray-800 dark:text-gray-200 bg-white/50 dark:bg-gray-800/50"
                />
              </div>

              {/* Latitude */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Latitude
                </label>
                <input
                  type="number"
                  step="any"
                  value={transitLat ?? ''}
                  onChange={(e) => setTransitLat(e.target.value ? parseFloat(e.target.value) : undefined)}
                  placeholder="e.g., 12.97"
                  className="w-full px-4 py-2 rounded-lg glass border border-white/20 focus:border-blue-500/50 focus:outline-none text-gray-800 dark:text-gray-200 bg-white/50 dark:bg-gray-800/50"
                />
              </div>

              {/* Longitude */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Longitude
                </label>
                <input
                  type="number"
                  step="any"
                  value={transitLon ?? ''}
                  onChange={(e) => setTransitLon(e.target.value ? parseFloat(e.target.value) : undefined)}
                  placeholder="e.g., 77.59"
                  className="w-full px-4 py-2 rounded-lg glass border border-white/20 focus:border-blue-500/50 focus:outline-none text-gray-800 dark:text-gray-200 bg-white/50 dark:bg-gray-800/50"
                />
              </div>
            </div>

            {/* Location Name (optional) */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Location Name (optional)
              </label>
              <input
                type="text"
                value={transitLocation}
                onChange={(e) => setTransitLocation(e.target.value)}
                placeholder="e.g., Bangalore, India"
                className="w-full px-4 py-2 rounded-lg glass border border-white/20 focus:border-blue-500/50 focus:outline-none text-gray-800 dark:text-gray-200 bg-white/50 dark:bg-gray-800/50"
              />
            </div>

            {/* Update Button */}
            <button
              onClick={fetchTransits}
              disabled={loading}
              className="flex items-center px-6 py-3 rounded-lg bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-medium hover:from-blue-600 hover:to-cyan-600 transition-smooth disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <ArrowPathIcon className="w-5 h-5 mr-2 animate-spin" />
                  <span>Updating...</span>
                </>
              ) : (
                <>
                  <ArrowPathIcon className="w-5 h-5 mr-2" />
                  <span>Update Transits</span>
                </>
              )}
            </button>
          </div>
        </SlideUp>

        {/* Transit Chart */}
        {transitData && transitData.Planets && transitData.Ascendant ? (
          <SlideUp delay={0.2}>
            <div className="mb-8">
              <ChartContainer 
                chartData={transitData}
                chartType={transitData.chartType || "TRANSIT"}
                vargaName="Transit Chart"
              />
            </div>
          </SlideUp>
        ) : transitData ? (
          <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/20 text-yellow-600 dark:text-yellow-400 mb-6">
            Chart Data Unavailable – Unable to extract Transit Chart from API response
          </div>
        ) : null}
      </div>
    </div>
  );
}
