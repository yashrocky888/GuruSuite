'use client';

/**
 * Panchang Cards Component
 * Displays panchang information in card format
 */

import { motion } from 'framer-motion';
import { SunIcon, MoonIcon, ClockIcon, CalendarIcon } from '@heroicons/react/24/outline';

interface PanchangData {
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
  const cards = [
    {
      title: 'Tithi',
      value: data.tithi || 'N/A',
      icon: CalendarIcon,
      gradient: 'from-yellow-400 to-orange-500',
    },
    {
      title: 'Nakshatra',
      value: data.nakshatra || 'N/A',
      icon: MoonIcon,
      gradient: 'from-purple-400 to-pink-500',
    },
    {
      title: 'Yoga',
      value: data.yoga || 'N/A',
      icon: SunIcon,
      gradient: 'from-blue-400 to-cyan-500',
    },
    {
      title: 'Karana',
      value: data.karana || 'N/A',
      icon: ClockIcon,
      gradient: 'from-green-400 to-emerald-500',
    },
  ];

  const timings = [
    { label: 'Sunrise', value: data.sunrise },
    { label: 'Sunset', value: data.sunset },
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

