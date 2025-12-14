/**
 * Kundli Store
 * Manages kundli chart data
 * Updated for Drik Panchang & JHORA compatibility
 */

import { create } from 'zustand';
import { KundliData } from '@/services/api';

interface KundliStore {
  kundliData: KundliData | null;
  loading: boolean;
  error: string | null;
  setKundliData: (data: KundliData) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearKundli: () => void;
}

export const useKundliStore = create<KundliStore>((set) => ({
  kundliData: null,
  loading: false,
  error: null,
  setKundliData: (data) => set({ kundliData: data, error: null }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  clearKundli: () => set({ kundliData: null, error: null }),
}));

