'use client';

/**
 * Dasha Timeline Component
 * Displays planetary periods timeline
 */

import { motion } from 'framer-motion';
import { ClockIcon } from '@heroicons/react/24/outline';

interface DashaPeriod {
  planet: string;
  startDate: string;
  endDate: string;
  duration: string;
  subPeriods?: DashaPeriod[];
}

interface DashaTimelineProps {
  periods: DashaPeriod[];
}

export default function DashaTimeline({ periods }: DashaTimelineProps) {
  if (!periods || periods.length === 0) {
    return (
      <div className="glass rounded-2xl p-8 border border-white/20">
        <p className="text-gray-500 dark:text-gray-400 text-center">No dasha data available</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-2xl p-6 border border-white/20"
    >
      <div className="flex items-center mb-6">
        <ClockIcon className="w-6 h-6 text-purple-500 mr-2" />
        <h3 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
          Dasha Timeline
        </h3>
      </div>

      <div className="space-y-4">
        {periods.map((period, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="border-l-4 border-purple-500 pl-4 py-2"
          >
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                {period.planet} Dasha
              </h4>
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {period.duration}
              </span>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {new Date(period.startDate).toLocaleDateString()} - {new Date(period.endDate).toLocaleDateString()}
            </p>
            
            {period.subPeriods && period.subPeriods.length > 0 && (
              <div className="mt-3 ml-4 space-y-2">
                {period.subPeriods.map((subPeriod, subIndex) => (
                  <div key={subIndex} className="text-sm text-gray-500 dark:text-gray-500">
                    <span className="font-medium">{subPeriod.planet}</span>: {subPeriod.startDate} - {subPeriod.endDate}
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}

