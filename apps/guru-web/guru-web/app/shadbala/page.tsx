'use client';

/**
 * Shadbala Page
 * Displays Sixfold Planetary Strength (Shadbala)
 * Render-only - No calculations, No AI
 */

import { useEffect, useState } from 'react';
import { ChartBarIcon, InformationCircleIcon, ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline';
import { FadeIn, SlideUp } from '@/frontend/animations';
import { getShadbala, getYogas, getYogasTimeline } from '@/services/api';
import { useBirthStore } from '@/store/useBirthStore';
import { useMaxLoadTime } from '@/hooks/useMaxLoadTime';

interface ShadbalaData {
  [planet: string]: {
    naisargika_bala: number;
    cheshta_bala: number;
    sthana_bala: number;
    sthana_bala_components?: {
      uchcha_bala: number;
      saptavargaja_bala: number;
      ojhayugmarasiamsa_bala: number;
      kendradi_bala: number;
      drekkana_bala: number;
    };
    dig_bala: number;
    kala_bala: number;
    kala_bala_components?: {
      nathonnatha_bala: number;
      paksha_bala: number;
      tribhaga_bala: number;
      varsha_bala: number;
      masa_bala: number;
      dina_bala: number;
      hora_bala: number;
      ayana_bala: number;
    };
    drik_bala: number;
    total_shadbala: number;
    shadbala_in_rupas: number;
    relative_rank: number;
    ratio?: number;
    status?: string;
  };
}

interface ShadbalaResponse {
  calculation_mode?: string;
  config?: {
    kendradi_scale: number;
    dig_bala_sun_multiplier: number;
    saptavargaja_divisor: number;
  };
  shadbala: ShadbalaData;
  birth_details?: {
    date: string;
    time: string;
    latitude: number;
    longitude: number;
    timezone?: string;
  };
}

interface YogaStrengthBreakdown {
  avg_shadbala_ratio: number;
  house_multiplier: number;
  degree_multiplier: number;
  vargottama_applied: boolean;
  cutoff?: {
    threshold: number;
    failed_planets: string[];
  };
}

interface YogaActivation {
  state: "Jāgrata" | "Swapna" | "Supta";
  state_label?: string;
  is_active_now: boolean;
  manifestation_score: number;
  connected_lords: {
    mahadasha: string | null;
    antardasha: string | null;
  };
}

interface NeechaBhangaData {
  is_rescued: boolean;
  rules_met: string[];
}

interface YogaItem {
  yoga_name: string;
  category: string;
  planets_involved: string[];
  formation_house: number | null;
  potency_percent: number;
  status_label: string;
  is_triggered: boolean;
  formation_logic?: string;
  formation_basis?: string;
  explanation: string;
  strength_breakdown: YogaStrengthBreakdown;
  activation?: YogaActivation;
  neecha_bhanga_data?: NeechaBhangaData;
}

interface YogaResponse {
  calculation_mode: string;
  chart_scope: string[];
  yogas: YogaItem[];
  transparency_note?: string;
}

interface YogaTimelineRow {
  start_date: string;
  end_date: string;
  state: "Jāgrata" | "Swapna" | "Supta";
  state_label: string;
  manifestation_score: number;
  dasha_period: string;
}

interface YogaTimelineItem {
  yoga_name: string;
  timeline: YogaTimelineRow[];
}

interface YogasTimelineResponse {
  birth_range: {
    from: string;
    to: string;
  };
  yogas: YogaTimelineItem[];
}

// Shadbala row order
const SHADBALA_ROWS = [
  { key: 'sthana_bala', label: 'Sthana Bala', isBold: true },
  { key: 'dig_bala', label: 'Dig Bala' },
  { key: 'kala_bala', label: 'Kala Bala' },
  { key: 'cheshta_bala', label: 'Cheshta Bala' },
  { key: 'naisargika_bala', label: 'Naisargika Bala' },
  { key: 'drik_bala', label: 'Drik Bala' },
  { key: 'total_shadbala', label: 'Total (Virupas)', isBold: true },
  { key: 'shadbala_in_rupas', label: 'Rupas', isBold: true },
  { key: 'relative_rank', label: 'Rank', isBold: true },
];

// Planet order (standard: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn)
const PLANET_ORDER = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'];

// Tooltip definitions for each Bala component
const BALA_TOOLTIPS: { [key: string]: string } = {
  sthana_bala: "Positional strength of the planet based on dignity, exaltation, divisional charts and house placement, calculated strictly as per BPHS.",
  dig_bala: "Directional strength of the planet based on its angular distance from the weakest direction, calculated using Bhava geometry as per BPHS.",
  kala_bala: "Time-based strength derived from day/night strength, lunar phase, ayana (declination), and other temporal factors defined in BPHS.",
  cheshta_bala: "Motional strength based on planetary speed and retrograde motion. Retrograde planets receive higher Cheshta Bala as per BPHS.",
  naisargika_bala: "Inherent natural strength of the planet fixed by BPHS and independent of chart position.",
  drik_bala: "Aspect-based strength caused by benefic and malefic aspects from other planets. Positive values indicate benefic influence; negative values indicate affliction.",
  total_shadbala: "Sum of all six strengths as defined in Bṛhat Parāśara Horā Śāstra (BPHS)."
};

const YOGA_TOOLTIPS: { [key: string]: string } = {
  potency_percent: "Yoga Potency (%) calculated strictly as per BPHS using D1, D9 and Shadbala ratios. No interpretive scaling.",
  formation: "Formation conditions are checked using pure D1 positional rules as per BPHS (no heuristics).",
  strength: "Strength is gated by Shadbala ratio cutoff and computed as Yoga‑Pinda strictly as per BPHS (Base × House × Degree × Vargottama).",
  explanation: "Calculated strictly as per BPHS (Bṛhat Parāśara Horā Śāstra).",
  activation: "Yoga activation depends on Mahadasha–Antardasha sambandha as per BPHS."
};

const MONTHS_SHORT: Record<string, string> = {
  "01": "Jan",
  "02": "Feb",
  "03": "Mar",
  "04": "Apr",
  "05": "May",
  "06": "Jun",
  "07": "Jul",
  "08": "Aug",
  "09": "Sep",
  "10": "Oct",
  "11": "Nov",
  "12": "Dec",
};

function formatIsoDateForDisplay(isoDate: string): string {
  // Render-only formatting of an ISO date (YYYY-MM-DD) into "DD Mon YYYY"
  // This does not change the underlying date; it is presentation only.
  const parts = (isoDate || "").split("-");
  if (parts.length !== 3) return isoDate;
  const [yyyy, mm, dd] = parts;
  const mon = MONTHS_SHORT[mm] || mm;
  return `${dd} ${mon} ${yyyy}`;
}

function stripInternalTokens(raw: string): string {
  // UI-only sanitization to prevent leaking internal calculation/debug tokens.
  // No astrology logic. No derived computations. String cleanup only.
  let t = raw || "";

  // Remove any content after a semicolon (debug trailers often append here)
  const semi = t.indexOf(";");
  if (semi !== -1) t = t.slice(0, semi);

  // Remove any content after known debug selectors
  const selectedIdx = t.indexOf("Selected:");
  if (selectedIdx !== -1) t = t.slice(0, selectedIdx);

  // Remove known internal tokens / indices
  t = t.replace(/dist_from_lagna\s*=\s*\d+/gi, "");
  t = t.replace(/\b(?:[A-Za-z]+\s+)?sign\s*=\s*\d+\b/gi, "");
  t = t.replace(/\bhouse\s*=\s*\d+\b/gi, "");
  t = t.replace(/\bhouse\s+\d+\b/gi, "");

  // Remove math-like parenthetical fragments (e.g., "(x=7, y=3)")
  t = t.replace(/\([^)]*=\s*\d+[^)]*\)/g, "");

  // Remove generic key=value tokens and snake_case identifiers
  t = t.replace(/\b[a-zA-Z_]+\s*=\s*[a-zA-Z0-9_]+\b/g, "");
  t = t.replace(/\b[a-zA-Z_]+\s*=\s*-?\d+(?:\.\d+)?\b/g, "");
  t = t.replace(/\b[a-z]+(?:_[a-z0-9]+)+\b/g, "");

  // Normalize whitespace/punctuation fallout
  t = t.replace(/\s{2,}/g, " ");
  t = t.replace(/\s+,/g, ",");
  t = t.replace(/,\s*,/g, ",");
  t = t.replace(/,\s*\./g, ".");
  t = t.replace(/\s+\./g, ".");
  t = t.replace(/\(\s+/g, "(");
  t = t.replace(/\s+\)/g, ")");
  return t.trim();
}

function sanitizeFormationLogic(raw?: string): string | null {
  if (!raw) return null;

  let t = stripInternalTokens(raw);

  // Small readability transforms (string-only), aligned with required examples
  t = t.replace(/\bown\/exaltation\b/gi, "own or exaltation");
  t = t.replace(/\bJupiter in Kendra from Moon\b/gi, "Jupiter in a Kendra from the Moon");
  t = t.replace(/\(sign-count:\s*1\s*\/\s*4\s*\/\s*7\s*\/\s*10\s*\)/gi, "(1st, 4th, 7th, or 10th)");

  // Convert slash-separated lists inside parentheses into a human list, excluding D1/D9 forms
  t = t.replace(/\(([^()]*\/[^()]*)\)/g, (_full, inner: string) => {
    if (/D\d\s*\/\s*D\d/i.test(inner)) {
      return `(${inner.replace(/\s*\/\s*/g, " and ")})`;
    }
    const parts = inner
      .split("/")
      .map((p) => p.trim())
      .filter(Boolean);
    if (parts.length <= 1) return `(${inner})`;
    if (parts.length === 2) return `(${parts[0]} or ${parts[1]})`;
    const last = parts[parts.length - 1];
    const head = parts.slice(0, -1).join(", ");
    return `(${head}, or ${last})`;
  });

  // Trim trailing punctuation artifacts
  t = t.replace(/[;,:]+$/g, "").trim();
  t = t.replace(/\.*$/g, "").trim();
  if (!t) return null;

  // Ensure a clean sentence ending
  return `${t}.`;
}

// Tooltip component
function Tooltip({ text, children }: { text: string; children: React.ReactNode }) {
  const [showTooltip, setShowTooltip] = useState(false);
  
  return (
    <div className="relative inline-flex items-center">
      <div
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        onTouchStart={() => setShowTooltip(!showTooltip)}
        className="cursor-help"
      >
        {children}
      </div>
      {showTooltip && (
        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 z-50 pointer-events-none">
          <div className="bg-gray-900 dark:bg-gray-700 text-white text-xs rounded-lg py-2 px-3 max-w-xs shadow-lg whitespace-normal">
            {text}
            <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
              <div className="border-4 border-transparent border-t-gray-900 dark:border-t-gray-700"></div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Status badge component with color coding
function StatusBadge({ status }: { status?: string }) {
  if (!status) return null;
  
  const statusConfig: { [key: string]: { color: string; bgColor: string } } = {
    "Very Strong": {
      color: "text-green-800 dark:text-green-200",
      bgColor: "bg-green-100 dark:bg-green-900/30 border-green-300 dark:border-green-700"
    },
    "Strong": {
      color: "text-green-700 dark:text-green-300",
      bgColor: "bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800"
    },
    "Average": {
      color: "text-amber-700 dark:text-amber-300",
      bgColor: "bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800"
    },
    "Weak": {
      color: "text-red-700 dark:text-red-300",
      bgColor: "bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800"
    }
  };
  
  const config = statusConfig[status] || statusConfig["Average"];
  
  return (
    <Tooltip text="Derived from BPHS minimum strength requirements (Ratio of actual Shadbala to canonical minimum).">
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${config.color} ${config.bgColor}`}>
        {status}
      </span>
    </Tooltip>
  );
}

function YogaStatusBadge({ status }: { status: string }) {
  const statusConfig: Record<string, { color: string; bgColor: string }> = {
    "Siddha": {
      color: "text-green-800 dark:text-green-200",
      bgColor: "bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800"
    },
    "Siddha (Rescued)": {
      color: "text-green-800 dark:text-green-200",
      bgColor: "bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800"
    },
    "Madhya": {
      color: "text-yellow-800 dark:text-yellow-200",
      bgColor: "bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800"
    },
    "Alpa": {
      color: "text-orange-800 dark:text-orange-200",
      bgColor: "bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800"
    },
    "Mṛta": {
      color: "text-red-800 dark:text-red-200",
      bgColor: "bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800"
    },
    "Mṛta (Inactive)": {
      color: "text-gray-700 dark:text-gray-300",
      bgColor: "bg-gray-100 dark:bg-gray-800 border-gray-300 dark:border-gray-700"
    }
  };

  const config = statusConfig[status] || statusConfig["Mṛta"];

  return (
    <Tooltip
      text={
        status === "Siddha (Rescued)"
          ? "Debilitation cancelled as per BPHS (Neecha Bhanga Raja Yoga). Results manifest during appropriate Dashas."
          : YOGA_TOOLTIPS.explanation
      }
    >
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${config.color} ${config.bgColor}`}>
        {status}
      </span>
    </Tooltip>
  );
}

function ActivationBadge({ activation }: { activation?: YogaActivation }) {
  if (!activation) return null;

  const config: Record<string, { label: string; color: string; bg: string; extra?: string }> = {
    "Jāgrata": {
      label: "Jāgrata",
      color: "text-green-800 dark:text-green-200",
      bg: "bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800",
      extra: "shadow-sm shadow-green-200/50 dark:shadow-green-900/30"
    },
    "Swapna": {
      label: "Swapna",
      color: "text-amber-800 dark:text-amber-200",
      bg: "bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800"
    },
    "Supta": {
      label: "Supta",
      color: "text-gray-700 dark:text-gray-300",
      bg: "bg-gray-100 dark:bg-gray-800 border-gray-300 dark:border-gray-700"
    }
  };

  const c = config[activation.state] || config["Supta"];
  const label = activation.state_label || c.label;

  return (
    <Tooltip text={YOGA_TOOLTIPS.activation}>
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${c.color} ${c.bg} ${c.extra || ""}`}>
        {label}
      </span>
    </Tooltip>
  );
}

function TimelineActivationBadge({ state, label }: { state: YogaTimelineRow["state"]; label: string }) {
  const config: Record<YogaTimelineRow["state"], { color: string; bg: string }> = {
    "Jāgrata": {
      color: "text-green-800 dark:text-green-200",
      bg: "bg-green-50 dark:bg-green-900/15 border-green-200 dark:border-green-800"
    },
    "Swapna": {
      color: "text-amber-800 dark:text-amber-200",
      bg: "bg-amber-50 dark:bg-amber-900/15 border-amber-200 dark:border-amber-800"
    },
    "Supta": {
      color: "text-gray-700 dark:text-gray-300",
      bg: "bg-gray-100 dark:bg-gray-800/60 border-gray-300 dark:border-gray-700"
    }
  };

  const c = config[state] || config["Supta"];

  return (
    <Tooltip text={YOGA_TOOLTIPS.activation}>
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border ${c.color} ${c.bg}`}>
        {label}
      </span>
    </Tooltip>
  );
}

export default function ShadbalaPage() {
  const { birthDetails, hasHydrated } = useBirthStore();
  const [shadbalaData, setShadbalaData] = useState<ShadbalaResponse | null>(null);
  const [yogaData, setYogaData] = useState<YogaResponse | null>(null);
  const [yogaTimeline, setYogaTimeline] = useState<YogasTimelineResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedPlanets, setExpandedPlanets] = useState<Set<string>>(new Set());
  const [expandedYogas, setExpandedYogas] = useState<Set<string>>(new Set());
  
  const togglePlanet = (planet: string) => {
    setExpandedPlanets(prev => {
      const newSet = new Set(prev);
      if (newSet.has(planet)) {
        newSet.delete(planet);
      } else {
        newSet.add(planet);
      }
      return newSet;
    });
  };

  const toggleYoga = (yogaName: string) => {
    setExpandedYogas(prev => {
      const newSet = new Set(prev);
      if (newSet.has(yogaName)) {
        newSet.delete(yogaName);
      } else {
        newSet.add(yogaName);
      }
      return newSet;
    });
  };

  // 🔒 HYDRATION FIX: Ensure store is marked hydrated on mount
  useEffect(() => {
    useBirthStore.setState({ hasHydrated: true });
  }, []);

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
    // 🔒 RACE CONDITION FIX: Client-side only
    if (typeof window === 'undefined') return;

    // 🔒 RACE CONDITION FIX: Hydration complete
    if (!hasHydrated) return;

    const fetchShadbalaYogasAndTimeline = async () => {
      try {
        setLoading(true);
        setError(null);

        if (!birthDetails) {
          throw new Error('Birth details not available');
        }

        // Parse birth date and time
        const birthDate = birthDetails.date || '';
        const birthTime = birthDetails.time || '00:00';
        const lat = birthDetails.latitude || 0;
        const lon = birthDetails.longitude || 0;
        const tz = birthDetails.timezone || 'Asia/Kolkata';

        if (!birthDate) {
          throw new Error('Birth date is required');
        }

        const [shadbalaResult, yogaResult, timelineResult] = await Promise.allSettled([
          getShadbala(birthDate, birthTime, lat, lon, tz),
          getYogas(birthDate, birthTime, lat, lon, tz),
          getYogasTimeline(birthDate, birthTime, lat, lon, tz),
        ]);

        if (shadbalaResult.status === 'fulfilled') {
          const data = shadbalaResult.value;
          // 🔒 HARD FAILSAFE: Validate data
          if (!data || !data.shadbala) {
            throw new Error("API returned invalid Shadbala response");
          }
          setShadbalaData(data);
        } else {
          throw shadbalaResult.reason;
        }

        if (yogaResult.status === 'fulfilled') {
          const y = yogaResult.value;
          if (y && Array.isArray(y.yogas)) {
            setYogaData(y);
          } else {
            // Keep Yoga section gracefully empty if response is malformed
            setYogaData(null);
          }
        } else {
          // Yoga is optional display; do not block Shadbala rendering
          setYogaData(null);
        }

        if (timelineResult.status === 'fulfilled') {
          const t = timelineResult.value;
          if (t && t.birth_range && Array.isArray(t.yogas)) {
            setYogaTimeline(t);
          } else {
            setYogaTimeline(null);
          }
        } else {
          // Timeline is optional display; do not block Shadbala rendering
          setYogaTimeline(null);
        }

      } catch (err: any) {
        console.error("🔍 SHADBALA FETCH ERROR", err);
        setError(err.message || 'Failed to load Shadbala');
      } finally {
        setLoading(false);
      }
    };

    fetchShadbalaYogasAndTimeline();
  }, [birthDetails, hasHydrated]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-purple-50/30 to-blue-50/30 dark:from-slate-900 dark:via-purple-900/20 dark:to-blue-900/20">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading Shadbala...</p>
          <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">This will timeout after 8 seconds</p>
        </div>
      </div>
    );
  }

  // 🔒 HARD FAILSAFE: Show error if no data
  if (error && !shadbalaData) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-purple-50/30 to-blue-50/30 dark:from-slate-900 dark:via-purple-900/20 dark:to-blue-900/20">
        <div className="text-center max-w-md">
          <div className="p-6 rounded-lg bg-red-500/10 border border-red-500/20">
            <p className="text-red-600 dark:text-red-400">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!shadbalaData || !shadbalaData.shadbala) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50/30 to-blue-50/30 dark:from-slate-900 dark:via-purple-900/20 dark:to-blue-900/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <FadeIn>
          <div className="text-center mb-12">
            <div className="w-16 h-16 mx-auto rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center mb-4">
              <ChartBarIcon className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-2">
              Shadbala
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Sixfold Planetary Strength
            </p>
            
            {/* Calculation Mode Label */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800">
              <span className="text-sm font-medium text-indigo-700 dark:text-indigo-300">
                Calculation Mode: <span className="font-bold">PURE BPHS</span> (No heuristics)
              </span>
            </div>
            
            {/* Prokerala Compatibility Toggle (Disabled, Visual Only) */}
            <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 opacity-50 cursor-not-allowed">
              <input
                type="checkbox"
                id="prokerala-toggle"
                disabled
                className="w-4 h-4 text-indigo-600 bg-gray-100 border-gray-300 rounded focus:ring-indigo-500 disabled:opacity-50"
              />
              <label htmlFor="prokerala-toggle" className="text-sm text-gray-500 dark:text-gray-400 cursor-not-allowed">
                Prokerala Compatibility Mode
              </label>
            </div>
          </div>
        </FadeIn>

        {error && (
          <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 mb-6">
            {error}
          </div>
        )}

        {/* Shadbala Cards - Enhanced with Primary Focus */}
        <SlideUp delay={0.1}>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {PLANET_ORDER.map((planet) => {
              const planetData = shadbalaData.shadbala[planet];
              if (!planetData) return null;
              
              const total = planetData.total_shadbala || 0;
              const rupas = planetData.shadbala_in_rupas || 0;
              const rank = planetData.relative_rank || 0;
              const isExpanded = expandedPlanets.has(planet);
              
              return (
                <div
                  key={planet}
                  className="glass rounded-xl p-6 border border-white/20 hover:border-white/30 transition-all"
                >
                  {/* PRIMARY FOCUS - Top Section */}
                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-xl font-bold text-gray-800 dark:text-gray-200">
                        {planet}
                      </h3>
                      <button
                        onClick={() => togglePlanet(planet)}
                        className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
                        aria-label={isExpanded ? "Collapse details" : "Expand details"}
                      >
                        {isExpanded ? (
                          <ChevronUpIcon className="w-5 h-5" />
                        ) : (
                          <ChevronDownIcon className="w-5 h-5" />
                        )}
                      </button>
                    </div>
                    
                    {/* Total Shadbala - Most Prominent */}
                    <div className="mb-2">
                      <div className="flex items-baseline gap-2">
                        <span className="text-3xl font-bold text-gray-900 dark:text-gray-100">
                          {total.toFixed(2)}
                        </span>
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          Virupas
                        </span>
                        <Tooltip text={BALA_TOOLTIPS.total_shadbala}>
                          <InformationCircleIcon className="w-4 h-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" />
                        </Tooltip>
                      </div>
                    </div>
                    
                    {/* Rupas, Rank, and Status */}
                    <div className="flex flex-col gap-2 text-sm">
                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-1">
                          <span className="text-gray-600 dark:text-gray-400">Rupas:</span>
                          <span className="font-semibold text-gray-800 dark:text-gray-200">
                            {rupas.toFixed(2)}
                          </span>
                        </div>
                        <div className="flex items-center gap-1">
                          <span className="text-gray-600 dark:text-gray-400">Rank:</span>
                          <span className="font-semibold text-gray-800 dark:text-gray-200">
                            {rank}
                          </span>
                        </div>
                      </div>
                      {/* Status Badge */}
                      <div className="flex items-center">
                        <StatusBadge status={planetData.status} />
                      </div>
                    </div>
                  </div>
                  
                  {/* DETAIL VIEW - Expandable Section */}
                  {isExpanded && (
                    <div className="mt-4 pt-4 border-t border-white/10 space-y-3">
                      <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
                        Component Breakdown
                      </div>
                      
                      {/* Sthana Bala */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1">
                          <span className="text-sm text-gray-700 dark:text-gray-300">Sthana Bala</span>
                          <Tooltip text={BALA_TOOLTIPS.sthana_bala}>
                            <InformationCircleIcon className="w-3.5 h-3.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" />
                          </Tooltip>
                        </div>
                        <span className="text-sm font-mono text-gray-800 dark:text-gray-200">
                          {planetData.sthana_bala?.toFixed(2) || '—'}
                        </span>
                      </div>
                      
                      {/* Dig Bala */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1">
                          <span className="text-sm text-gray-700 dark:text-gray-300">Dig Bala</span>
                          <Tooltip text={BALA_TOOLTIPS.dig_bala}>
                            <InformationCircleIcon className="w-3.5 h-3.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" />
                          </Tooltip>
                        </div>
                        <span className="text-sm font-mono text-gray-800 dark:text-gray-200">
                          {planetData.dig_bala?.toFixed(2) || '—'}
                        </span>
                      </div>
                      
                      {/* Kala Bala */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1">
                          <span className="text-sm text-gray-700 dark:text-gray-300">Kala Bala</span>
                          <Tooltip text={BALA_TOOLTIPS.kala_bala}>
                            <InformationCircleIcon className="w-3.5 h-3.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" />
                          </Tooltip>
                        </div>
                        <span className="text-sm font-mono text-gray-800 dark:text-gray-200">
                          {planetData.kala_bala?.toFixed(2) || '—'}
                        </span>
                      </div>
                      
                      {/* Cheshta Bala */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1">
                          <span className="text-sm text-gray-700 dark:text-gray-300">Cheshta Bala</span>
                          <Tooltip text={BALA_TOOLTIPS.cheshta_bala}>
                            <InformationCircleIcon className="w-3.5 h-3.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" />
                          </Tooltip>
                        </div>
                        <span className="text-sm font-mono text-gray-800 dark:text-gray-200">
                          {planetData.cheshta_bala?.toFixed(2) || '—'}
                        </span>
                      </div>
                      
                      {/* Naisargika Bala */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1">
                          <span className="text-sm text-gray-700 dark:text-gray-300">Naisargika Bala</span>
                          <Tooltip text={BALA_TOOLTIPS.naisargika_bala}>
                            <InformationCircleIcon className="w-3.5 h-3.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" />
                          </Tooltip>
                        </div>
                        <span className="text-sm font-mono text-gray-800 dark:text-gray-200">
                          {planetData.naisargika_bala?.toFixed(2) || '—'}
                        </span>
                      </div>
                      
                      {/* Drik Bala */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1">
                          <span className="text-sm text-gray-700 dark:text-gray-300">Drik Bala</span>
                          <Tooltip text={BALA_TOOLTIPS.drik_bala}>
                            <InformationCircleIcon className="w-3.5 h-3.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" />
                          </Tooltip>
                        </div>
                        <span className="text-sm font-mono text-gray-800 dark:text-gray-200">
                          {planetData.drik_bala?.toFixed(2) || '—'}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
          
          {/* Yoga Cards (Phase 1) */}
          <div className="mt-10">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  Yogas (Phase 1)
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  PURE BPHS • D1 (Rāśi) + D9 (Navāṁśa) • No heuristics
                </p>
              </div>
              <Tooltip text={YOGA_TOOLTIPS.explanation}>
                <InformationCircleIcon className="w-5 h-5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" />
              </Tooltip>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {(yogaData?.yogas || []).map((yoga) => {
                const isExpanded = expandedYogas.has(yoga.yoga_name);
                const planets = (yoga.planets_involved || []).join(', ') || '—';
                const formationText = sanitizeFormationLogic(yoga.formation_logic);
                const safeExplanation = stripInternalTokens(yoga.explanation || "") || YOGA_TOOLTIPS.explanation;
                const formationMet =
                  yoga.yoga_name === "Neecha Bhanga Raja Yoga"
                    ? Boolean(yoga.neecha_bhanga_data?.is_rescued)
                    : Boolean(yoga.formation_logic);

                return (
                  <div
                    key={yoga.yoga_name}
                    className="glass rounded-xl p-6 border border-white/20 hover:border-white/30 transition-all"
                  >
                    <div className="mb-4">
                      <div className="flex items-start justify-between gap-3 mb-3">
                        <div className="min-w-0">
                          <h3 className="text-xl font-bold text-gray-800 dark:text-gray-200 truncate">
                            {yoga.yoga_name}
                          </h3>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            {yoga.category}
                          </p>
                        </div>
                        <button
                          onClick={() => toggleYoga(yoga.yoga_name)}
                          className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
                          aria-label={isExpanded ? "Collapse details" : "Expand details"}
                        >
                          {isExpanded ? (
                            <ChevronUpIcon className="w-5 h-5" />
                          ) : (
                            <ChevronDownIcon className="w-5 h-5" />
                          )}
                        </button>
                      </div>

                      {/* Potency */}
                      <div className="mb-2">
                        <div className="flex items-baseline gap-2">
                          <span className="text-3xl font-bold text-gray-900 dark:text-gray-100">
                            {(yoga.potency_percent ?? 0).toFixed(2)}
                          </span>
                          <span className="text-sm text-gray-600 dark:text-gray-400">
                            %
                          </span>
                          <Tooltip text={YOGA_TOOLTIPS.potency_percent}>
                            <InformationCircleIcon className="w-4 h-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" />
                          </Tooltip>
                        </div>
                      </div>

                      {/* Planets + Status */}
                      <div className="flex flex-col gap-2 text-sm">
                        <div className="flex items-center gap-1">
                          <span className="text-gray-600 dark:text-gray-400">Planets:</span>
                          <span className="font-semibold text-gray-800 dark:text-gray-200">
                            {planets}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <YogaStatusBadge status={yoga.status_label} />
                          <ActivationBadge activation={yoga.activation} />
                          <Tooltip text={safeExplanation}>
                            <InformationCircleIcon className="w-4 h-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" />
                          </Tooltip>
                        </div>
                      </div>
                    </div>

                    {isExpanded && (
                      <div className="mt-4 pt-4 border-t border-white/10 space-y-3">
                        <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
                          Formation & Strength Breakdown
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-1">
                            <span className="text-sm text-gray-700 dark:text-gray-300">Formation</span>
                            <Tooltip text={YOGA_TOOLTIPS.formation}>
                              <InformationCircleIcon className="w-3.5 h-3.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" />
                            </Tooltip>
                          </div>
                          <span className="text-sm font-semibold text-gray-800 dark:text-gray-200">
                            {formationMet ? "Met" : "—"}
                          </span>
                        </div>

                        {yoga.formation_basis === "Chandra Lagna" && (
                          <div className="text-xs text-gray-500 dark:text-gray-400">
                            Formed from Moon (Chandra Lagna)
                          </div>
                        )}

                        {yoga.formation_logic && (
                          <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                            {formationText || "—"}
                          </div>
                        )}

                        {yoga.neecha_bhanga_data && (
                          <>
                            <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mt-4">
                              Neecha Bhanga (BPHS)
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-gray-700 dark:text-gray-300">Rescued</span>
                              <span className="text-sm font-mono text-gray-800 dark:text-gray-200">
                                {yoga.neecha_bhanga_data.is_rescued ? "YES" : "NO"}
                              </span>
                            </div>
                            <div className="flex items-start justify-between gap-4">
                              <span className="text-sm text-gray-700 dark:text-gray-300">Rules Met</span>
                              <span className="text-sm text-gray-800 dark:text-gray-200 text-right">
                                {(yoga.neecha_bhanga_data.rules_met || []).length
                                  ? (yoga.neecha_bhanga_data.rules_met || []).join(", ")
                                  : "—"}
                              </span>
                            </div>
                          </>
                        )}

                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-700 dark:text-gray-300">Base (Avg Shadbala Ratio)</span>
                          <span className="text-sm font-mono text-gray-800 dark:text-gray-200">
                            {(yoga.strength_breakdown?.avg_shadbala_ratio ?? 0).toFixed(4)}
                          </span>
                        </div>

                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-700 dark:text-gray-300">House Multiplier</span>
                          <span className="text-sm font-mono text-gray-800 dark:text-gray-200">
                            {(yoga.strength_breakdown?.house_multiplier ?? 0).toFixed(4)}
                          </span>
                        </div>

                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-700 dark:text-gray-300">Degree Multiplier</span>
                          <span className="text-sm font-mono text-gray-800 dark:text-gray-200">
                            {(yoga.strength_breakdown?.degree_multiplier ?? 0).toFixed(4)}
                          </span>
                        </div>

                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-700 dark:text-gray-300">Vargottama Applied (Lead)</span>
                          <span className="text-sm font-mono text-gray-800 dark:text-gray-200">
                            {(yoga.strength_breakdown?.vargottama_applied ?? false) ? "YES" : "NO"}
                          </span>
                        </div>

                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-700 dark:text-gray-300">Shadbala Cutoff</span>
                          <span className="text-sm font-mono text-gray-800 dark:text-gray-200">
                            {(yoga.strength_breakdown?.cutoff?.failed_planets?.length ?? 0) > 0
                              ? `FAILED (${yoga.strength_breakdown.cutoff?.failed_planets.join(', ')})`
                              : "OK"}
                          </span>
                        </div>

                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-700 dark:text-gray-300">Triggered (≥ 25%)</span>
                          <span className="text-sm font-mono text-gray-800 dark:text-gray-200">
                            {yoga.is_triggered ? "YES" : "NO"}
                          </span>
                        </div>

                        {yoga.activation && (
                          <>
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-gray-700 dark:text-gray-300">Activation State</span>
                              <span className="text-sm font-mono text-gray-800 dark:text-gray-200">
                                {yoga.activation.state}
                              </span>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-gray-700 dark:text-gray-300">Manifestation Score</span>
                              <span className="text-sm font-mono text-gray-800 dark:text-gray-200">
                                {(yoga.activation.manifestation_score ?? 0).toFixed(2)}
                              </span>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-gray-700 dark:text-gray-300">Connected Lords</span>
                              <span className="text-sm font-mono text-gray-800 dark:text-gray-200">
                                MD: {yoga.activation.connected_lords?.mahadasha ?? "—"} / AD: {yoga.activation.connected_lords?.antardasha ?? "—"}
                              </span>
                            </div>
                          </>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Yoga Transparency Note */}
            <div className="mt-2 p-4 rounded-lg bg-indigo-50/50 dark:bg-indigo-900/10 border border-indigo-200/50 dark:border-indigo-800/50">
              <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
                <strong className="text-gray-700 dark:text-gray-300">Yoga Standard:</strong> PURE BPHS (Bṛhat Parāśara Horā Śāstra).<br />
                Yogas calculated strictly using D1 (Rāśi), D9 (Navāṁśa), and Shadbala ratios.<br />
                No normalization or interpretive scaling applied.
              </p>
            </div>
          </div>

          {/* Yoga Activation Timeline (Birth → 100 Years) */}
          <div className="mt-10">
            <div className="mb-4">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                Yoga Activation Timeline (Birth → 100 Years)
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Timing of Yoga manifestation based on Mahadasha–Antardasha sambandha (BPHS)
              </p>
              {yogaTimeline?.birth_range && (
                <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
                  {yogaTimeline.birth_range.from} → {yogaTimeline.birth_range.to}
                </p>
              )}
            </div>

            {!yogaTimeline?.yogas?.length ? (
              <div className="p-4 rounded-lg bg-gray-50/50 dark:bg-gray-800/30 border border-gray-200/50 dark:border-gray-700/50 text-sm text-gray-600 dark:text-gray-400">
                Timeline not available.
              </div>
            ) : (
              <div className="divide-y divide-gray-200/60 dark:divide-gray-700/60">
                {yogaTimeline.yogas.map((y) => (
                  <div key={y.yoga_name} className="py-8">
                    {/* Yoga Group Header */}
                    <div className="mb-6">
                      <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">
                        {y.yoga_name}
                      </h3>
                    </div>

                    {/* ONE vertical spine per Yoga group */}
                    <div className="relative">
                      <div className="absolute left-3 top-0 bottom-0 w-px bg-gray-200 dark:bg-gray-700" />

                      <div className="space-y-6 pl-8">
                        {y.timeline.map((row, idx) => (
                          <div key={`${row.start_date}-${row.end_date}-${idx}`} className="relative">
                            {/* connector from spine to card (no dot markers) */}
                            <div className="absolute -left-8 top-6 w-8 h-px bg-gray-200 dark:bg-gray-700" />

                            <div className="rounded-xl border border-gray-200/70 dark:border-gray-700/70 bg-white/60 dark:bg-gray-900/30 p-5">
                              {/* date range + state badge */}
                              <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
                                <div className="text-xs text-gray-500 dark:text-gray-400">
                                  {formatIsoDateForDisplay(row.start_date)} → {formatIsoDateForDisplay(row.end_date)}
                                </div>
                                <TimelineActivationBadge state={row.state} label={row.state_label} />
                              </div>

                              {/* yoga name (bold, chapter context) */}
                              <div className="text-base font-bold text-gray-900 dark:text-gray-100 mb-2">
                                {y.yoga_name}
                              </div>

                              {/* manifestation score */}
                              <div className="text-sm text-gray-700 dark:text-gray-300 mb-1">
                                <span className="font-medium">Manifestation Score:</span>{" "}
                                <span className="font-mono">{Number(row.manifestation_score ?? 0).toFixed(2)}</span>
                              </div>

                              {/* dasha period */}
                              <div className="text-sm text-gray-600 dark:text-gray-400">
                                <span className="font-medium">Dasha:</span> {row.dasha_period}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Transparency Note */}
          <div className="mt-8 p-4 rounded-lg bg-indigo-50/50 dark:bg-indigo-900/10 border border-indigo-200/50 dark:border-indigo-800/50">
            <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
              <strong className="text-gray-700 dark:text-gray-300">Calculation Standard:</strong> PURE BPHS (Bṛhat Parāśara Horā Śāstra).<br />
              Status labels are derived from classical minimum-strength thresholds.<br />
              No normalization or interpretive scaling applied.
            </p>
          </div>
        </SlideUp>
      </div>
    </div>
  );
}
