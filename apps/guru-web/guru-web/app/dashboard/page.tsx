'use client';

/**
 * Dashboard Page
 * Main dashboard showing overview of astrological data
 */

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { 
  SparklesIcon, 
  ClockIcon, 
  ChartBarIcon,
  SunIcon,
  ArrowLeftIcon,
  ArrowPathIcon,
  AcademicCapIcon,
} from '@heroicons/react/24/outline';
import { FadeIn, SlideUp, StaggerContainer, StaggerItem } from '@/frontend/animations';
import { useBirthStore } from '@/store/useBirthStore';
import { getKundli } from '@/services/api';
import apiClient from '@/services/api';
import { useMaxLoadTime } from '@/hooks/useMaxLoadTime';
import DashboardTransitActivationCard from '@/components/DashboardTransitActivationCard';
// 🔒 ASTROLOGY LOCK: Removed calculateCurrentDasha import - UI must NEVER calculate astrology

export default function DashboardPage() {
  const { birthDetails, userId, hasHydrated } = useBirthStore();
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);

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

    // 🔒 RACE CONDITION FIX 3: Prevent duplicate calls - REMOVED
    // ❌ BUG FIX: if (loading) return; was preventing the effect from running!
    // The loading state starts as true, so this guard blocked the initial fetch
    // Instead, we'll track if we're already fetching with a ref or check inside the async function

    // 🔒 RACE CONDITION FIX 4: Ensure API client is ready
    if (!apiClient || !apiClient.defaults?.baseURL) {
      console.warn('⚠️ API client not ready, waiting...');
      return;
    }

    const fetchDashboard = async () => {
      console.log("🔍 DASHBOARD FETCH START");
      
      try {
        // Set loading to true at the start - this prevents duplicate calls
        setLoading(true);
        setError(null);
        
        // 🔒 HARD FAILSAFE: Check birth details
        if (!birthDetails) {
          console.warn("⚠️ Dashboard: No birth details available");
          setDashboardData({
            success: false,
            message: 'Birth details required',
            error: true,
          });
          setLoading(false);
          return;
        }

        console.log("🔍 BEFORE GETKUNDLI CALL");
        const kundliResponse = await getKundli(userId || undefined, birthDetails);
        console.log("🔍 GETKUNDLI RESPONSE", kundliResponse);
        
        // 🔒 HARD FAILSAFE: Validate API response
        if (!kundliResponse) {
          throw new Error("API returned null or undefined response");
        }
        
        // Extract D1 chart data
        // Handle both response formats: direct {D1: {...}} or nested {data: {kundli: {D1: {...}}}}
        const d1 = (kundliResponse as any).D1 || (kundliResponse as any).data?.kundli?.D1;
        
        // 🔒 HARD FAILSAFE: Validate D1 data exists
        if (!d1) {
          console.error("❌ Dashboard: D1 chart data not found in API response", {
            responseKeys: Object.keys(kundliResponse || {}),
            hasD1: !!(kundliResponse as any).D1,
            hasDataKundliD1: !!(kundliResponse as any).data?.kundli?.D1,
          });
          throw new Error('D1 chart data not found in API response');
        }

        const ascendant = d1.Ascendant;
        const planets = d1.Planets || {};
        const moon = planets.Moon;
        
        // 🔒 HARD FAILSAFE: Validate Ascendant data
        if (!ascendant || (!ascendant.sign_sanskrit && !ascendant.sign)) {
          console.error("❌ Dashboard: Ascendant data missing", { ascendant, d1Keys: Object.keys(d1) });
          throw new Error('Ascendant data missing in API response');
        }
        
        // 🔒 HARD FAILSAFE: Validate Moon data
        if (!moon || (!moon.sign_sanskrit && !moon.sign)) {
          console.error("❌ Dashboard: Moon data missing", { moon, planetsKeys: Object.keys(planets) });
          throw new Error('Moon data missing in API response');
        }

        // RUNTIME ASSERTION: Ascendant.house must be 1
        if (ascendant.house !== undefined && ascendant.house !== 1) {
          console.error(`❌ VIOLATION: Ascendant house must be 1, got ${ascendant.house}`);
        }
        
        // 🔒 ASTROLOGY LOCK: UI must NEVER calculate astrology.
        // API is the single source of truth.
        // Get current_dasha from API response ONLY - NO CALCULATIONS
        
        let currentDasha = 'N/A';
        
        // Check for current_dasha in various response formats
        if ((kundliResponse as any).current_dasha?.display) {
          currentDasha = (kundliResponse as any).current_dasha.display;
        } else if ((kundliResponse as any).data?.current_dasha?.display) {
          currentDasha = (kundliResponse as any).data.current_dasha.display;
        }
        // NO FALLBACK CALCULATIONS - If API doesn't provide, show "N/A"
        
        setDashboardData({
          success: true,
          currentDasha: currentDasha,
          ascendant: ascendant.sign_sanskrit || ascendant.sign,
          moonSign: moon.sign_sanskrit || moon.sign,
          system: 'Vedic',
          ayanamsa: 'Lahiri'
        });
        console.log("🔍 DASHBOARD FETCH SUCCESS");
      } catch (error: any) {
        console.error("🔍 DASHBOARD FETCH ERROR", error);
        // Handle 404 gracefully - show "Not available" instead of "Data Error"
        if (error?.response?.status === 404) {
          setDashboardData({
            success: false,
            message: 'Kundli data not available. Please submit birth details first.',
            error: false, // Not an error, just not available
          });
          setError(null); // 404 is expected, not an error
        } else {
          // Log error and show error state
          const errorMessage = error?.message || 'Failed to fetch dashboard data';
          console.error('Dashboard data fetch failed:', error);
          setError(errorMessage);
          setDashboardData({
            success: false,
            message: errorMessage,
            error: true,
          });
        }
      } finally {
        console.log("🔍 DASHBOARD FETCH END - Setting loading to false");
        setLoading(false);
      }
    };

    if (birthDetails) {
      fetchDashboard();
    } else {
      console.log("🔍 DASHBOARD - No birth details, setting loading to false");
      setLoading(false);
    }
  }, [userId, birthDetails, hasHydrated, retryCount]); // Added retryCount to trigger retry

  const quickLinks = [
    {
      title: 'Kundli Chart',
      description: 'View your Vedic birth chart',
      icon: SparklesIcon,
      href: '/kundli',
      gradient: 'from-purple-500 to-pink-500',
    },
    {
      title: 'Dasha Timeline',
      description: 'Planetary periods',
      icon: ClockIcon,
      href: '/dasha',
      gradient: 'from-indigo-500 to-purple-500',
    },
    {
      title: 'Transits',
      description: 'Current Vedic transits',
      icon: ChartBarIcon,
      href: '/kundli/transits',
      gradient: 'from-blue-500 to-cyan-500',
    },
    {
      title: 'Panchanga',
      description: 'Today\'s panchanga',
      icon: SunIcon,
      href: '/panchanga',
      gradient: 'from-yellow-400 to-orange-500',
    },
    {
      title: 'Shadbala',
      description: 'Sixfold Planetary Strength',
      icon: ChartBarIcon,
      href: '/shadbala',
      gradient: 'from-indigo-500 to-purple-500',
    },
    {
      title: 'Guru Predictions',
      description: 'Daily Guidance',
      icon: AcademicCapIcon,
      href: '/dashboard/predictions',
      gradient: 'from-amber-500 to-orange-500',
    },
  ];

  // 🔒 HARD FAILSAFE: Show error state if loading failed
  if (error && !loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="p-6 rounded-lg bg-red-500/10 border border-red-500/20 mb-4">
            <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
            <button
              onClick={() => {
                setRetryCount(prev => prev + 1);
                setError(null);
                setLoading(true);
              }}
              className="px-4 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold flex items-center mx-auto"
            >
              <ArrowPathIcon className="w-5 h-5 mr-2" />
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading dashboard...</p>
          <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">This will timeout after 8 seconds</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50/30 to-blue-50/30 dark:from-slate-900 dark:via-purple-900/20 dark:to-blue-900/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <FadeIn>
          <div className="text-center mb-12">
            <div className="flex items-center justify-between mb-4">
              <Link
                href="/"
                className="flex items-center px-4 py-2 rounded-lg glass border border-white/20 hover:border-purple-500/50 transition-smooth text-gray-700 dark:text-gray-300"
              >
                <ArrowLeftIcon className="w-5 h-5 mr-2" />
                <span>Re-enter Birth Details</span>
              </Link>
              <div className="flex-1"></div>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-4">
              Your Dashboard
            </h1>
            {birthDetails && (
              <p className="text-gray-600 dark:text-gray-400">
                Born on {new Date(birthDetails.date).toLocaleDateString()} at {birthDetails.time} in {birthDetails.city}, {birthDetails.country}
              </p>
            )}
          </div>
        </FadeIn>

        <StaggerContainer>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {quickLinks.map((link) => (
              <StaggerItem key={link.href}>
                <Link href={link.href}>
                  <motion.div
                    whileHover={{ scale: 1.05, y: -5 }}
                    whileTap={{ scale: 0.95 }}
                    className={`glass rounded-xl p-6 border border-white/20 cursor-pointer group relative overflow-hidden`}
                  >
                    <motion.div
                      className={`absolute inset-0 bg-gradient-to-br ${link.gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-300`}
                    />
                    <div className="relative z-10">
                      <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${link.gradient} flex items-center justify-center mb-4`}>
                        <link.icon className="w-6 h-6 text-white" />
                      </div>
                      <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">
                        {link.title}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {link.description}
                      </p>
                    </div>
                  </motion.div>
                </Link>
              </StaggerItem>
            ))}
          </div>
        </StaggerContainer>

        {/* Dashboard Summary */}
        {dashboardData && (
          <SlideUp delay={0.4}>
            <div className="glass rounded-2xl p-8 border border-white/20">
              <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-6">
                Overview
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center p-4 rounded-lg bg-white/5">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Current Dasha</p>
                  <p className="text-xl font-bold text-gray-800 dark:text-gray-200">
                    {dashboardData.currentDasha || 'N/A'}
                  </p>
                </div>
                <div className="text-center p-4 rounded-lg bg-white/5">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Ascendant</p>
                  <p className="text-xl font-bold text-gray-800 dark:text-gray-200">
                    {dashboardData.ascendant || 'N/A'}
                  </p>
                </div>
                <div className="text-center p-4 rounded-lg bg-white/5">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Moon Sign</p>
                  <p className="text-xl font-bold text-gray-800 dark:text-gray-200">
                    {dashboardData.moonSign || 'N/A'}
                  </p>
                </div>
              </div>
            </div>
          </SlideUp>
        )}

        {/* Guru Guidance CTA */}
        <SlideUp delay={0.45}>
          <div className="mt-6 flex flex-col sm:flex-row items-center justify-center gap-4 p-6 rounded-xl glass border border-white/20">
            <span className="text-gray-700 dark:text-gray-300 text-center sm:text-left">
              🕉 Receive Guru Guidance based on Dasha, Shadbala & Transits
            </span>
            <Link
              href="/dashboard/predictions"
              className="inline-flex items-center justify-center px-5 py-2.5 rounded-lg bg-gradient-to-r from-amber-500 to-orange-500 text-white font-medium hover:opacity-90 transition-opacity shrink-0"
            >
              View Predictions
            </Link>
          </div>
        </SlideUp>

        {/* Transit Activation (Secondary Switch) — Dashboard only, no duplicate elsewhere */}
        <SlideUp delay={0.5}>
          <div className="mt-8">
            <DashboardTransitActivationCard birthDetails={birthDetails} />
          </div>
        </SlideUp>
      </div>
    </div>
  );
}

