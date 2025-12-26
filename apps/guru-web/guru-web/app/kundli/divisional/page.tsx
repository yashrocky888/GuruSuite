'use client';

/**
 * Divisional Charts Page
 * Displays various divisional charts (D1-D60)
 * All varga charts are supported and rendered from API data
 */

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { SparklesIcon } from '@heroicons/react/24/outline';
import { FadeIn, SlideUp } from '@/frontend/animations';
import { getDivisionalCharts, getNavamsa } from '@/services/api';
import { ChartContainer } from '@/components/Chart/ChartContainer';
import { useBirthStore } from '@/store/useBirthStore';

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
  const { userId } = useBirthStore();

  useEffect(() => {
    const fetchChart = async () => {
      setLoading(true);
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
        const kundliResponse = await getKundli(userId || undefined, birthDetails || undefined);
        
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
        
        // Check multiple possible response structures
        // Structure 1: { D1: {...}, D2: {...}, ... } (direct)
        // Structure 2: { data: { kundli: { D1: {...}, D2: {...} } } }
        // Structure 3: { success: true, data: { kundli: { D1: {...}, D2: {...} } } }
        if (kundliResponse) {
          if ((kundliResponse as any)[backendChartType]) {
            // Direct structure: { D2: {...} }
            data = (kundliResponse as any)[backendChartType];
            console.log(`✅ Extracted ${backendChartType} from direct structure`);
          } else if ((kundliResponse as any).data?.kundli?.[backendChartType]) {
            // Nested structure: { data: { kundli: { D2: {...} } } }
            data = (kundliResponse as any).data.kundli[backendChartType];
            console.log(`✅ Extracted ${backendChartType} from nested structure (data.kundli)`);
          } else if ((kundliResponse as any).data?.[backendChartType]) {
            // Alternative nested: { data: { D2: {...} } }
            data = (kundliResponse as any).data[backendChartType];
            console.log(`✅ Extracted ${backendChartType} from nested structure (data)`);
          } else {
            console.warn(`⚠️ ${backendChartType} not found in response structure`);
          }
        }
        
        // If still no data, try fallback endpoint (but it will likely 404)
        if (!data) {
          try {
            data = await getDivisionalCharts(selectedChart, userId || undefined);
          } catch (divisionalError: any) {
            // Endpoint doesn't exist - this is expected
            // Validate error structure before logging
            const errorMessage = divisionalError?.message || String(divisionalError) || 'Unknown error';
            console.warn(`Divisional chart ${backendChartType} not found in main response:`, errorMessage);
          }
        }
        
        // Validate chart data structure before setting
        // CRITICAL: D24-D60 are "pure sign charts" with Houses: null (astrologically correct)
        if (data) {
          const isPureSignChart = /^D(24|27|30|40|45|60)$/.test(backendChartType);
          
          // 🔒 CRITICAL: Log D24 data structure for debugging
          if (backendChartType === 'D24') {
            console.log('📊 D24 Chart Data Structure:', {
              hasAscendant: !!data.Ascendant,
              ascendantSign: data.Ascendant?.sign,
              ascendantSignIndex: data.Ascendant?.sign_index,
              hasPlanets: !!data.Planets,
              planetsCount: data.Planets ? Object.keys(data.Planets).length : 0,
              planets: data.Planets ? Object.keys(data.Planets) : [],
              housesValue: data.Houses,
              isPureSignChart,
              fullData: data,
            });
          }
          
          // Validate required fields based on chart type
          const hasAscendant = !!data.Ascendant;
          const hasPlanets = data.Planets && typeof data.Planets === 'object' && Object.keys(data.Planets).length > 0;
          
          // For pure sign charts: Houses can be null (valid)
          // For other charts: Houses should be an array (but allow null as fallback)
          const hasValidHouses = isPureSignChart
            ? (data.Houses === null || data.Houses === undefined || Array.isArray(data.Houses))
            : (data.Houses === null || Array.isArray(data.Houses));
          
          if (!hasAscendant || !hasPlanets || !hasValidHouses) {
            // Only log in development - this might be legitimate data absence
            if (process.env.NODE_ENV === 'development') {
              console.warn(`⚠️ Chart ${backendChartType} structure validation:`, {
                hasAscendant,
                hasPlanets,
                hasValidHouses,
                housesValue: data.Houses,
                isPureSignChart,
                planetsCount: data.Planets ? Object.keys(data.Planets).length : 0,
              });
          }
            // Treat as legitimate absence, not error
            setChartData(null);
          } else {
            // 🔒 CRITICAL: Force fresh render with new data
            setChartData({ ...data }); // Create new object reference
            setChartKey(prev => prev + 1); // Force ChartContainer to re-render
          }
        } else {
          // No data returned - legitimate absence (chart not computed or not available)
          console.warn(`⚠️ No ${backendChartType} data returned from API`);
          setChartData(null);
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
        
        setChartData(null);
      } finally {
        setLoading(false);
      }
    };

    if (selectedChart) {
      // 🔒 CRITICAL: Clear chart data when chart type changes to prevent stale data
      setChartData(null);
      setChartKey(prev => prev + 1);
      fetchChart();
    }
  }, [selectedChart, userId]);

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
              <div className="mb-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-md">
                <p className="text-sm text-yellow-800 dark:text-yellow-200">
                  <strong>Note:</strong> D24 (Chaturvimsamsa) has multiple classical calculation methods. 
                  Results may differ from Prokerala depending on the method used.
                </p>
              </div>
            )}
            {chartData && (
              <div className="mt-4 pt-4 border-t border-white/10">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      <span className="font-semibold">Lagna:</span> {chartData.lagnaSignSanskrit || chartData.lagnaSign || 'N/A'} 
                      {chartData.lagnaDegree !== undefined && ` (${chartData.lagnaDegree.toFixed(2)}°)`}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      <span className="font-semibold">System:</span> {chartData.system || 'Vedic'} 
                      {' | '}
                      <span className="font-semibold">Ayanamsa:</span> {chartData.ayanamsa || 'Lahiri'}
                    </p>
                  </div>
                  <div>
                    {chartData.planets && chartData.planets.length > 0 && (
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        <span className="font-semibold">Planets:</span> {chartData.planets.length} calculated
                      </p>
                    )}
                    {chartData.houses && Array.isArray(chartData.houses) && chartData.houses.length > 0 && (
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        <span className="font-semibold">Houses:</span> {chartData.houses.length} calculated
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
            )}
          </div>
        </SlideUp>

        {/* Chart Display */}
        {loading ? (
          <div className="flex items-center justify-center h-[600px]">
            <div className="text-center">
              <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-gray-600 dark:text-gray-400">Loading chart...</p>
            </div>
          </div>
        ) : chartData ? (
          <SlideUp delay={0.4}>
            <ChartContainer 
              key={`${selectedChart}-${chartKey}`} // Force re-render on chart change
              chartData={chartData} 
              chartType={selectedChart === 'd9' ? 'navamsa' : selectedChart === 'd10' ? 'dasamsa' : 'rasi'}
              vargaName={divisionalCharts.find(c => c.key === selectedChart)?.name}
            />
          </SlideUp>
        ) : (
          <div className="flex items-center justify-center h-[600px] glass rounded-xl border border-white/20">
            <p className="text-gray-500 dark:text-gray-400">No chart data available. Please submit birth details first.</p>
          </div>
        )}
      </div>
    </div>
  );
}

