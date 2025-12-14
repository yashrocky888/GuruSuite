'use client';

/**
 * Home Page - Birth Details Input
 * First page users see to enter their birth information
 */

import { motion } from 'framer-motion';
import { SparklesIcon } from '@heroicons/react/24/outline';
import BirthDetailsForm from '@/components/BirthDetailsForm';
import { FadeIn } from '@/frontend/animations';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50/30 to-blue-50/30 dark:from-slate-900 dark:via-purple-900/20 dark:to-blue-900/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <FadeIn>
          <div className="text-center mb-12">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 200, damping: 15 }}
              className="inline-block mb-6"
            >
              <div className="w-24 h-24 rounded-full bg-gradient-to-br from-purple-500 via-blue-500 to-cyan-500 flex items-center justify-center spiritual-glow mx-auto">
                <SparklesIcon className="w-12 h-12 text-white" />
              </div>
            </motion.div>
            
            <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-purple-600 via-blue-600 to-cyan-600 bg-clip-text text-transparent mb-4">
              Welcome to GURU
            </h1>
            
            <p className="text-lg md:text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Discover your cosmic blueprint with Vedic astrology insights
            </p>
          </div>
        </FadeIn>

        {/* Birth Details Form */}
        <BirthDetailsForm />
      </div>
    </div>
  );
}
