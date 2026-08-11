"use client";

import { use, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Wifi,
  WifiOff,
  AlertTriangle,
  ChevronRight,
  FlaskConical,
} from "lucide-react";
import { Button } from "@/components/buttons/Button";
import { ProgressBar, Spinner, SkeletonCard } from "@/components/loading/Loading";
import { Badge } from "@/components/badges/Badge";
import { StageTimeline } from "@/components/cards/StageTimeline";
import { Modal } from "@/components/modals/Modal";
import { GlassCard } from "@/components/cards/GlassCard";
import { useJob, useWebSocket } from "@/hooks/useResearch";
import { useResearchStore } from "@/store/researchStore";
import { cancelJob } from "@/services/apiClient";
import type { TimelineStage } from "@/components/cards/StageTimeline";
import type { PipelineStage, JobStatus } from "@/types/api";
import { formatDate } from "@/utils/formatters";

/* ── Stage definitions (full pipeline) ───────── */
const PIPELINE_STAGES: { id: PipelineStage; label: string; description: string }[] = [
  { id: "profiling",     label: "Dataset Profiling",   description: "Analyzing column types, distributions, quality, and missing values." },
  { id: "understanding", label: "Understanding",        description: "Semantic analysis — detecting target, task type, and mission context." },
  { id: "planning",      label: "Research Planning",    description: "LangGraph orchestrator designing the experiment pipeline." },
  { id: "executing",     label: "Running Experiments",  description: "Executing ML pipelines across multiple model configurations." },
  { id: "evaluating",    label: "Evaluation",           description: "Scoring experiments, ranking models, extracting knowledge findings." },
  { id: "decision",      label: "Decision Making",      description: "Selecting the best pipeline and generating recommendations." },
  { id: "reporting",     label: "Report Generation",    description: "Compiling the final HTML and Markdown research report." },
];

function stageStatusForJob(
  stageId: PipelineStage,
  currentStage: PipelineStage | null,
  jobStatus: JobStatus
): TimelineStage["status"] {
  const order = PIPELINE_STAGES.map((s) => s.id);
  const stageIdx = order.indexOf(stageId);
  const currentIdx = currentStage ? order.indexOf(currentStage) : -1;

  if (jobStatus === "completed") return "completed";
  if (jobStatus === "failed") {
    if (stageIdx < currentIdx) return "completed";
    if (stageIdx === currentIdx) return "failed";
    return "waiting";
  }
  if (stageIdx < currentIdx) return "completed";
  if (stageIdx === currentIdx) return "running";
  return "waiting";
}

export default function TimelinePage({
  params,
}: {
  params: Promise<{ jobId: string }>;
}) {
  const { jobId } = use(params);
  const router = useRouter();

  const { data: job, isLoading } = useJob(jobId);
  useWebSocket(jobId);

  const { wsConnected, progressPercent, currentStage, logMessages } =
    useResearchStore();

  const [cancelModalOpen, setCancelModalOpen] = useState(false);
  const [cancelling, setCancelling] = useState(false);

  // Auto-navigate to experiments when job completes
  useEffect(() => {
    if (job?.status === "completed") {
      const t = setTimeout(() => router.push(`/experiments/${jobId}`), 1500);
      return () => clearTimeout(t);
    }
  }, [job?.status, jobId, router]);

  const handleCancel = async () => {
    setCancelling(true);
    try {
      await cancelJob(jobId);
      setCancelModalOpen(false);
    } catch {
      // ignore
    } finally {
      setCancelling(false);
    }
  };

  const stages: TimelineStage[] = PIPELINE_STAGES.map((s) => ({
    id: s.id,
    label: s.label,
    description: s.description,
    status: job
      ? stageStatusForJob(s.id, currentStage ?? job.current_stage ?? null, job.status)
      : "waiting",
  }));

  return (
    <>
      <div className="flex h-full overflow-hidden">
      {/* ── LEFT: Pipeline timeline ── */}
      <div className="w-full max-w-lg flex-shrink-0 flex flex-col border-r border-border-subtle overflow-y-auto">
        <div className="p-6">
          {/* Job header — includes WS indicator + action buttons */}
          {isLoading ? (
            <SkeletonCard />
          ) : job ? (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6"
            >
              <div className="flex items-start justify-between gap-3 mb-3">
                  <div className="min-w-0">
                    <p className="text-xs text-slate-500 mb-1 uppercase tracking-wider">Research Job</p>
                    <p className="text-xs font-mono text-slate-600 truncate">{job.job_id}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    {/* WS indicator — inline */}
                    <div className="flex items-center gap-1.5 text-xs">
                      {wsConnected ? (
                        <><Wifi className="w-3.5 h-3.5 text-emerald-400" /><span className="text-emerald-400">Live</span></>
                      ) : (
                        <><WifiOff className="w-3.5 h-3.5 text-slate-500" /><span className="text-slate-500">Offline</span></>
                      )}
                    </div>
                    <Badge variant={job.status} label={job.status} />
                    {job.status === "running" && (
                      <Button variant="danger" size="sm" onClick={() => setCancelModalOpen(true)}>
                        Cancel
                      </Button>
                    )}
                    {job.status === "completed" && (
                      <Button
                        variant="primary"
                        size="sm"
                        icon={<ChevronRight className="w-3.5 h-3.5" />}
                        onClick={() => router.push(`/experiments/${jobId}`)}
                      >
                        View Results
                      </Button>
                    )}
                  </div>
                </div>

                {/* Mission */}
                <GlassCard padding="sm" hover={false} className="mb-4">
                  <p className="text-xs text-slate-500 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                    <FlaskConical className="w-3 h-3" /> Mission
                  </p>
                  <p className="text-sm text-slate-300 leading-relaxed">{job.mission}</p>
                </GlassCard>

                {/* Global progress bar */}
                <ProgressBar
                  value={job.status === "completed" ? 100 : progressPercent || job.progress_percent || 0}
                  label={
                    job.status === "completed"
                      ? "Research complete!"
                      : job.status === "failed"
                      ? "Job failed"
                      : currentStage
                      ? `Running: ${currentStage.replace(/_/g, " ")}…`
                      : "Initializing…"
                  }
                  color={
                    job.status === "completed"
                      ? "success"
                      : job.status === "failed"
                      ? "error"
                      : "brand"
                  }
                />

                {/* Started / created */}
                <p className="text-xs text-slate-600 mt-3">
                  Started {job.started_at ? formatDate(job.started_at) : formatDate(job.created_at)}
                </p>
              </motion.div>
            ) : null}

            {/* Error state */}
            {job?.status === "failed" && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mb-4 p-4 rounded-xl bg-red-500/10 border border-red-500/25 flex items-start gap-3"
              >
                <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-red-300">Job Failed</p>
                  {job.error_message && (
                    <p className="text-xs text-red-400/80 mt-1 font-mono">
                      {job.error_message}
                    </p>
                  )}
                </div>
              </motion.div>
            )}

            {/* Completed state */}
            {job?.status === "completed" && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="mb-4 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/25 text-center"
              >
                <p className="text-sm font-semibold text-emerald-300">
                  ✓ Research Complete — Redirecting to results…
                </p>
              </motion.div>
            )}

            {/* Stage timeline */}
            <StageTimeline stages={stages} />
          </div>
        </div>

        {/* ── RIGHT: Live log panel ── */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="flex items-center justify-between px-5 py-3 border-b border-slate-800/60 bg-slate-950/50">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
              Live Research Log
            </span>
            {isLoading && <Spinner size="sm" />}
          </div>

          <div className="flex-1 overflow-y-auto p-4 font-mono text-xs space-y-1">
            <AnimatePresence initial={false}>
              {logMessages.length === 0 && (
                <motion.p
                  key="empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-slate-700 italic pt-4 text-center"
                >
                  Waiting for research events…
                </motion.p>
              )}
              {logMessages.map((msg) => (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, x: -4 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.2 }}
                  className={`flex gap-3 py-0.5 leading-relaxed ${
                    msg.level === "error"
                      ? "text-red-400"
                      : msg.level === "warning"
                      ? "text-amber-400"
                      : msg.level === "success"
                      ? "text-emerald-400"
                      : "text-slate-400"
                  }`}
                >
                  <span className="text-slate-700 shrink-0">
                    {new Date(msg.timestamp).toLocaleTimeString("en-US", {
                      hour12: false,
                      hour: "2-digit",
                      minute: "2-digit",
                      second: "2-digit",
                    })}
                  </span>
                  <span className="shrink-0 uppercase text-[10px] font-semibold opacity-60 w-14 text-right">
                    {msg.stage ?? msg.level}
                  </span>
                  <span className="break-all">{msg.message}</span>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* ── Cancel Modal ── */}
      <Modal
        open={cancelModalOpen}
        onClose={() => setCancelModalOpen(false)}
        title="Cancel Research Job"
        size="sm"
      >
        <p className="text-slate-300 text-sm mb-6">
          Are you sure you want to cancel this research job? All progress will
          be lost and cannot be resumed.
        </p>
        <div className="flex gap-3 justify-end">
          <Button variant="ghost" size="sm" onClick={() => setCancelModalOpen(false)}>
            Keep Running
          </Button>
          <Button
            variant="danger"
            size="sm"
            loading={cancelling}
            onClick={handleCancel}
          >
            Cancel Job
          </Button>
        </div>
      </Modal>
    </>
  );
}
