'use client';

/**
 * Profile Page
 * Placeholder for profile, saved charts, preferences
 */

import { motion } from 'framer-motion';
import { UserIcon } from '@heroicons/react/24/outline';
import MainLayout from '@/frontend/layouts/MainLayout';
import { FadeIn, SlideUp } from '@/frontend/animations';

export default function ProfilePage() {
  return (
    <MainLayout>
      <div className="space-y-8">
        <FadeIn>
          <div className="text-center space-y-4">
            <div className="w-16 h-16 mx-auto rounded-full bg-gradient-to-br from-gray-500 to-slate-500 flex items-center justify-center">
              <UserIcon className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-gray-600 to-slate-600 bg-clip-text text-transparent">
              Profile
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Your profile, saved charts, and preferences
            </p>
          </div>
        </FadeIn>

        <SlideUp delay={0.2}>
          <div className="glass rounded-2xl p-8 md:p-12 border border-white/20 min-h-[400px] flex items-center justify-center">
            <div className="text-center space-y-4">
              <p className="text-gray-500 dark:text-gray-400 text-lg">
                Profile settings, saved charts, and preferences will be displayed here
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

