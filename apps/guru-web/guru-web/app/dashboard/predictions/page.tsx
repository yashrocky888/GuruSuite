'use client';

/**
 * Guru Predictions — DAILY ONLY
 * Calls POST /api/v1/predict with timescale "daily". Full dark theme.
 * Renders the FULL response.guidance string exactly as returned — no split, no truncate, no section whitelist.
 */

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowLeftIcon, ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline';
import { useBirthStore } from '@/store/useBirthStore';
import { getPredict } from '@/services/api';
import type { BirthDetails } from '@/services/api';

const TIMESCALE = 'daily' as const;

export default function PredictionsPage() {
  const { birthDetails, hasHydrated } = useBirthStore();
  const [seekerName, setSeekerName] = useState<string>('');
  const [guidance, setGuidance] = useState<string>('');
  const [structured, setStructured] = useState<Record<string, string> | null>(null);
  const [technicalBreakdown, setTechnicalBreakdown] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [accordionOpen, setAccordionOpen] = useState(false);
  const [nameForFetch, setNameForFetch] = useState<string>('');

  useEffect(() => {
    if (!hasHydrated || !birthDetails?.name?.trim()) return;
    setSeekerName((prev) => (prev.trim() === '' ? birthDetails.name!.trim() : prev));
  }, [hasHydrated, birthDetails?.name]);

  useEffect(() => {
    if (!seekerName.trim()) {
      setNameForFetch('');
      return;
    }
    const t = setTimeout(() => setNameForFetch(seekerName.trim()), 400);
    return () => clearTimeout(t);
  }, [seekerName]);

  useEffect(() => {
    if (typeof window === 'undefined' || !hasHydrated || !birthDetails || !nameForFetch) return;

    const fetchPrediction = async () => {
      setLoading(true);
      setError(null);
      setStructured(null);
      try {
        const data = await getPredict(birthDetails as BirthDetails, TIMESCALE, nameForFetch);
        const g = data.message ?? data.guidance ?? '';
        setGuidance(g);
        setStructured(data.structured ?? null);
        setTechnicalBreakdown(data.technical_breakdown ?? null);
        if (process.env.NODE_ENV === 'development' && g) {
          console.log('[Predictions] Full guidance length:', g.length, 'has NIRNAYA:', g.includes('NIRNAYA'), 'has SHANTI:', g.includes('SHANTI'));
          console.log('[Predictions] RAW GUIDANCE:', g);
        }
      } catch (err: any) {
        setError(err?.response?.data?.detail || err?.message || 'Failed to load prediction');
        setGuidance('');
        setStructured(null);
        setTechnicalBreakdown(null);
      } finally {
        setLoading(false);
      }
    };

    fetchPrediction();
  }, [hasHydrated, birthDetails, nameForFetch]);

  if (!hasHydrated) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <p className="text-gray-300">Loading...</p>
      </div>
    );
  }

  if (!birthDetails) {
    return (
      <div className="min-h-screen bg-black text-white p-6">
        <Link href="/dashboard" className="inline-flex items-center gap-1 text-gray-300 hover:text-white mb-6">
          <ArrowLeftIcon className="w-4 h-4" /> Back to Dashboard
        </Link>
        <div className="bg-neutral-900 border border-neutral-700 rounded-lg p-6 text-amber-200">
          Birth details are required. Please set your birth details on the dashboard first.
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white p-4 md:p-6">
      <Link href="/dashboard" className="inline-flex items-center gap-1 text-gray-300 hover:text-white mb-6">
        <ArrowLeftIcon className="w-4 h-4" /> Back to Dashboard
      </Link>

      <h1 className="text-2xl font-semibold text-white mb-4">
        {structured?.greeting?.trim() ? `${structured.greeting.trim().split(',')[0]} — Daily Daiva-Jña Reading` : 'Guru Guidance'}
      </h1>

      <div className="mb-6">
        <label htmlFor="seeker-name" className="block text-sm font-medium text-gray-300 mb-1">
          Your Name <span className="text-amber-400">*</span>
        </label>
        <input
          id="seeker-name"
          type="text"
          required
          value={seekerName}
          onChange={(e) => setSeekerName(e.target.value)}
          placeholder="Enter your name"
          className="w-full max-w-xs px-3 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white placeholder-gray-500 focus:ring-2 focus:ring-amber-500/30 focus:border-amber-500"
        />
      </div>

      <h2 className="text-lg font-semibold text-white mb-4">Daily Guidance</h2>

      {error && (
        <div className="mb-6 p-4 bg-red-950/50 border border-red-800 rounded-lg text-red-200 text-sm">
          {error}
        </div>
      )}

      <div
        className="bg-neutral-900 border border-neutral-800 rounded-xl shadow-sm overflow-hidden mb-6"
        style={{ fontFamily: 'Georgia, "Times New Roman", serif' }}
      >
        <div className="p-6 md:p-8">
          {loading ? (
            <p className="text-gray-400 italic">The Rishi is reflecting...</p>
          ) : guidance ? (
            <div className="text-gray-200 leading-relaxed whitespace-pre-wrap pb-6 space-y-2 [&_ul]:pl-5 [&_ol]:pl-5 [&_li]:py-0.5">{guidance}</div>
          ) : !nameForFetch ? (
            <p className="text-gray-400 italic">Enter your name above to receive guidance.</p>
          ) : !error ? (
            <p className="text-gray-400 italic">No guidance available.</p>
          ) : null}
        </div>

        {technicalBreakdown && (
          <div className="border-t border-neutral-800">
            <button
              onClick={() => setAccordionOpen(!accordionOpen)}
              className="w-full flex items-center justify-between px-6 py-4 text-left text-sm font-medium text-gray-300 hover:bg-neutral-800"
            >
              <span>Technical breakdown (Shadbala / Dasha / Bindus)</span>
              {accordionOpen ? (
                <ChevronUpIcon className="w-5 h-5 text-gray-400" />
              ) : (
                <ChevronDownIcon className="w-5 h-5 text-gray-400" />
              )}
            </button>
            {accordionOpen && (
              <div className="px-6 pb-6 pt-0">
                <pre className="text-xs text-gray-400 bg-neutral-800 p-4 rounded-lg overflow-x-auto max-h-80 overflow-y-auto font-mono">
                  {JSON.stringify(technicalBreakdown, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
