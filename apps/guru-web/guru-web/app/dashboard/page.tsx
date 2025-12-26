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
} from '@heroicons/react/24/outline';
import { FadeIn, SlideUp, StaggerContainer, StaggerItem } from '@/frontend/animations';
import { useBirthStore } from '@/store/useBirthStore';
import { getKundli } from '@/services/api';
// 🔒 ASTROLOGY LOCK: Removed calculateCurrentDasha import - UI must NEVER calculate astrology

export default function DashboardPage() {
  const { birthDetails, userId } = useBirthStore();
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        // CRITICAL: /dashboard endpoint does NOT exist - use /kundli directly
        // Extract dashboard data from D1 chart
        if (!birthDetails) {
          setDashboardData({
            success: false,
            message: 'Birth details required',
            error: true,
          });
          setLoading(false);
          return;
        }

        const kundliResponse = await getKundli(userId || undefined, birthDetails);
        
        // Extract D1 chart data
        // Handle both response formats: direct {D1: {...}} or nested {data: {kundli: {D1: {...}}}}
        const d1 = (kundliResponse as any).D1 || (kundliResponse as any).data?.kundli?.D1;
        
        if (!d1) {
          setDashboardData({
            success: false,
            message: 'D1 chart data not found in API response',
            error: true,
          });
          setLoading(false);
          return;
        }

        const ascendant = d1.Ascendant;
        const planets = d1.Planets || {};
        const moon = planets.Moon;
        
        // RUNTIME ASSERTION: Ascendant must exist and have sign
        if (!ascendant || (!ascendant.sign_sanskrit && !ascendant.sign)) {
          setDashboardData({
            success: false,
            message: 'Ascendant data missing in API response',
            error: true,
          });
          setLoading(false);
          return;
        }
        
        // RUNTIME ASSERTION: Moon must exist and have sign
        if (!moon || (!moon.sign_sanskrit && !moon.sign)) {
          setDashboardData({
            success: false,
            message: 'Moon data missing in API response',
            error: true,
          });
          setLoading(false);
          return;
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
      } catch (error: any) {
        // Handle 404 gracefully - show "Not available" instead of "Data Error"
        if (error?.response?.status === 404) {
          setDashboardData({
            success: false,
            message: 'Kundli data not available. Please submit birth details first.',
            error: false, // Not an error, just not available
          });
        } else {
          // Log error and show error state
          console.error('Dashboard data fetch failed:', error);
          setDashboardData({
            success: false,
            message: error.message || 'Failed to fetch dashboard data',
            error: true,
          });
        }
      } finally {
        setLoading(false);
      }
    };

    if (birthDetails) {
      fetchDashboard();
    } else {
      setLoading(false);
    }
  }, [userId, birthDetails]);

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
      href: '/transits',
      gradient: 'from-blue-500 to-cyan-500',
    },
    {
      title: 'Panchang',
      description: 'Today\'s panchang',
      icon: SunIcon,
      href: '/panchang',
      gradient: 'from-yellow-400 to-orange-500',
    },
  ];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading dashboard...</p>
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
      </div>
    </div>
  );
}

