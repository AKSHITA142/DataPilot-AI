import { create } from "zustand";
import type { PipelineStage } from "@/types/api";

interface ResearchState {
  activeJobId: string | null;
  wsConnected: boolean;
  currentStage: PipelineStage | null;
  progressPercent: number;
  logMessages: LogMessage[];

  setActiveJobId: (id: string | null) => void;
  setWsConnected: (connected: boolean) => void;
  setCurrentStage: (stage: PipelineStage | null) => void;
  setProgressPercent: (pct: number) => void;
  addLogMessage: (msg: LogMessage) => void;
  clearLogs: () => void;
}

export interface LogMessage {
  id: string;
  timestamp: string;
  level: "info" | "warning" | "error" | "success";
  message: string;
  stage?: PipelineStage;
}

export const useResearchStore = create<ResearchState>((set) => ({
  activeJobId: null,
  wsConnected: false,
  currentStage: null,
  progressPercent: 0,
  logMessages: [],

  setActiveJobId: (id) => set({ activeJobId: id }),
  setWsConnected: (connected) => set({ wsConnected: connected }),
  setCurrentStage: (stage) => set({ currentStage: stage }),
  setProgressPercent: (pct) => set({ progressPercent: pct }),
  addLogMessage: (msg) =>
    set((state) => ({
      logMessages: [...state.logMessages.slice(-199), msg], // keep last 200
    })),
  clearLogs: () => set({ logMessages: [] }),
}));
