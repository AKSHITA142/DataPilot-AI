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
  Terminal,
  Copy,
  Check,
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
  const [copiedLogs, setCopiedLogs] = useState(false);

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

  const copyLogText = () => {
    const text = logMessages
      .map(
        (m) =>
          `[${new Date(m.timestamp).toISOString()}] [${m.level.toUpperCase()}] ${
            m.stage ? `[${m.stage}] ` : ""
          }${m.message}`
      )
      .join("\n");
    navigator.clipboard.writeText(text);
    setCopiedLogs(true);
    setTimeout(() => setCopiedLogs(false), 2000);
  };

  const stages: TimelineStage[] = PIPELINE_STAGES.map((s) => ({
    id: s.id,
    label: s.label,
    description: s.description,
    status: job
      ? stageStatusForJob(s.id, currentStage ?? job.current_stage ?? null, job.status)
      : "waiting",
  }));

  // Progress Bar color mapping (Strict Semantic Colors)
  const progressBarColor =
    job?.status === "completed"
      ? "success"
      : job?.status === "failed"
      ? "error"
      : job?.status === "cancelled"
      ? "warning"
      : "brand";

  return (
    <>
      <div className="flex flex-col lg:flex-row h-full overflow-hidden">
        
        {/* ── LEFT PANE: Pipeline Stepper & Control Card ── */}
        <div className="w-full lg:max-w-md xl:max-w-lg flex-shrink-0 flex flex-col border-b lg:border-b-0 lg:border-r border-border-subtle overflow-y-auto">
          <div className="p-4 sm:p-6">
            {/* Job Header Card */}
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
                    <p className="text-[11px] text-text-muted mb-0.5 uppercase tracking-wider font-semibold">Research Job</p>
                    <p className="text-xs font-mono text-text-secondary truncate">{job.job_id}</p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    {/* Live WS indicator */}
                    <div className="flex items-center gap-1.5 text-xs px-2 py-0.5 rounded-full bg-surface-3 border border-border-subtle">
                      {wsConnected ? (
                        <>
                          <Wifi className="w-3 h-3 text-success-400" />
                          <span className="text-success-400 font-semibold text-[11px]">Live</span>
                        </>
                      ) : (
                        <>
                          <WifiOff className="w-3 h-3 text-text-muted" />
                          <span className="text-text-muted text-[11px]">Offline</span>
                        </>
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
                        Results
                      </Button>
                    )}
                  </div>
                </div>

                {/* Mission Card */}
                <GlassCard padding="sm" hover={false} className="mb-4">
                  <p className="text-[11px] text-text-muted uppercase tracking-wider mb-1 flex items-center gap-1.5 font-semibold">
                    <FlaskConical className="w-3 h-3 text-brand-400" /> Research Mission
                  </p>
                  <p className="text-xs sm:text-sm text-text leading-relaxed font-normal">{job.mission}</p>
                </GlassCard>

                {/* Global Progress Bar (Strict Semantic Color) */}
                <ProgressBar
                  value={job.status === "completed" ? 100 : progressPercent || job.progress_percent || 0}
                  label={
                    job.status === "completed"
                      ? "Research complete!"
                      : job.status === "failed"
                      ? "Job failed"
                      : currentStage
                      ? `Running: ${currentStage.replace(/_/g, " ")}…`
                      : "Initializing execution…"
                  }
                  color={progressBarColor}
                />

                {/* Started Timestamp */}
                <p className="text-[11px] text-text-muted mt-2 font-mono">
                  Started: {job.started_at ? formatDate(job.started_at) : formatDate(job.created_at)}
                </p>
              </motion.div>
            ) : null}

            {/* Error Banner (Red / Error) */}
            {job?.status === "failed" && (
              <motion.div
                initial={{ opacity: 0, scale: 0.96 }}
                animate={{ opacity: 1, scale: 1 }}
                className="mb-6 p-4 rounded-xl bg-error-500/10 border border-error-500/30 flex items-start gap-3"
              >
                <AlertTriangle className="w-4 h-4 text-error-400 shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-semibold text-error-400">Execution Error</p>
                  <p className="text-xs text-error-400/90 mt-1 font-mono leading-relaxed">
                    {job.error_message || "An unexpected error occurred while executing the research pipeline."}
                  </p>
                </div>
              </motion.div>
            )}

            {/* Success Banner */}
            {job?.status === "completed" && (
              <motion.div
                initial={{ opacity: 0, scale: 0.96 }}
                animate={{ opacity: 1, scale: 1 }}
                className="mb-6 p-4 rounded-xl bg-success-500/10 border border-success-500/25 text-center"
              >
                <p className="text-xs sm:text-sm font-semibold text-success-400">
                  ✓ Research Complete — Loading Experiment Leaderboard…
                </p>
              </motion.div>
            )}

            {/* Stepper Timeline */}
            <StageTimeline stages={stages} />
          </div>
        </div>

        {/* ── RIGHT PANE: Live Execution Console Stream ── */}
        <div className="flex-1 flex flex-col overflow-hidden bg-surface-1 min-h-[350px] lg:min-h-0">
          
          {/* Console Topbar Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-border-subtle bg-surface-2 shrink-0">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-brand-400" />
              <span className="text-xs font-semibold text-text uppercase tracking-wider">
                Live Execution Console
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-surface-3 text-text-muted font-mono">
                {logMessages.length} events
              </span>
            </div>

            <div className="flex items-center gap-2">
              {isLoading && <Spinner size="sm" />}
              {logMessages.length > 0 && (
                <button
                  onClick={copyLogText}
                  className="flex items-center gap-1 text-[11px] text-text-muted hover:text-text px-2 py-1 rounded bg-surface-3 border border-border-subtle transition-colors"
                  title="Copy log to clipboard"
                >
                  {copiedLogs ? <Check className="w-3 h-3 text-success-400" /> : <Copy className="w-3 h-3" />}
                  {copiedLogs ? "Copied" : "Copy"}
                </button>
              )}
            </div>
          </div>

          {/* Console Log Stream Window */}
          <div className="flex-1 overflow-y-auto p-4 font-mono text-xs space-y-1.5 bg-surface-1">
            <AnimatePresence initial={false}>
              {logMessages.length === 0 && (
                <motion.div
                  key="empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-text-muted italic pt-8 text-center flex flex-col items-center gap-2"
                >
                  <Spinner size="md" />
                  <p className="text-xs">Waiting for live WebSocket research events…</p>
                </motion.div>
              )}

              {logMessages.map((msg) => (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, x: -4 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.15 }}
                  className={`flex items-start gap-2.5 py-0.5 leading-relaxed ${
                    msg.level === "error"
                      ? "text-error-400 font-semibold"
                      : msg.level === "warning"
                      ? "text-warning-400"
                      : msg.level === "success"
                      ? "text-success-400 font-semibold"
                      : "text-text-secondary"
                  }`}
                >
                  <span className="text-text-muted shrink-0 text-[11px]">
                    {new Date(msg.timestamp).toLocaleTimeString("en-US", {
                      hour12: false,
                      hour: "2-digit",
                      minute: "2-digit",
                      second: "2-digit",
                    })}
                  </span>
                  <span className="shrink-0 uppercase text-[10px] font-bold opacity-60 w-16 text-right font-sans">
                    [{msg.stage ?? msg.level}]
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
        <p className="text-text-secondary text-sm mb-6 leading-relaxed">
          Are you sure you want to cancel this research job? All running ML experiments will be terminated immediately.
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
