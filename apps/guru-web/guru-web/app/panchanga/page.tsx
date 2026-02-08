'use client';

/**
 * Panchanga Page
 * Displays Panchanga information from Drik Siddhanta API
 * Render-only - No calculations, No AI
 * User-controlled date and location (NOT birth details)
 */

import { useEffect, useState } from 'react';
import { ArrowPathIcon } from '@heroicons/react/24/outline';
import { SlideUp } from '@/frontend/animations';
import { getPanchanga, LocationSuggestion } from '@/services/api';
import LocationAutocomplete from '@/components/LocationAutocomplete';

interface KaranaItem {
  name: string;
  end_time: string;
}

interface PanchangaData {
  panchanga: {
    sunrise: string;
    sunset: string;
    vara: {
      name: string;
      lord: string;
    };
    tithi: {
      current?: {
        name: string;
        number: number;
        paksha: string;
        end_time: string;
      };
      next?: {
        name: string;
        number: number;
        paksha: string;
      };
      // Legacy format support (for backward compatibility)
      name?: string;
      number?: number;
      paksha?: string;
      end_time?: string;
    };
    nakshatra: {
      current?: {
        name: string;
        lord: string;
        pada: number;
        end_time: string;
      };
      next?: {
        name: string;
        lord: string;
      };
      // Legacy format support
      name?: string;
      lord?: string;
      pada?: number;
      end_time?: string;
    };
    yoga: {
      current?: {
        name: string;
        end_time: string;
      };
      next?: {
        name: string;
      };
      // Legacy format support
      name?: string;
      end_time?: string;
    };
    karana: KaranaItem | KaranaItem[]; // Can be single object or array
    paksha?: string;
    amanta_month?: string;
    purnimanta_month?: string;
    is_adhika_masa?: boolean;
    moonsign?: string;
    sunsign?: string;
    weekday?: string;
    shaka_samvat?: string;
    vikram_samvat?: string;
    gujarati_samvat?: string;
  };
}

export default function PanchangaPage() {
  const [panchangaData, setPanchangaData] = useState<PanchangaData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Panchanga input state - default to today and Bangalore
  const [panchangaDate, setPanchangaDate] = useState<string>('');
  const [panchangaLocation, setPanchangaLocation] = useState<LocationSuggestion | null>(null);
  const [panchangaLat, setPanchangaLat] = useState<number>(12.9716); // Default: Bangalore
  const [panchangaLon, setPanchangaLon] = useState<number>(77.5946);
  const [panchangaTz, setPanchangaTz] = useState<string>('Asia/Kolkata');

  // Initialize defaults: today's date
  useEffect(() => {
    if (!panchangaDate) {
      const today = new Date();
      const yyyy = today.getFullYear();
      const mm = String(today.getMonth() + 1).padStart(2, '0');
      const dd = String(today.getDate()).padStart(2, '0');
      setPanchangaDate(`${yyyy}-${mm}-${dd}`);
    }
  }, [panchangaDate]);

  // Update lat/lon/tz when location is selected
  useEffect(() => {
    if (panchangaLocation) {
      setPanchangaLat(panchangaLocation.latitude);
      setPanchangaLon(panchangaLocation.longitude);
      if (panchangaLocation.timezone) {
        setPanchangaTz(panchangaLocation.timezone);
      }
    }
  }, [panchangaLocation]);

  // Fetch Panchanga
  const fetchPanchanga = async () => {
    if (!panchangaDate) {
      setError('Please provide a date');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      console.log('🧪 PANCHANGA API REQUEST:', { date: panchangaDate, lat: panchangaLat, lon: panchangaLon, tz: panchangaTz });

      const data = await getPanchanga(panchangaDate, panchangaLat, panchangaLon, panchangaTz);

      // TEMP DEBUG: Verify data structure
      console.log('🧪 PANCHANGA RAW API', data);
      console.log('🧪 PANCHANGA OBJECT', data?.panchanga);
      console.log('🧪 KARANA TYPE', Array.isArray(data?.panchanga?.karana) ? 'ARRAY' : 'OBJECT', data?.panchanga?.karana);

      if (!data || !data.panchanga) {
        throw new Error('Invalid API response');
      }

      setPanchangaData(data);
    } catch (err: any) {
      console.error('❌ PANCHANGA FETCH ERROR:', err);
      setError(err.message || 'Failed to load Panchanga');
    } finally {
      setLoading(false);
    }
  };

  // Auto-fetch on mount with default values (only once)
  const [hasAutoFetched, setHasAutoFetched] = useState(false);

  useEffect(() => {
    if (panchangaDate && !hasAutoFetched) {
      setHasAutoFetched(true);
      fetchPanchanga();
    }
  }, [panchangaDate, hasAutoFetched]);

  if (loading && !panchangaData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50/30 to-blue-50/30 dark:from-slate-900 dark:via-purple-900/20 dark:to-blue-900/20 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading Panchanga...</p>
        </div>
      </div>
    );
  }

  // Normalize karana to array
  const karanas = panchangaData?.panchanga?.karana
    ? (Array.isArray(panchangaData.panchanga.karana)
        ? panchangaData.panchanga.karana
        : [panchangaData.panchanga.karana])
    : [];

  // Get location display string
  const locationDisplay = panchangaLocation
    ? `${panchangaLocation.city || '—'}, ${panchangaLocation.country || '—'}`
    : '—';

  // Get formatted date
  const dateDisplay = panchangaDate
    ? new Date(panchangaDate).toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : '—';

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50/30 to-blue-50/30 dark:from-slate-900 dark:via-purple-900/20 dark:to-blue-900/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <SlideUp>
          <div className="mb-8">
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent mb-2">
              Panchanga
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Daily Panchanga from Drik Siddhanta • Sunrise-based calculation
            </p>
          </div>
        </SlideUp>

        {error && (
          <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 mb-6">
            {error}
          </div>
        )}

        {/* Panchanga Controls */}
        <SlideUp delay={0.1}>
          <div className="mb-8 glass rounded-xl p-6 border border-white/20">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">
              Panchanga Settings
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
              {/* Date */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Date
                </label>
                <input
                  type="date"
                  value={panchangaDate}
                  onChange={(e) => setPanchangaDate(e.target.value)}
                  className="w-full px-4 py-2 rounded-lg glass border border-white/20 focus:border-blue-500/50 focus:outline-none text-gray-800 dark:text-gray-200 bg-white/50 dark:bg-gray-800/50"
                />
              </div>

              {/* Location Autocomplete */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Location
                </label>
                <LocationAutocomplete
                  value={panchangaLocation?.displayName || panchangaLocation?.city || ''}
                  onChange={(location) => setPanchangaLocation(location)}
                  placeholder="Search city..."
                />
              </div>

              {/* Timezone */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Timezone
                </label>
                <input
                  type="text"
                  value={panchangaTz}
                  onChange={(e) => setPanchangaTz(e.target.value)}
                  placeholder="e.g., Asia/Kolkata"
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
                  value={panchangaLat}
                  onChange={(e) => setPanchangaLat(e.target.value ? parseFloat(e.target.value) : 0)}
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
                  value={panchangaLon}
                  onChange={(e) => setPanchangaLon(e.target.value ? parseFloat(e.target.value) : 0)}
                  placeholder="e.g., 77.59"
                  className="w-full px-4 py-2 rounded-lg glass border border-white/20 focus:border-blue-500/50 focus:outline-none text-gray-800 dark:text-gray-200 bg-white/50 dark:bg-gray-800/50"
                />
              </div>
            </div>

            {/* Update Button */}
            <button
              onClick={fetchPanchanga}
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
                  <span>Update Panchanga</span>
                </>
              )}
            </button>
          </div>
        </SlideUp>

        {/* Panchanga Table */}
        {panchangaData && (
          <SlideUp delay={0.2}>
            <div className="rounded-lg bg-slate-800/50 dark:bg-slate-800/50 border border-slate-700 dark:border-slate-700 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <tbody className="divide-y divide-slate-700 dark:divide-slate-700">
                    {/* Location */}
                    <tr className="hover:bg-slate-800/50 dark:hover:bg-slate-800/50 transition-colors">
                      <td className="px-6 py-4 text-sm font-medium text-gray-400 dark:text-gray-400 w-1/3">Location</td>
                      <td className="px-6 py-4 text-base text-gray-200 dark:text-gray-200">{locationDisplay}</td>
                    </tr>

                    {/* Date */}
                    <tr className="hover:bg-slate-800/50 dark:hover:bg-slate-800/50 transition-colors">
                      <td className="px-6 py-4 text-sm font-medium text-gray-400 dark:text-gray-400">Date</td>
                      <td className="px-6 py-4 text-base text-gray-200 dark:text-gray-200">{dateDisplay}</td>
                    </tr>

                    {/* Sunrise */}
                    <tr className="hover:bg-slate-800/50 dark:hover:bg-slate-800/50 transition-colors">
                      <td className="px-6 py-4 text-sm font-medium text-gray-400 dark:text-gray-400">Sunrise</td>
                      <td className="px-6 py-4 text-base font-mono text-gray-200 dark:text-gray-200">{panchangaData.panchanga.sunrise ?? "—"}</td>
                    </tr>

                    {/* Sunset */}
                    <tr className="hover:bg-slate-800/50 dark:hover:bg-slate-800/50 transition-colors">
                      <td className="px-6 py-4 text-sm font-medium text-gray-400 dark:text-gray-400">Sunset</td>
                      <td className="px-6 py-4 text-base font-mono text-gray-200 dark:text-gray-200">{panchangaData.panchanga.sunset ?? "—"}</td>
                    </tr>

                    {/* Vara */}
                    <tr className="hover:bg-slate-800/50 dark:hover:bg-slate-800/50 transition-colors">
                      <td className="px-6 py-4 text-sm font-medium text-gray-400 dark:text-gray-400">Vara</td>
                      <td className="px-6 py-4 text-base text-gray-200 dark:text-gray-200">
                        {panchangaData.panchanga.vara?.name ?? "—"}
                        {panchangaData.panchanga.vara?.lord && (
                          <span className="ml-2 text-sm text-gray-400 dark:text-gray-400">({panchangaData.panchanga.vara.lord})</span>
                        )}
                      </td>
                    </tr>

                    {/* Tithi */}
                    <tr className="hover:bg-slate-800/50 dark:hover:bg-slate-800/50 transition-colors">
                      <td className="px-6 py-4 text-sm font-medium text-gray-400 dark:text-gray-400">Tithi</td>
                      <td className="px-6 py-4 text-base text-gray-200 dark:text-gray-200">
                        <div className="space-y-1">
                          <div className="flex flex-col sm:flex-row sm:items-center sm:gap-2">
                            <span className="font-semibold">{panchangaData.panchanga.tithi?.current?.name ?? panchangaData.panchanga.tithi?.name ?? "—"}</span>
                            {panchangaData.panchanga.tithi?.current?.paksha && (
                              <span className="text-sm text-gray-400 dark:text-gray-400">({panchangaData.panchanga.tithi.current.paksha} Paksha)</span>
                            )}
                            {panchangaData.panchanga.tithi?.current?.end_time && (
                              <span className="text-sm text-gray-400 dark:text-gray-400 font-mono">upto {panchangaData.panchanga.tithi.current.end_time}</span>
                            )}
                          </div>
                          {panchangaData.panchanga.tithi?.next && (
                            <div className="text-sm text-gray-400 dark:text-gray-400">
                              Next: {panchangaData.panchanga.tithi.next.name} ({panchangaData.panchanga.tithi.next.paksha})
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>

                    {/* Nakshatra */}
                    <tr className="hover:bg-slate-800/50 dark:hover:bg-slate-800/50 transition-colors">
                      <td className="px-6 py-4 text-sm font-medium text-gray-400 dark:text-gray-400">Nakshatra</td>
                      <td className="px-6 py-4 text-base text-gray-200 dark:text-gray-200">
                        <div className="space-y-1">
                          <div className="flex flex-col sm:flex-row sm:items-center sm:gap-2">
                            <span className="font-semibold">{panchangaData.panchanga.nakshatra?.current?.name ?? panchangaData.panchanga.nakshatra?.name ?? "—"}</span>
                            {panchangaData.panchanga.nakshatra?.current?.pada && (
                              <span className="text-sm text-gray-400 dark:text-gray-400">Pada {panchangaData.panchanga.nakshatra.current.pada}</span>
                            )}
                            {panchangaData.panchanga.nakshatra?.current?.lord && (
                              <span className="text-sm text-gray-400 dark:text-gray-400">({panchangaData.panchanga.nakshatra.current.lord})</span>
                            )}
                            {panchangaData.panchanga.nakshatra?.current?.end_time && (
                              <span className="text-sm text-gray-400 dark:text-gray-400 font-mono">upto {panchangaData.panchanga.nakshatra.current.end_time}</span>
                            )}
                          </div>
                          {panchangaData.panchanga.nakshatra?.next && (
                            <div className="text-sm text-gray-400 dark:text-gray-400">
                              Next: {panchangaData.panchanga.nakshatra.next.name} ({panchangaData.panchanga.nakshatra.next.lord})
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>

                    {/* Yoga */}
                    <tr className="hover:bg-slate-800/50 dark:hover:bg-slate-800/50 transition-colors">
                      <td className="px-6 py-4 text-sm font-medium text-gray-400 dark:text-gray-400">Yoga</td>
                      <td className="px-6 py-4 text-base text-gray-200 dark:text-gray-200">
                        <div className="space-y-1">
                          <div className="flex flex-col sm:flex-row sm:items-center sm:gap-2">
                            <span className="font-semibold">{panchangaData.panchanga.yoga?.current?.name ?? panchangaData.panchanga.yoga?.name ?? "—"}</span>
                            {panchangaData.panchanga.yoga?.current?.end_time && (
                              <span className="text-sm text-gray-400 dark:text-gray-400 font-mono">upto {panchangaData.panchanga.yoga.current.end_time}</span>
                            )}
                          </div>
                          {panchangaData.panchanga.yoga?.next && (
                            <div className="text-sm text-gray-400 dark:text-gray-400">
                              Next: {panchangaData.panchanga.yoga.next.name}
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>

                    {/* Karana(s) */}
                    <tr className="hover:bg-slate-800/50 dark:hover:bg-slate-800/50 transition-colors">
                      <td className="px-6 py-4 text-sm font-medium text-gray-400 dark:text-gray-400">Karana</td>
                      <td className="px-6 py-4 text-base text-gray-200 dark:text-gray-200">
                        {karanas.length > 0 ? (
                          <div className="space-y-1">
                            {karanas.map((karana, idx) => (
                              <div key={idx} className="flex flex-col sm:flex-row sm:items-center sm:gap-2">
                                <span className={idx === 0 ? "font-semibold" : ""}>{karana.name ?? "—"}</span>
                                {karana.end_time && (
                                  <span className="text-sm text-gray-400 dark:text-gray-400 font-mono">upto {karana.end_time}</span>
                                )}
                              </div>
                            ))}
                          </div>
                        ) : (
                          "—"
                        )}
                      </td>
                    </tr>

                    {/* Paksha */}
                    {panchangaData.panchanga.paksha && (
                      <tr className="hover:bg-slate-800/50 dark:hover:bg-slate-800/50 transition-colors">
                        <td className="px-6 py-4 text-sm font-medium text-gray-400 dark:text-gray-400">Paksha</td>
                        <td className="px-6 py-4 text-base text-gray-200 dark:text-gray-200">{panchangaData.panchanga.paksha}</td>
                      </tr>
                    )}

                    {/* Amanta Month */}
                    {panchangaData.panchanga.amanta_month && (
                      <tr className="hover:bg-slate-800/50 dark:hover:bg-slate-800/50 transition-colors">
                        <td className="px-6 py-4 text-sm font-medium text-gray-400 dark:text-gray-400">Amanta Month</td>
                        <td className="px-6 py-4 text-base text-gray-200 dark:text-gray-200">{panchangaData.panchanga.amanta_month}</td>
                      </tr>
                    )}

                    {/* Purnimanta Month */}
                    {panchangaData.panchanga.purnimanta_month && (
                      <tr className="hover:bg-slate-800/50 dark:hover:bg-slate-800/50 transition-colors">
                        <td className="px-6 py-4 text-sm font-medium text-gray-400 dark:text-gray-400">Purnimanta Month</td>
                        <td className="px-6 py-4 text-base text-gray-200 dark:text-gray-200">{panchangaData.panchanga.purnimanta_month}</td>
                      </tr>
                    )}

                    {/* Moon Sign */}
                    {panchangaData.panchanga.moonsign && (
                      <tr className="hover:bg-slate-800/50 dark:hover:bg-slate-800/50 transition-colors">
                        <td className="px-6 py-4 text-sm font-medium text-gray-400 dark:text-gray-400">Moon Sign</td>
                        <td className="px-6 py-4 text-base text-gray-200 dark:text-gray-200">{panchangaData.panchanga.moonsign}</td>
                      </tr>
                    )}

                    {/* Sun Sign */}
                    {panchangaData.panchanga.sunsign && (
                      <tr className="hover:bg-slate-800/50 dark:hover:bg-slate-800/50 transition-colors">
                        <td className="px-6 py-4 text-sm font-medium text-gray-400 dark:text-gray-400">Sun Sign</td>
                        <td className="px-6 py-4 text-base text-gray-200 dark:text-gray-200">{panchangaData.panchanga.sunsign}</td>
                      </tr>
                    )}

                    {/* Shaka Samvat */}
                    {panchangaData.panchanga.shaka_samvat && (
                      <tr className="hover:bg-slate-800/50 dark:hover:bg-slate-800/50 transition-colors">
                        <td className="px-6 py-4 text-sm font-medium text-gray-400 dark:text-gray-400">Shaka Samvat</td>
                        <td className="px-6 py-4 text-base text-gray-200 dark:text-gray-200">{panchangaData.panchanga.shaka_samvat}</td>
                      </tr>
                    )}

                    {/* Vikram Samvat */}
                    {panchangaData.panchanga.vikram_samvat && (
                      <tr className="hover:bg-slate-800/50 dark:hover:bg-slate-800/50 transition-colors">
                        <td className="px-6 py-4 text-sm font-medium text-gray-400 dark:text-gray-400">Vikram Samvat</td>
                        <td className="px-6 py-4 text-base text-gray-200 dark:text-gray-200">{panchangaData.panchanga.vikram_samvat}</td>
                      </tr>
                    )}

                    {/* Gujarati Samvat */}
                    {panchangaData.panchanga.gujarati_samvat && (
                      <tr className="hover:bg-slate-800/50 dark:hover:bg-slate-800/50 transition-colors">
                        <td className="px-6 py-4 text-sm font-medium text-gray-400 dark:text-gray-400">Gujarati Samvat</td>
                        <td className="px-6 py-4 text-base text-gray-200 dark:text-gray-200">{panchangaData.panchanga.gujarati_samvat}</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </SlideUp>
        )}
      </div>
    </div>
  );
}
