/**
 * useMaxLoadTime Hook
 * Automatically stops loading state after max time (default 8 seconds)
 * Prevents infinite loading spinners
 */

import { useEffect, useRef } from 'react';

interface UseMaxLoadTimeOptions {
  loading: boolean;
  setLoading: (loading: boolean) => void;
  maxTime?: number; // in milliseconds, default 8000 (8 seconds)
  onTimeout?: () => void; // Optional callback when timeout occurs
}

export function useMaxLoadTime({
  loading,
  setLoading,
  maxTime = 8000,
  onTimeout,
}: UseMaxLoadTimeOptions) {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (loading) {
      // Start timeout when loading starts
      timeoutRef.current = setTimeout(() => {
        console.warn(`⚠️ Loading timeout after ${maxTime}ms - stopping spinner`);
        setLoading(false);
        if (onTimeout) {
          onTimeout();
        }
      }, maxTime);
    } else {
      // Clear timeout when loading stops
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
    }

    // Cleanup on unmount
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [loading, setLoading, maxTime, onTimeout]);
}
