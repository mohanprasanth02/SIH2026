/**
 * SatQuery AI - Global State Store (Zustand)
 */
import { create } from 'zustand';
import type { UploadResult, AnalysisResult, JobState } from '../services/api';

interface AppState {
  // Auth
  isAuthenticated: boolean;
  setAuthenticated: (v: boolean) => void;

  // Current images
  primaryImage: UploadResult | null;
  secondaryImage: UploadResult | null;
  setPrimaryImage: (img: UploadResult | null) => void;
  setSecondaryImage: (img: UploadResult | null) => void;

  // Analysis
  currentJobId: string | null;
  currentJob: JobState | null;
  currentResult: AnalysisResult | null;
  analysisHistory: AnalysisResult[];
  setCurrentJobId: (id: string | null) => void;
  setCurrentJob: (job: JobState | null) => void;
  setCurrentResult: (result: AnalysisResult | null) => void;
  addToHistory: (result: AnalysisResult) => void;

  // Chat history
  chatMessages: ChatMessage[];
  addChatMessage: (msg: ChatMessage) => void;
  clearChat: () => void;

  // UI state
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
  activeLayer: string | null;
  setActiveLayer: (layer: string | null) => void;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  jobId?: string;
  resultRef?: AnalysisResult;
}

export const useAppStore = create<AppState>((set) => ({
  // Auth
  isAuthenticated: !!localStorage.getItem('satquery_token'),
  setAuthenticated: (v) => set({ isAuthenticated: v }),

  // Images
  primaryImage: null,
  secondaryImage: null,
  setPrimaryImage: (img) => set({ primaryImage: img }),
  setSecondaryImage: (img) => set({ secondaryImage: img }),

  // Analysis
  currentJobId: null,
  currentJob: null,
  currentResult: null,
  analysisHistory: [],
  setCurrentJobId: (id) => set({ currentJobId: id }),
  setCurrentJob: (job) => set({ currentJob: job }),
  setCurrentResult: (result) => set({ currentResult: result }),
  addToHistory: (result) =>
    set((state) => ({
      analysisHistory: [result, ...state.analysisHistory].slice(0, 50),
    })),

  // Chat
  chatMessages: [],
  addChatMessage: (msg) =>
    set((state) => ({ chatMessages: [...state.chatMessages, msg] })),
  clearChat: () => set({ chatMessages: [] }),

  // UI
  sidebarCollapsed: false,
  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
  activeLayer: null,
  setActiveLayer: (layer) => set({ activeLayer: layer }),
}));
