'use client';

/**
 * Divisional Charts Page
 * Displays various divisional charts (D1-D60)
 * All varga charts are supported and rendered from API data
 */

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { SparklesIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { FadeIn, SlideUp } from '@/frontend/animations';
import { getDivisionalCharts, getNavamsa } from '@/services/api';
import apiClient from '@/services/api';
import { ChartContainer } from '@/components/Chart/ChartContainer';
import { useBirthStore } from '@/store/useBirthStore';
import { useMaxLoadTime } from '@/hooks/useMaxLoadTime';

// Complete list of all varga charts (D1-D60)
// These match the backend API varga keys exactly
const divisionalCharts = [
  { key: 'd1', name: 'D1 - Rasi Chart', description: 'Main birth chart' },
  { key: 'd2', name: 'D2 - Hora Chart', description: 'Wealth and finances' },
  { key: 'd3', name: 'D3 - Drekkana Chart', description: 'Siblings and courage' },
  { key: 'd4', name: 'D4 - Chaturthamsa Chart', description: 'Property and assets' },
  { key: 'd7', name: 'D7 - Saptamsa Chart', description: 'Children and progeny' },
  { key: 'd9', name: 'D9 - Navamsa Chart', description: 'Marriage and relationships' },
  { key: 'd10', name: 'D10 - Dashamsa Chart', description: 'Career and profession' },
  { key: 'd12', name: 'D12 - Dwadashamsa Chart', description: 'Parents and past life' },
  { key: 'd16', name: 'D16 - Shodasamsa Chart', description: 'Vehicles and comforts' },
  { key: 'd20', name: 'D20 - Vimsamsa Chart', description: 'Spiritual progress' },
  { key: 'd24', name: 'D24 - Chaturvimsamsa Chart', description: 'Education and learning' },
  { key: 'd27', name: 'D27 - Saptavimsamsa Chart', description: 'Strengths and weaknesses' },
  { key: 'd30', name: 'D30 - Trimsamsa Chart', description: 'Misfortunes and obstacles' },
  { key: 'd40', name: 'D40 - Khavedamsa Chart', description: 'Maternal family influences' },
  { key: 'd45', name: 'D45 - Akshavedamsa Chart', description: 'Paternal family influences' },
  { key: 'd60', name: 'D60 - Shashtiamsa Chart', description: 'Karmic patterns from past lives' },
];


export default function DivisionalChartsPage() {
  const [selectedChart, setSelectedChart] = useState('d1');
  const [chartData, setChartData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [chartKey, setChartKey] = useState(0); // Force re-render key
  const [isMounted, setIsMounted] = useState(false); // Track client-side mount
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const { userId, birthDetails, hasHydrated } = useBirthStore();
  const router = useRouter();

  // 🔒 MAX LOAD TIME: Auto-stop spinner after 8 seconds
  useMaxLoadTime({
    loading,
    setLoading,
    maxTime: 8000,
    onTimeout: () => {
      setError('Loading took too long. Please try again.');
    },
  });

  // 🔒 SSR FIX: Track client-side mount to prevent hydration mismatch
  useEffect(() => {
    setIsMounted(true);
    // Set hasHydrated immediately on client-side mount
    if (!hasHydrated) {
      useBirthStore.setState({ hasHydrated: true });
    }
  }, [hasHydrated]); // Run once on mount

  // 🔒 FIX 2: Reset chart ONLY when chart type changes
  useEffect(() => {
    setChartData(null);
    setChartKey(prev => prev + 1);
  }, [selectedChart]);

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

    // 🔒 PRODUCTION API GUARD - userId OR birthDetails required
    if (!userId && !birthDetails) {
      console.warn('⚠️ userId and birthDetails missing — divisional charts require either userId or birthDetails');
      setChartData(null);
      setLoading(false);
      return;
    }

    // 🔒 FIX 1: Remove forced clearing - only fetch if not loading
    if (!selectedChart) {
      return;
    }

    const fetchChart = async () => {
      setLoading(true);
      setError(null);
      try {
        // Map frontend chart type to backend format (d1 -> D1, d2 -> D2, etc.)
        const chartTypeUpper = selectedChart.toUpperCase();
        const backendChartType = chartTypeUpper.startsWith('D') ? chartTypeUpper : `D${chartTypeUpper.replace(/^D?/i, '')}`;
        
        // 🔒 CRITICAL: Log that we're fetching fresh data
        console.log(`🔄 Fetching fresh ${backendChartType} chart data from API (cache-busted)...`);
        
        let data;
        
        // Get from main kundli response (which includes all divisional charts as D1, D2, D3, etc.)
        const { getKundli } = await import('@/services/api');
        const { useBirthStore } = await import('@/store/useBirthStore');
        const birthDetails = useBirthStore.getState().birthDetails;
        
        // 🔒 IMPORTANT: Production API expects userId, but fallback to birthDetails if userId fails
        // Pass both userId and birthDetails - API will use userId first, fallback to birthDetails if 404
        const kundliResponse = await getKundli(userId || undefined, birthDetails || undefined);
        
        // 🔒 DEBUG LOG (TEMPORARY)
        console.log('📦 Kundli API response keys:', {
          topLevel: Object.keys(kundliResponse || {}),
          hasD1: 'D1' in (kundliResponse || {}),
          hasD4: 'D4' in (kundliResponse || {}),
          hasD9: 'D9' in (kundliResponse || {}),
        });
        
        // 🔒 CRITICAL: Log raw API response for D24 specifically
        if (backendChartType === 'D24') {
          console.log('📥 RAW API RESPONSE FOR D24:', {
            fullResponse: kundliResponse,
            hasD24: !!(kundliResponse as any)?.[backendChartType] || !!(kundliResponse as any)?.data?.kundli?.[backendChartType] || !!(kundliResponse as any)?.data?.[backendChartType],
            d24Data: (kundliResponse as any)?.[backendChartType] || (kundliResponse as any)?.data?.kundli?.[backendChartType] || (kundliResponse as any)?.data?.[backendChartType],
            responseKeys: Object.keys(kundliResponse || {}),
            kundliKeys: (kundliResponse as any)?.data?.kundli ? Object.keys((kundliResponse as any).data.kundli) : [],
          });
        }
        
        // 🔒 DEBUG: Log API response structure for D4
        if (backendChartType === 'D4') {
          console.log('🔍 D4 API RESPONSE DEBUG:', {
            hasKundliResponse: !!kundliResponse,
            kundliResponseKeys: kundliResponse ? Object.keys(kundliResponse) : [],
            hasD4TopLevel: !!(kundliResponse as any)?.[backendChartType],
            hasD4DataKundli: !!(kundliResponse as any)?.data?.kundli?.[backendChartType],
            hasD4Data: !!(kundliResponse as any)?.data?.[backendChartType],
            d4TopLevel: (kundliResponse as any)?.[backendChartType],
          });
        }
        
        // 🔒 UNIFIED EXTRACTION: Extract chart data once for ALL charts (including D4)
        let extractedChart =
          (kundliResponse as any)?.[backendChartType] ??
          (kundliResponse as any)?.data?.kundli?.[backendChartType] ??
          (kundliResponse as any)?.data?.[backendChartType] ??
          null;
        
        // 🔒 CRITICAL FIX: Validate extracted chart structure
        // Backend might return array instead of object for some charts
        if (extractedChart && Array.isArray(extractedChart)) {
          console.warn(`⚠️ ${backendChartType} extracted as array, expected object. Raw data:`, extractedChart);
          // If it's an array, it's likely invalid - set to null
          extractedChart = null;
        }
        
        // 🔒 VALIDATE: For D4, ensure it has required structure
        if (extractedChart && backendChartType === 'D4') {
          const hasAscendant = !!(extractedChart as any)?.Ascendant;
          const hasPlanets = !!(extractedChart as any)?.Planets;
          const planetsIsObject = hasPlanets && typeof (extractedChart as any).Planets === 'object' && !Array.isArray((extractedChart as any).Planets);
          const planetsCount = planetsIsObject ? Object.keys((extractedChart as any).Planets).length : 0;
          
          // 🔒 DEBUG: Log D4 data structure before validation
          console.log('🔍 D4 EXTRACTION DEBUG:', {
            hasExtractedChart: !!extractedChart,
            extractedChartType: typeof extractedChart,
            isArray: Array.isArray(extractedChart),
            extractedChartKeys: extractedChart && !Array.isArray(extractedChart) ? Object.keys(extractedChart) : 'N/A (array)',
            hasAscendant,
            hasPlanets,
            planetsIsObject,
            planetsCount,
            hasHouses: !!(extractedChart as any)?.Houses,
            rawD4: extractedChart, // Log full structure
          });
          
          // If D4 is missing required fields, it's invalid
          if (!hasAscendant || !hasPlanets || !planetsIsObject || planetsCount === 0) {
            console.error(`❌ D4 data incomplete:`, {
              hasAscendant,
              hasPlanets,
              planetsIsObject,
              planetsCount,
              extractedChart,
            });
            extractedChart = null; // Mark as invalid
          }
        }
        
        // If still no data, try fallback endpoint (for all charts)
        if (!extractedChart) {
          try {
            const fallbackData = await getDivisionalCharts(selectedChart, userId || undefined);
            if (fallbackData) {
              // Use fallback data if available
              setChartData({
                [backendChartType]: fallbackData
              });
              setChartKey(prev => prev + 1);
              setLoading(false);
              return;
            }
          } catch (divisionalError: any) {
            // Endpoint doesn't exist - this is expected
            const errorMessage = divisionalError?.message || String(divisionalError) || 'Unknown error';
            console.warn(`Divisional chart ${backendChartType} not found:`, errorMessage);
          }
        }
        
        // 🔒 HARD FAILSAFE: Validate extracted chart before setting
        if (!extractedChart) {
          console.warn(`⚠️ ${backendChartType} chart not found or invalid in API response`);
          throw new Error(`${backendChartType} chart not found or invalid in API response`);
        }
        
        // 🔒 HARD FAILSAFE: Validate chart structure
        if (Array.isArray(extractedChart)) {
          throw new Error(`${backendChartType} chart is an array, expected object`);
        }
        
        // 🔒 SINGLE DATA CONTRACT: All charts use { [chartType]: chartObject }
        if (extractedChart) {
          const chartDataToSet = {
            [backendChartType]: extractedChart
          };
          
          // 🔒 DEBUG: Log final chartData structure for D4
          if (backendChartType === 'D4') {
            console.log('🔍 D4 FINAL chartData STRUCTURE:', {
              chartDataKeys: Object.keys(chartDataToSet),
              hasD4: 'D4' in chartDataToSet,
              d4DataType: typeof chartDataToSet.D4,
              d4DataIsArray: Array.isArray(chartDataToSet.D4),
              d4DataKeys: chartDataToSet.D4 && !Array.isArray(chartDataToSet.D4) ? Object.keys(chartDataToSet.D4) : 'N/A',
            });
          }
          
          setChartData(chartDataToSet);
          setChartKey(prev => prev + 1);
        }
      } catch (error: any) {
        // Handle errors gracefully with proper validation
        const errorMessage = error?.message || String(error) || 'Unknown error';
        const errorStatus = error?.status || error?.response?.status || 'NO_STATUS';
        
        console.error(`❌ Error fetching divisional chart ${selectedChart}:`, {
          message: errorMessage,
          status: errorStatus,
          chartType: selectedChart,
        });
        
        setError(errorMessage);
        setChartData(null); // 🔒 HARD FAILSAFE: Clear invalid data
      } finally {
        console.log(`🔍 DIVISIONAL FETCH END (${selectedChart}) - Setting loading to false`);
        setLoading(false);
      }
    };

    // 🔒 FIX 1: Only fetch if selectedChart exists and not loading
    if (selectedChart && !loading) {
      fetchChart();
    }
  }, [hasHydrated, birthDetails, selectedChart, userId, router, retryCount]); // Added retryCount

  // 🔒 FIX 5: FINAL render logic (MANDATORY) - exact pattern
  // Prevent hydration mismatch by ensuring server and client render the same initial HTML
  // Only show loading state after client-side mount
  if (!isMounted) {
    // Server and initial client render: show full page structure
    // This ensures hydration matches
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50/30 to-blue-50/30 dark:from-slate-900 dark:via-purple-900/20 dark:to-blue-900/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="flex items-center justify-center h-[600px]">
            <p className="text-gray-500">Loading chart data…</p>
          </div>
        </div>
      </div>
    );
  }

  // After mount, check hydration and birth details
  if (!hasHydrated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50/30 to-blue-50/30 dark:from-slate-900 dark:via-purple-900/20 dark:to-blue-900/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="flex items-center justify-center h-[600px]">
            <p className="text-gray-500">Loading chart data…</p>
          </div>
        </div>
      </div>
    );
  }

  // Allow page to render even without birthDetails (user can navigate to birth-details)
  // Don't block the entire page - just show empty state for charts
  if (!birthDetails) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50/30 to-blue-50/30 dark:from-slate-900 dark:via-purple-900/20 dark:to-blue-900/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="flex items-center justify-center h-[600px] glass rounded-xl border border-white/20">
            <div className="text-center">
              <p className="text-gray-500 dark:text-gray-400 mb-4">
                Birth details not found
              </p>
              <a 
                href="/birth-details" 
                className="text-purple-600 dark:text-purple-400 hover:underline"
              >
                Go to Birth Details →
              </a>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50/30 to-blue-50/30 dark:from-slate-900 dark:via-purple-900/20 dark:to-blue-900/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <FadeIn>
          <div className="text-center mb-8">
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-2">
              Divisional Charts
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Explore different divisional charts (Vargas)
            </p>
          </div>
        </FadeIn>

        {/* Chart Selector */}
        <SlideUp delay={0.2}>
          <div className="glass rounded-xl p-4 mb-8 border border-white/20 overflow-x-auto">
            <div className="flex space-x-2">
              {divisionalCharts.map((chart) => (
                <button
                  key={chart.key}
                  onClick={() => setSelectedChart(chart.key)}
                  className={`px-4 py-2 rounded-lg transition-smooth whitespace-nowrap ${
                    selectedChart === chart.key
                      ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white'
                      : 'glass border border-white/20 text-gray-700 dark:text-gray-300 hover:border-white/40'
                  }`}
                >
                  {chart.name}
                </button>
              ))}
            </div>
          </div>
        </SlideUp>

        {/* Chart Info */}
        <SlideUp delay={0.3}>
          <div className="glass rounded-xl p-6 mb-8 border border-white/20">
            <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2">
              {divisionalCharts.find(c => c.key === selectedChart)?.name}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-3">
              {divisionalCharts.find(c => c.key === selectedChart)?.description}
            </p>
            {selectedChart === 'd24' && (
              <div className="mb-3 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md">
                <p className="text-sm text-green-800 dark:text-green-200">
                  <strong>✓ Verified:</strong> D24 (Chaturvimsamsa) uses Method 1 (Traditional Parasara Siddhamsa) 
                  and has been verified against Jagannatha Hora (JHora).
                </p>
              </div>
            )}
            {chartData && (() => {
              const chartTypeUpper = selectedChart.toUpperCase();
              const isD4 = chartTypeUpper === 'D4';

              // 🔒 FINAL UI GUARD — D4 MUST EXIST BEFORE READING
              if (isD4 && !(chartData as any)?.D4) {
                return null;
              }

              const chartRoot = isD4 ? (chartData as any).D4 : chartData;

              const lagnaSign = chartRoot?.Ascendant?.sign;
              const lagnaSignSanskrit = chartRoot?.Ascendant?.sign_sanskrit;
              const lagnaDegree = chartRoot?.Ascendant?.degree;

              return (
                <div className="mt-4 pt-4 border-t border-white/10">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        <span className="font-semibold">Lagna:</span>{' '}
                        {lagnaSignSanskrit || lagnaSign || 'N/A'}
                        {lagnaDegree !== undefined && ` (${lagnaDegree.toFixed(2)}°)`}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        <span className="font-semibold">System:</span>{' '}
                        {chartData.system || 'Vedic'}
                        {' | '}
                        <span className="font-semibold">Ayanamsa:</span>{' '}
                        {chartData.ayanamsa || 'Lahiri'}
                      </p>
                    </div>
                    <div>
                      {chartRoot?.Planets && (
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          <span className="font-semibold">Planets:</span>{' '}
                          {Object.keys(chartRoot.Planets).length} calculated
                        </p>
                      )}
                      {Array.isArray(chartRoot?.Houses) && (
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          <span className="font-semibold">Houses:</span>{' '}
                          {chartRoot.Houses.length} calculated
                        </p>
                      )}
                      {userId && (
                        <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                          Using stored birth details (User ID: {userId})
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              );
            })()}
          </div>
        </SlideUp>

        {/* Chart Display - FIX 5: Exact render pattern */}
        {error && !loading ? (
          <div className="flex items-center justify-center h-[600px]">
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
        ) : loading ? (
          <div className="flex items-center justify-center h-[600px]">
            <div className="text-center">
              <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-gray-600 dark:text-gray-400">Loading chart...</p>
              <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">This will timeout after 8 seconds</p>
            </div>
          </div>
        ) : !loading && chartData ? (
          (() => {
            // 🔒 GUARD: For D4, ensure chartData.D4 exists and is valid before rendering
            const chartTypeUpper = selectedChart.toUpperCase();
            const isD4 = chartTypeUpper === 'D4';
            
            if (isD4) {
              const d4Data = (chartData as any)?.D4;
              
              // Check if D4 exists and is valid (object with required fields, not array)
              if (!d4Data || Array.isArray(d4Data) || !d4Data.Ascendant || !d4Data.Planets || Object.keys(d4Data.Planets || {}).length === 0) {
                console.warn('⚠️ D4 chartData missing or invalid, skipping render', {
                  chartDataExists: !!chartData,
                  chartDataKeys: chartData ? Object.keys(chartData) : [],
                  hasD4: chartData && 'D4' in chartData,
                  d4DataExists: !!d4Data,
                  d4DataIsArray: Array.isArray(d4Data),
                  d4DataType: typeof d4Data,
                  hasAscendant: d4Data?.Ascendant,
                  hasPlanets: d4Data?.Planets,
                  planetsCount: d4Data?.Planets ? Object.keys(d4Data.Planets).length : 0,
                });
                return (
                  <div className="flex items-center justify-center h-[600px] glass rounded-xl border border-white/20">
                    <p className="text-gray-500 dark:text-gray-400">
                      D4 chart data is not available or incomplete. Please wait...
                    </p>
                  </div>
                );
              }
              
              // 🔒 DEBUG: Log chartData before passing to ChartContainer
              console.log('🔍 D4 RENDER DEBUG:', {
                chartDataExists: !!chartData,
                chartDataType: typeof chartData,
                chartDataKeys: chartData ? Object.keys(chartData) : [],
                hasD4: chartData && 'D4' in chartData,
                d4Data: d4Data,
                d4DataKeys: d4Data ? Object.keys(d4Data) : [],
                hasAscendant: d4Data?.Ascendant,
                hasPlanets: d4Data?.Planets,
                planetsCount: d4Data?.Planets ? Object.keys(d4Data.Planets).length : 0,
              });
            }
            
            return (
              <SlideUp delay={0.4}>
                <ChartContainer 
                  key={`${selectedChart}-${chartKey}`}
                  chartType={chartTypeUpper}
                  chartData={chartData}
                  vargaName={divisionalCharts.find(c => c.key === selectedChart)?.name}
                />
              </SlideUp>
            );
          })()
        ) : (
          <div className="flex items-center justify-center h-[600px] glass rounded-xl border border-white/20">
            <p className="text-gray-500 dark:text-gray-400">
              Divisional charts will appear once calculated
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

