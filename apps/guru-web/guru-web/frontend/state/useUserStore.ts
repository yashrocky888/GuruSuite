/**
 * User Store
 * Zustand store for user state management
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string | null;
  name: string | null;
  email: string | null;
  birthDetails: {
    date: string | null;
    time: string | null;
    place: string | null;
    latitude: number | null;
    longitude: number | null;
  } | null;
  preferences: {
    theme: 'light' | 'dark' | 'auto';
    language: string;
    notifications: boolean;
  };
}

interface UserStore {
  user: User;
  isAuthenticated: boolean;
  setUser: (user: Partial<User>) => void;
  setBirthDetails: (details: User['birthDetails']) => void;
  setPreferences: (preferences: Partial<User['preferences']>) => void;
  logout: () => void;
}

const initialUser: User = {
  id: null,
  name: null,
  email: null,
  birthDetails: null,
  preferences: {
    theme: 'auto',
    language: 'en',
    notifications: true,
  },
};

export const useUserStore = create<UserStore>()(
  persist(
    (set) => ({
      user: initialUser,
      isAuthenticated: false,
      
      setUser: (userData) =>
        set((state) => ({
          user: { ...state.user, ...userData },
          isAuthenticated: !!userData.id,
        })),
      
      setBirthDetails: (details) =>
        set((state) => ({
          user: {
            ...state.user,
            birthDetails: details,
          },
        })),
      
      setPreferences: (preferences) =>
        set((state) => ({
          user: {
            ...state.user,
            preferences: {
              ...state.user.preferences,
              ...preferences,
            },
          },
        })),
      
      logout: () =>
        set({
          user: initialUser,
          isAuthenticated: false,
        }),
    }),
    {
      name: 'guru-user-storage',
    }
  )
);

