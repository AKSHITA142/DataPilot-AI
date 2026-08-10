import { create } from "zustand";

interface ExperimentState {
  // Active filters on Experiment Explorer
  filterModelType: string | null;
  filterStatus: string | null;
  filterMinMetric: number | null;
  // Selected experiment IDs for comparison
  selectedIds: Set<string>;
  // Comparison modal open
  compareModalOpen: boolean;

  setFilterModelType: (type: string | null) => void;
  setFilterStatus: (status: string | null) => void;
  setFilterMinMetric: (min: number | null) => void;
  toggleSelectExperiment: (id: string) => void;
  clearSelection: () => void;
  setCompareModalOpen: (open: boolean) => void;
}

export const useExperimentStore = create<ExperimentState>((set) => ({
  filterModelType: null,
  filterStatus: null,
  filterMinMetric: null,
  selectedIds: new Set(),
  compareModalOpen: false,

  setFilterModelType: (type) => set({ filterModelType: type }),
  setFilterStatus: (status) => set({ filterStatus: status }),
  setFilterMinMetric: (min) => set({ filterMinMetric: min }),
  toggleSelectExperiment: (id) =>
    set((state) => {
      const next = new Set(state.selectedIds);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return { selectedIds: next };
    }),
  clearSelection: () => set({ selectedIds: new Set() }),
  setCompareModalOpen: (open) => set({ compareModalOpen: open }),
}));
