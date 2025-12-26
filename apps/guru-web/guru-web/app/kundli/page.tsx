'use client';

/**
 * Kundli Chart Page
 * Displays the main birth chart
 */

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { SparklesIcon, ArrowRightIcon, ArrowLeftIcon, DocumentDuplicateIcon } from '@heroicons/react/24/outline';
import { FadeIn, SlideUp } from '@/frontend/animations';
import { useKundliStore } from '@/store/useKundliStore';
import { useBirthStore } from '@/store/useBirthStore';
import { getKundli } from '@/services/api';
import KundliChart from '@/components/KundliChart';
import DataTable from '@/components/DataTable';
import { fetchAndDisplayKundliJson, copyKundliJsonToClipboard } from '@/utils/fetchKundliJson';

export default function KundliPage() {
  const { kundliData, setKundliData, loading, setLoading, error, setError } = useKundliStore();
  const { userId, birthDetails } = useBirthStore();
  const [planetData, setPlanetData] = useState<any[]>([]);
  const [jsonCopied, setJsonCopied] = useState(false);
  const [showJson, setShowJson] = useState(false);
  const [jsonString, setJsonString] = useState<string>('');

  useEffect(() => {
    const fetchKundli = async () => {
      setLoading(true);
      try {
        // Pass user_id and birth details to get kundli
        // The deployed API needs birth details as query parameters
        const response = await getKundli(userId || undefined, birthDetails || undefined);
        
        // Debug: Log the response structure
        console.log('📥 API Response Structure:', {
          hasSuccess: !!(response as any).success,
          hasData: !!(response as any).data,
          hasKundli: !!(response as any).data?.kundli,
          hasD1: !!(response as any).D1 || !!(response as any).data?.kundli?.D1,
          topLevelKeys: Object.keys(response as any),
          kundliKeys: (response as any).data?.kundli ? Object.keys((response as any).data.kundli) : [],
          d1Keys: (response as any).D1 ? Object.keys((response as any).D1) : []
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
        
        // Pass data to ChartContainer - it will handle extraction
        setKundliData(dataForChart);
        
        // Format planet data for table - handle both formats
        // Extract data from response for table display
        let dataForTable = dataForChart;
        if ((dataForChart as any).data?.kundli) {
          dataForTable = (dataForChart as any).data.kundli;
        } else if ((dataForChart as any).D1) {
          dataForTable = (dataForChart as any).D1;
        } else if ((dataForChart as any).data?.kundli?.D1) {
          dataForTable = (dataForChart as any).data.kundli.D1;
        }
        
        let planetsForTable: any[] = [];
        if ((dataForTable as any).planets && Array.isArray((dataForTable as any).planets)) {
          // Direct planets array (old format)
          planetsForTable = (dataForTable as any).planets;
        } else if ((dataForTable as any).Planets && typeof (dataForTable as any).Planets === 'object') {
          // Nested Planets object (new format)
          planetsForTable = Object.entries((dataForTable as any).Planets).map(([name, planetData]: [string, any]) => {
            // 🔒 ASTROLOGY LOCK: UI must NEVER calculate astrology.
            // API is the single source of truth.
            // Use API-provided degree_dms, arcminutes, arcseconds directly - NO CALCULATIONS
            
            let degreeDisplay = 'N/A';
            
            // Use API-provided DMS values directly (NO CALCULATIONS)
            if (planetData.degree_dms !== undefined && planetData.degree_dms !== null) {
              const deg = planetData.degree_dms;
              const min = planetData.arcminutes ?? 0;
              const sec = planetData.arcseconds ?? 0;
              
              // Format: "1°24'49\"" or "1°24'" if seconds are 0
              if (sec > 0) {
                degreeDisplay = `${deg}°${min}'${sec}"`;
              } else if (min > 0) {
                degreeDisplay = `${deg}°${min}'`;
              } else {
                degreeDisplay = `${deg}°`;
              }
            } else if (planetData.degrees_in_sign !== undefined && planetData.degrees_in_sign !== null) {
              // Fallback: Use degrees_in_sign as-is (NO CALCULATION)
              degreeDisplay = `${planetData.degrees_in_sign.toFixed(2)}°`;
            }
            
            return {
              name,
              sign: planetData.sign_sanskrit || planetData.sign || 'N/A',
              house: planetData.house ?? 'N/A',
              degree: degreeDisplay,
              nakshatra: planetData.nakshatra || 'N/A',
            };
          });
        }
        
        if (planetsForTable.length > 0) {
          setPlanetData(planetsForTable.map((planet: any) => ({
            planet: planet.name,
            sign: planet.sign,
            house: planet.house,
            degree: planet.degree, // Already formatted as "31°24'" - don't add another °
            nakshatra: planet.nakshatra || '-',
          })));
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load kundli');
      } finally {
        setLoading(false);
      }
    };

    fetchKundli();
  }, [setKundliData, setLoading, setError, userId]);

  const planetColumns = [
    { key: 'planet', label: 'Planet' },
    { key: 'sign', label: 'Rashi (Vedic)' },
    { key: 'house', label: 'House' },
    { key: 'degree', label: 'Degree' },
    { key: 'nakshatra', label: 'Nakshatra' },
  ];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading kundli chart...</p>
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
              lagna={kundliData?.lagna || 1}
            />
          </div>
        </SlideUp>

        {/* Planet Table */}
        {planetData.length > 0 && (
          <SlideUp delay={0.4}>
            <DataTable
              columns={planetColumns}
              data={planetData}
              title="Planetary Positions"
            />
          </SlideUp>
        )}

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

