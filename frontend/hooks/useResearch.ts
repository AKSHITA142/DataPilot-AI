"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";
import { getJob, getExperiments, getReport, getDashboard, listDatasets } from "@/services/apiClient";
import { wsClient } from "@/services/websocketClient";
import { useResearchStore } from "@/store/researchStore";
import type { WSEvent } from "@/types/api";


// ── useJob — fetch job status with polling fallback ──────────────────
export function useJob(jobId: string | null) {
  return useQuery({
    queryKey: ["job", jobId],
    queryFn: () => getJob(jobId!),
    enabled: !!jobId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      // Auto-refetch while running; stop when terminal
      if (status === "completed" || status === "failed" || status === "cancelled") {
        return false;
      }
      return 10_000; // 10-second fallback polling
    },
  });
}

// ── useExperiments — fetch experiments list ───────────────────────────
export function useExperiments(jobId: string | null) {
  return useQuery({
    queryKey: ["experiments", jobId],
    queryFn: () => getExperiments(jobId!),
    enabled: !!jobId,
    staleTime: 5_000,
  });
}

// ── useReport — fetch final report ────────────────────────────────────
export function useReport(jobId: string | null) {
  return useQuery({
    queryKey: ["report", jobId],
    queryFn: () => getReport(jobId!),
    enabled: !!jobId,
    staleTime: 60_000,
    retry: 3,
  });
}

// ── useWebSocket — subscribe to live job events ───────────────────────
export function useWebSocket(jobId: string | null) {
  const queryClient = useQueryClient();
  const { setWsConnected, setCurrentStage, setProgressPercent, addLogMessage } =
    useResearchStore();
  const unsubRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    if (!jobId) return;

    wsClient.connect(jobId);
    setWsConnected(wsClient.isConnected);

    const handler = (event: WSEvent) => {
      const { data } = event;

      // Update stores
      if (data.stage) setCurrentStage(data.stage);
      if (data.progress_percent !== undefined)
        setProgressPercent(data.progress_percent);

      // Log all events to the live log panel
      if (data.message) {
        addLogMessage({
          id: `${event.timestamp}-${Math.random()}`,
          timestamp: event.timestamp,
          level: data.level ?? "info",
          message: data.message,
          stage: data.stage,
        });
      }

      // Invalidate TanStack Query caches based on event type
      switch (event.event) {
        case "job.status_changed":
        case "job.progress":
        case "job.stage_update":
          queryClient.invalidateQueries({ queryKey: ["job", jobId] });
          break;
        case "experiment.completed":
          queryClient.invalidateQueries({ queryKey: ["experiments", jobId] });
          break;
        case "job.completed":
          queryClient.invalidateQueries({ queryKey: ["job", jobId] });
          queryClient.invalidateQueries({ queryKey: ["experiments", jobId] });
          queryClient.invalidateQueries({ queryKey: ["report", jobId] });
          break;
        case "job.failed":
          queryClient.invalidateQueries({ queryKey: ["job", jobId] });
          break;
      }
    };

    unsubRef.current = wsClient.on("all", handler);

    return () => {
      unsubRef.current?.();
      setWsConnected(false);
    };
  }, [jobId, queryClient, setWsConnected, setCurrentStage, setProgressPercent, addLogMessage]);
}

// ── useDashboard — overview stats ────────────────────────────────────
export function useDashboard() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: getDashboard,
    staleTime: 30_000,
    refetchInterval: 60_000,
  });
}

// ── useDatasets — full list for the datasets table ───────────────────
export function useDatasets() {
  return useQuery({
    queryKey: ["datasets"],
    queryFn: listDatasets,
    staleTime: 60_000,
  });
}
