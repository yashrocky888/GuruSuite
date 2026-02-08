'use client';

/**
 * Kundli Chart Page
 * Displays the main birth chart
 */

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { SparklesIcon, ArrowRightIcon, ArrowLeftIcon, DocumentDuplicateIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { FadeIn, SlideUp } from '@/frontend/animations';
import { useKundliStore } from '@/store/useKundliStore';
import { useBirthStore } from '@/store/useBirthStore';
import { getKundli } from '@/services/api';
import apiClient from '@/services/api';
import KundliChart from '@/components/KundliChart';
import { fetchAndDisplayKundliJson, copyKundliJsonToClipboard } from '@/utils/fetchKundliJson';
import { useMaxLoadTime } from '@/hooks/useMaxLoadTime';

export default function KundliPage() {
  const { kundliData, setKundliData, loading, setLoading, error, setError } = useKundliStore();
  const { userId, birthDetails, hasHydrated } = useBirthStore();
  const [jsonCopied, setJsonCopied] = useState(false);
  const [showJson, setShowJson] = useState(false);
  const [jsonString, setJsonString] = useState<string>('');
  const [retryCount, setRetryCount] = useState(0);
  const [planetFunctionalStrength, setPlanetFunctionalStrength] = useState<Record<string, any> | null>(null);

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
    if (loading) return;

    // 🔒 RACE CONDITION FIX 4: Ensure API client is ready
    if (!apiClient || !apiClient.defaults?.baseURL) {
      console.warn('⚠️ API client not ready, waiting...');
      return;
    }

    const fetchKundli = async () => {
      setLoading(true);
      setError(null);
      try {
        // Pass user_id and birth details to get kundli
        // The deployed API needs birth details as query parameters
        const response = await getKundli(userId || undefined, birthDetails || undefined);
        
        // 🔒 HARD FAILSAFE: Validate API response
        if (!response) {
          throw new Error("API returned null or undefined response");
        }
        
        // 🔒 AUDIT: Log the response structure (MANDATORY)
        console.log('📥 API Response Structure:', {
          hasSuccess: !!(response as any).success,
          hasData: !!(response as any).data,
          hasKundli: !!(response as any).data?.kundli,
          hasD1: !!(response as any).D1 || !!(response as any).data?.kundli?.D1,
          topLevelKeys: Object.keys(response as any),
          kundliKeys: (response as any).data?.kundli ? Object.keys((response as any).data.kundli) : [],
          d1Keys: (response as any).D1 ? Object.keys((response as any).D1) : [],
          // 🔒 CRITICAL: Check for D4 specifically
          hasD4: !!(response as any).D4 || !!(response as any).data?.kundli?.D4,
          // 🔒 CRITICAL: Check for ascendant and planets
          hasAscendant: !!(response as any).D1?.Ascendant || !!(response as any).data?.kundli?.D1?.Ascendant,
          hasPlanets: !!(response as any).D1?.Planets || !!(response as any).data?.kundli?.D1?.Planets,
        });
        
        // 🔒 AUDIT: Log expected vs actual keys
        const expectedKeys = ['D1', 'D2', 'D3', 'D4', 'D7', 'D9', 'D10', 'D12'];
        const actualKeys = Object.keys(response as any).filter(k => k.startsWith('D'));
        console.log('📊 Expected vs Actual Keys:', {
          expected: expectedKeys,
          actual: actualKeys,
          missing: expectedKeys.filter(k => !actualKeys.includes(k)),
        });
        
        // Check if we need to extract D1 from the response
        // API can return: { D1: {...}, D2: {...} } OR { success: true, data: { kundli: { D1: {...} } } }
        let dataForChart = response;
        if ((response as any).D1) {
          // API returns D1 directly at top level: { D1: { Ascendant: {...}, Planets: {...}, Houses: [...] }, D2: {...}, ... }
          console.log('✅ Found D1 at top level, using D1 data');
          dataForChart = (response as any).D1;
        } else if ((response as any).data?.kundli?.D1) {
          // API returns D1 as a separate key in kundli object
          console.log('✅ Found D1 chart in response.data.kundli, using D1 data');
          dataForChart = (response as any).data.kundli.D1;
        } else if ((response as any).data?.kundli) {
          // Check if kundli has Planets directly (main chart)
          if ((response as any).data.kundli.Planets) {
            console.log('✅ Found Planets in kundli, using kundli data directly');
            dataForChart = (response as any).data.kundli;
          }
        }
        
        // 🔒 HARD FAILSAFE: Validate chart data before setting
        if (!dataForChart) {
          throw new Error("Chart data extraction failed - no valid data found");
        }
        
        // 🔒 HARD FAILSAFE: Validate D1 has required structure
        if (!(dataForChart as any).Ascendant && !(dataForChart as any).Planets) {
          console.error("❌ Kundli: Invalid chart data structure", {
            dataForChartKeys: Object.keys(dataForChart || {}),
            hasAscendant: !!(dataForChart as any).Ascendant,
            hasPlanets: !!(dataForChart as any).Planets,
          });
          throw new Error("Chart data missing required fields (Ascendant or Planets)");
        }
        
        // Pass data to ChartContainer - it will handle extraction
        setKundliData(dataForChart);
        
        // Extract planet_functional_strength from top-level response (admin-only, D1-only)
        const strengthData = (response as any).planet_functional_strength;
        
        // 🧪 API PAYLOAD DEBUG (TEMP - VERIFY API RESPONSE)
        console.log('🧪 API RESPONSE - planet_functional_strength', {
          exists: !!strengthData,
          type: typeof strengthData,
          keys: strengthData ? Object.keys(strengthData) : [],
          sample: strengthData ? Object.entries(strengthData).slice(0, 2) : [],
          fullResponseKeys: Object.keys(response || {}),
          // 🔒 VERIFICATION: Check if data structure matches expected format
          firstPlanetData: strengthData && Object.keys(strengthData).length > 0 
            ? strengthData[Object.keys(strengthData)[0]] 
            : null,
        });
        
        if (strengthData && typeof strengthData === 'object') {
          setPlanetFunctionalStrength(strengthData);
        } else {
          console.warn('🧪 API RESPONSE - planet_functional_strength is missing or invalid');
          setPlanetFunctionalStrength(null);
        }
      } catch (err: any) {
        console.error("🔍 KUNDLI FETCH ERROR", err);
        const errorMessage = err?.message || 'Failed to load kundli';
        setError(errorMessage);
        // 🔒 HARD FAILSAFE: Clear invalid data on error
        setKundliData(null as any);
        setPlanetFunctionalStrength(null);
      } finally {
        console.log("🔍 KUNDLI FETCH END - Setting loading to false");
        setLoading(false);
      }
    };

    fetchKundli();
  }, [setKundliData, setLoading, setError, userId, hasHydrated, retryCount]); // Added retryCount

  // 🔒 HARD FAILSAFE: Show error state with retry if loading failed
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
          <p className="text-gray-600 dark:text-gray-400">Loading kundli chart...</p>
          <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">This will timeout after 8 seconds</p>
        </div>
      </div>
    );
  }

  // 🔒 HARD FAILSAFE: Show error if no chart data
  if (!kundliData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="p-6 rounded-lg bg-yellow-500/10 border border-yellow-500/20 mb-4">
            <p className="text-yellow-600 dark:text-yellow-400 mb-4">
              No chart data available. Please submit birth details first.
            </p>
            <Link
              href="/"
              className="px-4 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold inline-block"
            >
              Go to Birth Details
            </Link>
          </div>
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
                <span>Re-enter Birth Details</span>
              </Link>
              <div className="flex items-center gap-2">
                <button
                  onClick={async () => {
                    try {
                      const result = await fetchAndDisplayKundliJson(userId || undefined);
                      setJsonString(result.jsonString);
                      setShowJson(true);
                      await copyKundliJsonToClipboard(userId || undefined);
                      setJsonCopied(true);
                      setTimeout(() => setJsonCopied(false), 2000);
                    } catch (err) {
                      console.error('Failed to fetch/copy JSON:', err);
                    }
                  }}
                  className="flex items-center px-4 py-2 rounded-lg glass border border-white/20 hover:border-purple-500/50 transition-smooth text-gray-700 dark:text-gray-300"
                  title="Fetch and display JSON (also copied to clipboard)"
                >
                  <DocumentDuplicateIcon className="w-5 h-5 mr-2" />
                  <span>{jsonCopied ? 'Copied!' : 'Show JSON'}</span>
                </button>
                <Link
                  href="/kundli/divisional"
                  className="flex items-center px-4 py-2 rounded-lg glass border border-white/20 hover:border-white/40 transition-smooth"
                >
                  <span className="mr-2">Divisional Charts</span>
                  <ArrowRightIcon className="w-5 h-5" />
                </Link>
              </div>
            </div>
            <div>
              <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-2">
                Kundli Chart
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Your complete birth chart analysis
              </p>
            </div>
          </div>
        </FadeIn>

        {error && (
          <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 mb-6">
            {error || 'Failed to load kundli data'}
          </div>
        )}

        {/* Vedic Chart */}
        <SlideUp delay={0.2}>
          <div className="mb-8">
            <KundliChart 
              chartData={kundliData} 
              chartType="D1"
              lagna={kundliData?.lagna || 1}
              planetFunctionalStrength={planetFunctionalStrength || undefined}
            />
          </div>
        </SlideUp>

        {/* JSON Display */}
        {showJson && jsonString && (
          <SlideUp delay={0.6}>
            <div className="mb-8">
              <div className="glass rounded-xl p-6 border border-white/20">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                    API JSON Response
                  </h3>
                  <button
                    onClick={() => setShowJson(false)}
                    className="px-3 py-1 rounded-lg glass border border-white/20 hover:border-red-500/50 transition-smooth text-gray-700 dark:text-gray-300"
                  >
                    Close
                  </button>
                </div>
                <div className="bg-slate-900 rounded-lg p-4 overflow-auto max-h-[600px]">
                  <pre className="text-xs text-green-400 font-mono whitespace-pre-wrap break-words">
                    {jsonString}
                  </pre>
                </div>
              </div>
            </div>
          </SlideUp>
        )}
      </div>
    </div>
  );
}

