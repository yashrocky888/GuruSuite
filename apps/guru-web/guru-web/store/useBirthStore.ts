/**
 * Birth Details Store
 * Manages birth details state including user_id from API response
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { BirthDetails } from '@/services/api';

interface BirthStore {
  birthDetails: BirthDetails | null;
  userId: string | null;
  lagna: number | null;
  lagnaSign: string | null;

  // ✅ Hydration flag (CRITICAL)
  hasHydrated: boolean;

  setBirthDetails: (details: BirthDetails) => void;
  setUserId: (userId: string) => void;
  setLagna: (lagna: number, lagnaSign: string) => void;
  clearBirthDetails: () => void;
}

export const useBirthStore = create<BirthStore>()(
  persist(
    (set) => ({
      birthDetails: null,
      userId: null,
      lagna: null,
      lagnaSign: null,

      hasHydrated: false,

      setBirthDetails: (details) => set({ birthDetails: details }),
      setUserId: (userId) => set({ userId }),
      setLagna: (lagna, lagnaSign) => set({ lagna, lagnaSign }),

      clearBirthDetails: () =>
        set({
          birthDetails: null,
          userId: null,
          lagna: null,
          lagnaSign: null,
        }),
    }),
    {
      name: 'guru-birth-store',

      // Persist only necessary fields
      partialize: (state) => ({
        birthDetails: state.birthDetails,
        userId: state.userId,
        lagna: state.lagna,
        lagnaSign: state.lagnaSign,
      }),

      // 🔒 CRITICAL: hydration completion hook
      // NOTE: Cannot access useBirthStore here (circular reference during initialization)
      // hasHydrated will be set by component's useEffect after mount
      onRehydrateStorage: () => {
        // Return function that runs AFTER rehydration completes
        // We don't set hasHydrated here to avoid circular reference
        // Component's useEffect will handle setting hasHydrated after mount
        return () => {
          // Rehydration complete - component will set hasHydrated via useEffect
        };
      },
    }
  )
);

