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
      setBirthDetails: (details) => set({ birthDetails: details }),
      setUserId: (userId) => set({ userId }),
      setLagna: (lagna, lagnaSign) => set({ lagna, lagnaSign }),
      clearBirthDetails: () => set({ 
        birthDetails: null, 
        userId: null,
        lagna: null,
        lagnaSign: null
      }),
    }),
    {
      name: 'guru-birth-storage',
    }
  )
);

