'use client';

/**
 * Panchang Cards Component
 * Displays panchang information in card format
 */

import { motion } from 'framer-motion';
import { SunIcon, MoonIcon, ClockIcon, CalendarIcon } from '@heroicons/react/24/outline';

interface PanchangData {
  panchanga?: {
    tithi?: {
      name?: string;
      number?: number;
      paksha?: string;
      end_time?: string;
    };
    nakshatra?: {
      name?: string;
      lord?: string;
      
      pada?: number;
      end_time?: string;
    };
    yoga?: {
      name?: string;
      end_time?: string;
    };
    karana?: {
      name?: string;
      end_time?: string;
    };
    sunrise?: string;
    sunset?: string;
    vara?: {
      name?: string;
      lord?: string;
    };
  };
  // Legacy support for old format
  tithi?: string;
  nakshatra?: string;
  yoga?: string;
  karana?: string;
  sunrise?: string;
  sunset?: string;
  moonrise?: string;
  moonset?: string;
}

interface PanchangCardsProps {
  data: PanchangData;
}

export default function PanchangCards({ data }: PanchangCardsProps) {
  // TEMP DEBUG: Verify data structure
  console.log('🧪 DASHBOARD PANCHANGA DEBUG', data);

  // Extract panchanga object (new API format) or use data directly (legacy)
  const panchanga = data.panchanga || data;

  // Helper function to extract name from object or string
  const getName = (value: any): string => {
    if (!value) return '—';
    if (typeof value === 'string') return value;
    if (typeof value === 'object' && value.name) return value.name;
    return '—';
  };

  const cards = [
    {
      title: 'Tithi',
      value: getName(panchanga.tithi),
      icon: CalendarIcon,
      gradient: 'from-yellow-400 to-orange-500',
    },
    {
      title: 'Nakshatra',
      value: getName(panchanga.nakshatra),
      icon: MoonIcon,
      gradient: 'from-purple-400 to-pink-500',
    },
    {
      title: 'Yoga',
      value: getName(panchanga.yoga),
      icon: SunIcon,
      gradient: 'from-blue-400 to-cyan-500',
    },
    {
      title: 'Karana',
      value: getName(panchanga.karana),
      icon: ClockIcon,
      gradient: 'from-green-400 to-emerald-500',
    },
  ];

  const timings = [
    { label: 'Sunrise', value: panchanga.sunrise ?? data.sunrise },
    { label: 'Sunset', value: panchanga.sunset ?? data.sunset },
    { label: 'Moonrise', value: data.moonrise },
    { label: 'Moonset', value: data.moonset },
  ].filter((item) => item.value);

  return (
    <div className="space-y-6">
      {/* Main Panchang Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map((card, index) => {
          const Icon = card.icon;
          return (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="glass rounded-xl p-6 border border-white/20 hover:border-white/40 transition-smooth"
            >
              <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${card.gradient} flex items-center justify-center mb-4`}>
                <Icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                {card.title}
              </h3>
              <p className="text-xl font-bold text-gray-800 dark:text-gray-200">
                {card.value}
              </p>
            </motion.div>
          );
        })}
      </div>

      {/* Timings */}
      {timings.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass rounded-xl p-6 border border-white/20"
        >
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">
            Timings
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {timings.map((timing) => (
              <div key={timing.label} className="text-center">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                  {timing.label}
                </p>
                <p className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                  {timing.value}
                </p>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}

