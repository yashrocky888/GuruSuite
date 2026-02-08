'use client';

/**
 * Dashboard Transit Activation Card (Secondary Switch).
 * Renders ONLY on Dashboard. Backend is single source of truth.
 * - Current activation (Active / Dormant), trigger planet, one-line reason
 * - Ashtakavarga strength for Active yogas only (X/8, SHUBHA/SAMA/KASHTA)
 * - Next 100-Year Activation Outlook (collapsed, lazy-loaded when expanded)
 * Philosophy: "Dasha grants permission. Transit gives timing. Ashtakavarga decides comfort."
 */

import React, { useState, useCallback } from 'react';
import { ChevronDownIcon, ChevronUpIcon, SparklesIcon, InformationCircleIcon } from '@heroicons/react/24/outline';
import { getYogaActivation } from '@/services/api';

export interface YogaActivationItem {
  yoga_name: string;
  status: 'Active' | 'Dormant';
  reason?: string;
  dasha_md?: string;
  dasha_ad?: string;
  participants?: string[];
  bindus?: number | null;
  quality?: string | null;
  trigger_planet?: string | null;
  transit_sign?: number | null;
}

export interface ForecastItem {
  yoga_name: string;
  window_start: string;
  window_end: string;
  date_approx: string;
  trigger_planet: string;
  activation_type: string;
  bindus?: number | null;
  dasha_md?: string;
  dasha_ad?: string;
}

interface DashboardTransitActivationCardProps {
  birthDetails: {
    date: string;
    time: string;
    latitude: number;
    longitude: number;
    timezone?: string;
  } | null;
}

function qualityLabel(quality: string | null | undefined): string {
  if (!quality) return '—';
  if (quality === 'Kashta') return 'Kashta (0–3)';
  if (quality === 'Sama') return 'Sama (4)';
  if (quality === 'Shubha') return 'Shubha (5–8)';
  return quality;
}

export default function DashboardTransitActivationCard({ birthDetails }: DashboardTransitActivationCardProps) {
  const [transitActivation, setTransitActivation] = useState<YogaActivationItem[]>([]);
  const [forecast, setForecast] = useState<ForecastItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [showForecast, setShowForecast] = useState(false);
  const [loadingForecast, setLoadingForecast] = useState(false);
  const [forecastLoaded, setForecastLoaded] = useState(false);

  // Fetch summary on mount when birthDetails present
  React.useEffect(() => {
    if (!birthDetails?.date || !birthDetails?.time || birthDetails?.latitude == null || birthDetails?.longitude == null) {
      setTransitActivation([]);
      setError(null);
      return;
    }
    let cancelled = false;
    setLoadingSummary(true);
    setError(null);
    getYogaActivation({
      dob: birthDetails.date,
      time: birthDetails.time,
      lat: birthDetails.latitude,
      lon: birthDetails.longitude,
      timezone: birthDetails.timezone || 'Asia/Kolkata',
      mode: 'summary',
    })
      .then((res) => {
        if (cancelled) return;
        setTransitActivation(res.transit_activation || []);
        setError(res.error || null);
      })
      .catch((err) => {
        if (cancelled) return;
        setTransitActivation([]);
        setError(err?.message || 'Failed to load activation');
      })
      .finally(() => {
        if (!cancelled) setLoadingSummary(false);
      });
    return () => { cancelled = true; };
  }, [birthDetails?.date, birthDetails?.time, birthDetails?.latitude, birthDetails?.longitude, birthDetails?.timezone]);

  // Lazy-load 100-year forecast when section expanded
  const loadForecast = useCallback(() => {
    if (!birthDetails?.date || !birthDetails?.time || birthDetails?.latitude == null || birthDetails?.longitude == null || forecastLoaded) return;
    setLoadingForecast(true);
    getYogaActivation({
      dob: birthDetails.date,
      time: birthDetails.time,
      lat: birthDetails.latitude,
      lon: birthDetails.longitude,
      timezone: birthDetails.timezone || 'Asia/Kolkata',
      mode: 'forecast',
      years: 100,
    })
      .then((res) => {
        setForecast(res.forecast || []);
        setForecastLoaded(true);
      })
      .catch(() => setForecast([]))
      .finally(() => setLoadingForecast(false));
  }, [birthDetails, forecastLoaded]);

  const onToggleForecast = () => {
    const next = !showForecast;
    setShowForecast(next);
    if (next) loadForecast();
  };

  if (!birthDetails) {
    return (
      <div className="rounded-xl p-6 border border-white/20 bg-white/5 dark:bg-slate-800/50">
        <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2">
          Transit Activation (Secondary Switch)
        </h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Enter birth details to see yoga activation.
        </p>
      </div>
    );
  }

  if (loadingSummary) {
    return (
      <div className="rounded-xl p-6 border border-white/20 bg-white/5 dark:bg-slate-800/50">
        <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2">
          Transit Activation (Secondary Switch)
        </h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">Loading…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl p-6 border border-red-500/20 bg-red-500/5 text-red-600 dark:text-red-400">
        <h2 className="text-xl font-semibold mb-2">Transit Activation (Secondary Switch)</h2>
        <p>{error}</p>
      </div>
    );
  }

  const active = transitActivation.filter((y) => y.status === 'Active');
  const dormant = transitActivation.filter((y) => y.status === 'Dormant');

  return (
    <div className="rounded-xl p-6 border border-white/20 bg-white/5 dark:bg-slate-800/50 shadow-lg">
      <div className="flex items-center gap-2 mb-2">
        <SparklesIcon className="w-6 h-6 text-amber-500" />
        <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
          Transit Activation (Secondary Switch)
        </h2>
        <span
          className="text-gray-400 cursor-help"
          title="Dasha grants permission. Transit gives timing. Ashtakavarga decides comfort."
        >
          <InformationCircleIcon className="w-5 h-5" />
        </span>
      </div>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
        Dasha grants permission. Transit gives timing. Ashtakavarga decides comfort.
      </p>

      {/* A) Current activation */}
      <div className="grid gap-4 mb-4">
        {active.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-emerald-600 dark:text-emerald-400 mb-2">Active</h3>
            <ul className="space-y-2">
              {active.map((y, i) => (
                <li key={`active-${i}`} className="flex flex-wrap items-center gap-2 text-gray-700 dark:text-gray-300">
                  <span className="font-medium">{y.yoga_name}</span>
                  {y.trigger_planet && (
                    <span className="text-xs text-gray-500">
                      ({y.trigger_planet} activating during {y.dasha_md} Mahadasha / {y.dasha_ad} Antardasha)
                    </span>
                  )}
                  {y.bindus != null && (
                    <span className="text-xs px-2 py-0.5 rounded bg-amber-500/20 text-amber-700 dark:text-amber-300">
                      {y.bindus} / 8 bindus
                    </span>
                  )}
                  {y.quality && (
                    <span className="text-xs text-gray-500" title="Ashtakavarga decides comfort, not existence.">
                      {qualityLabel(y.quality)}
                    </span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
        {dormant.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Dormant</h3>
            <ul className="space-y-1">
              {dormant.map((y, i) => (
                <li key={`dormant-${i}`} className="text-sm text-gray-600 dark:text-gray-400">
                  {y.yoga_name}
                  {y.reason && <span className="text-xs text-gray-500 ml-1">— {y.reason}</span>}
                </li>
              ))}
            </ul>
          </div>
        )}
        {transitActivation.length === 0 && (
          <p className="text-sm text-gray-500 dark:text-gray-400">
            No natal yogas in scope, or no activation at this time.
          </p>
        )}
      </div>

      {/* C) Next 100-Year Activation Outlook (collapsed, lazy-load) */}
      <div className="border-t border-white/10 pt-4">
        <button
          type="button"
          onClick={onToggleForecast}
          className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-purple-600 dark:hover:text-purple-400"
        >
          Next 100-Year Activation Outlook
          {showForecast ? <ChevronUpIcon className="w-4 h-4" /> : <ChevronDownIcon className="w-4 h-4" />}
        </button>
        {showForecast && (
          <div className="mt-3 space-y-2 max-h-64 overflow-y-auto">
            {loadingForecast ? (
              <p className="text-sm text-gray-500 dark:text-gray-400">Loading forecast…</p>
            ) : forecast.length === 0 ? (
              <p className="text-sm text-gray-500 dark:text-gray-400">
                No activation windows in the next 100 years for current yogas.
              </p>
            ) : (
              forecast.slice(0, 50).map((f, i) => (
                <div key={`f-${i}`} className="text-xs text-gray-600 dark:text-gray-400 flex flex-wrap gap-2">
                  <span className="font-medium text-gray-700 dark:text-gray-300">{f.yoga_name}</span>
                  <span>{f.date_approx}</span>
                  <span>{f.trigger_planet}</span>
                  {f.bindus != null && <span>{f.bindus}/8</span>}
                  {f.activation_type && (
                    <span
                      className={
                        f.activation_type === 'MAJOR_ACTIVATION' ? 'text-amber-600 dark:text-amber-400' : ''
                      }
                    >
                      {f.activation_type}
                    </span>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
