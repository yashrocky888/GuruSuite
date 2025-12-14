/**
 * UI Store
 * Zustand store for UI state management
 */

import { create } from 'zustand';

interface UIStore {
  sidebarOpen: boolean;
  modalOpen: boolean;
  modalContent: React.ReactNode | null;
  loading: boolean;
  loadingMessage: string | null;
  notifications: Array<{
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    message: string;
    timestamp: Date;
  }>;
  
  // Actions
  setSidebarOpen: (open: boolean) => void;
  setModalOpen: (open: boolean, content?: React.ReactNode) => void;
  setLoading: (loading: boolean, message?: string | null) => void;
  addNotification: (notification: Omit<UIStore['notifications'][0], 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
}

export const useUIStore = create<UIStore>((set) => ({
  sidebarOpen: false,
  modalOpen: false,
  modalContent: null,
  loading: false,
  loadingMessage: null,
  notifications: [],
  
  setSidebarOpen: (open) =>
    set({ sidebarOpen: open }),
  
  setModalOpen: (open, content = null) =>
    set({
      modalOpen: open,
      modalContent: content,
    }),
  
  setLoading: (loading, message = undefined) =>
    set({
      loading,
      loadingMessage: message || null,
    }),
  
  addNotification: (notification) =>
    set((state) => ({
      notifications: [
        ...state.notifications,
        {
          ...notification,
          id: `notif-${Date.now()}-${Math.random()}`,
          timestamp: new Date(),
        },
      ],
    })),
  
  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),
  
  clearNotifications: () =>
    set({ notifications: [] }),
}));

