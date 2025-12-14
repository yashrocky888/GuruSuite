/**
 * Guru Store
 * Zustand store for Guru chat and conversation state
 */

import { create } from 'zustand';

interface Message {
  id: string;
  role: 'user' | 'guru';
  content: string;
  timestamp: Date;
  metadata?: {
    chartData?: any;
    predictionType?: string;
    [key: string]: any;
  };
}

interface GuruStore {
  messages: Message[];
  isTyping: boolean;
  currentSession: string | null;
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  setTyping: (typing: boolean) => void;
  clearMessages: () => void;
  startNewSession: () => void;
}

export const useGuruStore = create<GuruStore>((set) => ({
  messages: [],
  isTyping: false,
  currentSession: null,
  
  addMessage: (message) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          ...message,
          id: `msg-${Date.now()}-${Math.random()}`,
          timestamp: new Date(),
        },
      ],
    })),
  
  setTyping: (typing) =>
    set({ isTyping: typing }),
  
  clearMessages: () =>
    set({ messages: [], currentSession: null }),
  
  startNewSession: () =>
    set({
      messages: [],
      currentSession: `session-${Date.now()}`,
    }),
}));

