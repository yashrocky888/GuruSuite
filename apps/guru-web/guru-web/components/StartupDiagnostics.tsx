'use client';

import { useEffect } from 'react';

/**
 * Startup Diagnostics Component
 * Logs frontend startup information for debugging
 */
export default function StartupDiagnostics() {
  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://guru-api-660206747784.asia-south1.run.app/api/v1';
    
    console.log('✅ Guru Web started on localhost:3000');
    console.log(`📡 API Base URL: ${apiUrl}`);
    console.log(`🌐 Environment: ${process.env.NODE_ENV || 'development'}`);
    
    // Test API connectivity (non-blocking)
    if (apiUrl && !apiUrl.includes('localhost')) {
      fetch(`${apiUrl.replace('/api/v1', '')}/`, { method: 'GET', signal: AbortSignal.timeout(5000) })
        .then(() => console.log('✅ API connectivity: OK'))
        .catch(() => console.warn('⚠️  API connectivity: Could not reach deployed API (may be normal if API is down)'));
    }
  }, []);

  return null; // This component doesn't render anything
}

