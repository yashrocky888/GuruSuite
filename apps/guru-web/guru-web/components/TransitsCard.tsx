'use client';

/**
 * TransitsCard — Transit Activation of Yogas (read-only from API).
 * Renders ONLY on /transits page. Backend is single source of truth.
 * - Active / Dormant yogas
 * - Ashtakavarga Bindus (X / 8) ONLY here
 * - Next 5-Year Activation Calendar (collapsed)
 */

import React, { useState } from 'react';
import { ChevronDownIcon, ChevronUpIcon, SparklesIcon } from '@heroicons/react/24/outline';

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

interface TransitsCardProps {
  transitActivation: YogaActivationItem[];
  forecast: ForecastItem[];
  error: string | null;
}

function qualityLabel(quality: string | null | undefined): string {
  if (!quality) return '—';
  if (quality === 'Kashta') return 'Kashta (0–3)';
  if (quality === 'Sama') return 'Sama (4)';
  if (quality === 'Shubha') return 'Shubha (5–8)';
  return quality;
}

export default function TransitsCard({ transitActivation, forecast, error }: TransitsCardProps) {
  const [showForecast, setShowForecast] = useState(false);

  if (error) {
    return (
      <div className="rounded-xl p-6 border border-red-500/20 bg-red-500/5 text-red-600 dark:text-red-400">
        {error}
      </div>
    );
  }

  const active = transitActivation.filter((y) => y.status === 'Active');
  const dormant = transitActivation.filter((y) => y.status === 'Dormant');

  return (
    <div className="rounded-xl p-6 border border-white/20 bg-white/5 dark:bg-slate-800/50 shadow-lg">
      <div className="flex items-center gap-2 mb-4">
        <SparklesIcon className="w-6 h-6 text-amber-500" />
        <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
          Transit Activation of Yogas
        </h2>
      </div>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
        Dasha grants permission; transit gives timing. Ashtakavarga (bindus) indicates comfort only.
      </p>

      {/* Active / Dormant */}
      <div className="grid gap-4 mb-4">
        {active.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-emerald-600 dark:text-emerald-400 mb-2">
              Active
            </h3>
            <ul className="space-y-2">
              {active.map((y, i) => (
                <li
                  key={`active-${i}`}
                  className="flex flex-wrap items-center gap-2 text-gray-700 dark:text-gray-300"
                >
                  <span className="font-medium">{y.yoga_name}</span>
                  {y.trigger_planet && (
                    <span className="text-xs text-gray-500">({y.trigger_planet})</span>
                  )}
                  {y.bindus != null && (
                    <span className="text-xs px-2 py-0.5 rounded bg-amber-500/20 text-amber-700 dark:text-amber-300">
                      {y.bindus} / 8 bindus
                    </span>
                  )}
                  {y.quality && (
                    <span className="text-xs text-gray-500">{qualityLabel(y.quality)}</span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
        {dormant.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
              Dormant
            </h3>
            <ul className="space-y-1">
              {dormant.map((y, i) => (
                <li
                  key={`dormant-${i}`}
                  className="text-sm text-gray-600 dark:text-gray-400"
                >
                  {y.yoga_name}
                  {y.reason && (
                    <span className="text-xs text-gray-500 ml-1">— {y.reason}</span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
        {transitActivation.length === 0 && (
          <p className="text-sm text-gray-500 dark:text-gray-400">
            No natal yogas in scope, or enter birth details to see activation.
          </p>
        )}
      </div>

      {/* Next 5-Year Activation Calendar (collapsed) */}
      <div className="border-t border-white/10 pt-4">
        <button
          type="button"
          onClick={() => setShowForecast(!showForecast)}
          className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-purple-600 dark:hover:text-purple-400"
        >
          Next 5-Year Activation Calendar
          {showForecast ? (
            <ChevronUpIcon className="w-4 h-4" />
          ) : (
            <ChevronDownIcon className="w-4 h-4" />
          )}
        </button>
        {showForecast && (
          <div className="mt-3 space-y-2 max-h-64 overflow-y-auto">
            {forecast.length === 0 ? (
              <p className="text-sm text-gray-500 dark:text-gray-400">
                No activation windows in the next 5 years for current yogas.
              </p>
            ) : (
              forecast.slice(0, 30).map((f, i) => (
                <div
                  key={`f-${i}`}
                  className="text-xs text-gray-600 dark:text-gray-400 flex flex-wrap gap-2"
                >
                  <span className="font-medium text-gray-700 dark:text-gray-300">
                    {f.yoga_name}
                  </span>
                  <span>{f.date_approx}</span>
                  <span>{f.trigger_planet}</span>
                  {f.bindus != null && <span>{f.bindus}/8</span>}
                  {f.activation_type && (
                    <span
                      className={
                        f.activation_type === 'MAJOR_ACTIVATION'
                          ? 'text-amber-600 dark:text-amber-400'
                          : ''
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
