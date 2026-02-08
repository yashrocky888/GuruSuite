'use client';

/**
 * Panchang Page (Legacy Route)
 * Redirects to /panchanga for the new table-based UI
 */

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function PanchangPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to new Panchanga page with table layout
    router.replace('/panchanga');
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-gray-600 dark:text-gray-400">Redirecting to Panchanga...</p>
      </div>
    </div>
  );
}

