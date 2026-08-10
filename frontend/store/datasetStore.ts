import { create } from "zustand";

interface DatasetState {
  activeDatasetId: string | null;
  uploadStatus: "idle" | "uploading" | "success" | "error";
  uploadProgress: number;
  uploadError: string | null;
  mission: string;

  setActiveDatasetId: (id: string | null) => void;
  setUploadStatus: (status: DatasetState["uploadStatus"]) => void;
  setUploadProgress: (pct: number) => void;
  setUploadError: (err: string | null) => void;
  setMission: (mission: string) => void;
  reset: () => void;
}

export const useDatasetStore = create<DatasetState>((set) => ({
  activeDatasetId: null,
  uploadStatus: "idle",
  uploadProgress: 0,
  uploadError: null,
  mission: "",

  setActiveDatasetId: (id) => set({ activeDatasetId: id }),
  setUploadStatus: (status) => set({ uploadStatus: status }),
  setUploadProgress: (pct) => set({ uploadProgress: pct }),
  setUploadError: (err) => set({ uploadError: err }),
  setMission: (mission) => set({ mission }),
  reset: () =>
    set({
      uploadStatus: "idle",
      uploadProgress: 0,
      uploadError: null,
    }),
}));
