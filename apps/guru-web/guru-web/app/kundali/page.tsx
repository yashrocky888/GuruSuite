'use client';

/**
 * Kundali Page
 * Placeholder for Kundli chart components
 */

import { motion } from 'framer-motion';
import { SparklesIcon } from '@heroicons/react/24/outline';
import MainLayout from '@/frontend/layouts/MainLayout';
import { FadeIn, SlideUp } from '@/frontend/animations';

export default function KundaliPage() {
  return (
    <MainLayout>
      <div className="space-y-8">
        <FadeIn>
          <div className="text-center space-y-4">
            <div className="w-16 h-16 mx-auto rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
              <SparklesIcon className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              Kundali Chart
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Your complete birth chart analysis
            </p>
          </div>
        </FadeIn>

        <SlideUp delay={0.2}>
          <div className="glass rounded-2xl p-8 md:p-12 border border-white/20 min-h-[400px] flex items-center justify-center">
            <div className="text-center space-y-4">
              <p className="text-gray-500 dark:text-gray-400 text-lg">
                Kundali chart components will be displayed here
              </p>
              <p className="text-sm text-gray-400 dark:text-gray-500">
                Integration with GURU API coming soon
              </p>
            </div>
          </div>
        </SlideUp>
      </div>
    </MainLayout>
  );
}

