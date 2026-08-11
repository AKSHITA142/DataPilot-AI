"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import {
  Briefcase,
  CheckCircle2,
  FlaskConical,
  TrendingUp,
  Clock,
  Zap,
  ArrowRight,
  Database,
  AlertTriangle,
  RefreshCw,
  Upload,
} from "lucide-react";
import { MetricCard } from "@/components/cards/MetricCard";
import { Badge } from "@/components/badges/Badge";
import { Button } from "@/components/buttons/Button";
import { Skeleton } from "@/components/loading/Loading";
import { AppPieChart } from "@/components/charts/Charts";
import { useDashboard, useDatasets } from "@/hooks/useResearch";
import { formatDate, formatBytes, formatNumber } from "@/utils/formatters";
import type { Job, JobStatus } from "@/types/api";

/* ── Stagger container ───────────────────────────────────── */
const stagger = {
  container: { hidden: {}, show: { transition: { staggerChildren: 0.04 } } },
  item: {
    hidden: { opacity: 0, y: 8 },
    show: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.28, ease: "easeOut" as const },
    },
  },
} as const;



/* ── Section heading ─────────────────────────────────────── */
function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-[11px] font-semibold uppercase tracking-widest text-text-muted mb-3 mt-0">
      {children}
    </p>
  );
}

/* ── Empty state ─────────────────────────────────────────── */
function EmptyState({
  icon: Icon,
  title,
  desc,
  action,
}: {
  icon: React.ElementType;
  title: string;
  desc: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center text-center gap-3 py-10 px-6">
      <div className="w-12 h-12 rounded-xl bg-surface-3 border border-border flex items-center justify-center mb-1">
        <Icon className="w-5 h-5 text-text-muted" />
      </div>
      <p className="text-sm font-semibold text-text-secondary">{title}</p>
      <p className="text-xs text-text-muted max-w-xs leading-relaxed">{desc}</p>
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}

/* ── Metric skeleton ─────────────────────────────────────── */
function MetricSkeleton() {
  return (
    <div className="card p-5 flex items-start gap-4">
      <Skeleton className="w-10 h-10 rounded-md shrink-0" />
      <div className="flex-1 space-y-2">
        <Skeleton className="h-3 w-24 rounded" />
        <Skeleton className="h-7 w-16 rounded" />
        <Skeleton className="h-2.5 w-32 rounded" />
      </div>
    </div>
  );
}

/* ── Recent Job row ──────────────────────────────────────── */
function RecentJobRow({ job, index }: { job: Job; index: number }) {
  const isTerminal =
    job.status === "completed" ||
    job.status === "failed" ||
    job.status === "cancelled";

  const dest = isTerminal
    ? `/experiments/${job.job_id}`
    : `/timeline/${job.job_id}`;

  return (
    <motion.div
      variants={stagger.item}
      className="
        flex items-start justify-between gap-4 px-4 py-3.5
        border-b border-border-subtle last:border-0
        hover:bg-surface-3 transition-colors group cursor-pointer
      "
      onClick={() => { window.location.href = dest; }}
    >
      <div className="flex items-start gap-3 min-w-0">
        <span className="text-xs font-mono text-text-muted shrink-0 pt-0.5 w-5 text-right">
          {index + 1}
        </span>
        <div className="min-w-0">
          <p className="text-sm text-text font-medium truncate leading-snug">
            {job.mission}
          </p>
          <p className="text-xs text-text-muted mt-0.5 font-mono truncate">
            {job.job_id.slice(0, 8)}&hellip;
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3 shrink-0">
        {job.status === "running" && job.current_stage && (
          <span className="hidden sm:inline text-[10px] text-text-muted uppercase tracking-wide">
            {job.current_stage}
          </span>
        )}
        <Badge variant={job.status as JobStatus} label={job.status} />
        <span className="hidden md:inline text-xs text-text-muted whitespace-nowrap">
          {formatDate(job.created_at)}
        </span>
        <ArrowRight className="w-3.5 h-3.5 text-text-muted opacity-0 group-hover:opacity-100 transition-opacity" />
      </div>
    </motion.div>
  );
}

/* ── Main dashboard page ─────────────────────────────────── */
export default function DashboardPage() {
  const { data: dash, isLoading: dashLoading, error: dashError, refetch } = useDashboard();
  const { data: datasets, isLoading: datasetsLoading } = useDatasets();

  /* Derived: success rate */
  const successRate =
    dash && dash.total_jobs > 0
      ? Math.round((dash.completed_jobs / dash.total_jobs) * 100)
      : null;

  const runningJobs =
    dash?.recent_jobs.filter((j) => j.status === "running").length ?? 0;

  /* Pie chart data from recent_jobs status distribution */
  const jobStatusCounts: Record<string, number> = {};
  for (const job of dash?.recent_jobs ?? []) {
    jobStatusCounts[job.status] = (jobStatusCounts[job.status] ?? 0) + 1;
  }
  const pieData = Object.entries(jobStatusCounts).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value,
  }));

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 md:py-8">

      {/* Page header */}
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8"
      >
        <div>
          <h1 className="text-xl font-bold text-text tracking-tight">
            Research Overview
          </h1>
          <p className="text-sm text-text-muted mt-0.5">
            All your ML research runs, datasets, and experiment history.
          </p>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={() => refetch()}
            className="p-2 rounded-md text-text-muted hover:text-text hover:bg-surface-3 transition-colors"
            title="Refresh"
            aria-label="Refresh dashboard"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <Link href="/upload">
            <Button variant="primary" size="sm" icon={<Zap className="w-3.5 h-3.5" />}>
              New Run
            </Button>
          </Link>
        </div>
      </motion.div>

      {/* Error banner */}
      {dashError && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="card p-4 mb-6 flex items-center gap-3"
          style={{ borderColor: "var(--error)" }}
        >
          <AlertTriangle className="w-4 h-4 text-error-400 shrink-0" />
          <p className="text-sm text-text-secondary">
            Could not load dashboard data — is the backend running?
          </p>
          <button
            onClick={() => refetch()}
            className="ml-auto text-xs text-brand-400 hover:text-brand-300 transition-colors"
          >
            Retry
          </button>
        </motion.div>
      )}

      {/* KPI metrics grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-8">
        {dashLoading ? (
          <>
            <MetricSkeleton />
            <MetricSkeleton />
            <MetricSkeleton />
            <MetricSkeleton />
          </>
        ) : (
          <>
            <MetricCard
              label="Total Jobs"
              value={dash ? formatNumber(dash.total_jobs) : "—"}
              icon={<Briefcase className="w-5 h-5" />}
              subtext={
                runningJobs > 0
                  ? `${runningJobs} currently running`
                  : "No active runs"
              }
              accent="brand"
            />
            <MetricCard
              label="Completed"
              value={dash ? formatNumber(dash.completed_jobs) : "—"}
              icon={<CheckCircle2 className="w-5 h-5" />}
              subtext="Fully processed research jobs"
              accent="success"
            />
            <MetricCard
              label="Success Rate"
              value={successRate !== null ? `${successRate}%` : "—"}
              icon={<TrendingUp className="w-5 h-5" />}
              subtext={
                dash?.total_jobs
                  ? `${dash.completed_jobs} of ${dash.total_jobs} jobs`
                  : "No jobs yet"
              }
              accent={
                successRate === null
                  ? "neutral"
                  : successRate >= 80
                  ? "success"
                  : successRate >= 50
                  ? "warning"
                  : "error"
              }
            />
            <MetricCard
              label="Experiments"
              value={dash ? formatNumber(dash.total_experiments) : "—"}
              icon={<FlaskConical className="w-5 h-5" />}
              subtext="Total ML pipeline executions"
              accent="neutral"
            />
          </>
        )}
      </div>

      {/* Two-column: recent jobs + breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">

        {/* Recent Jobs — 2/3 width */}
        <div className="lg:col-span-2">
          <SectionLabel>Recent Research Jobs</SectionLabel>
          <div className="card overflow-hidden">
            {dashLoading ? (
              <div className="p-4 space-y-3">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <Skeleton className="h-4 w-4 rounded" />
                    <div className="flex-1 space-y-1.5">
                      <Skeleton className="h-3.5 w-3/4 rounded" />
                      <Skeleton className="h-2.5 w-1/3 rounded" />
                    </div>
                    <Skeleton className="h-5 w-16 rounded-full" />
                  </div>
                ))}
              </div>
            ) : !dash || dash.recent_jobs.length === 0 ? (
              <EmptyState
                icon={Briefcase}
                title="No research jobs yet"
                desc="Upload a CSV dataset and define a mission to start your first automated ML research run."
                action={
                  <Link href="/upload">
                    <Button
                      variant="primary"
                      size="sm"
                      icon={<Upload className="w-3.5 h-3.5" />}
                    >
                      Start First Run
                    </Button>
                  </Link>
                }
              />
            ) : (
              <motion.div
                variants={stagger.container}
                initial="hidden"
                animate="show"
              >
                {dash.recent_jobs.map((job, i) => (
                  <RecentJobRow key={job.job_id} job={job} index={i} />
                ))}
              </motion.div>
            )}
          </div>
        </div>

        {/* Status breakdown donut — 1/3 width */}
        <div>
          <SectionLabel>Status Breakdown</SectionLabel>
          <div className="card p-5">
            {dashLoading ? (
              <div className="flex items-center justify-center h-52">
                <Skeleton className="w-36 h-36 rounded-full" />
              </div>
            ) : pieData.length === 0 ? (
              <EmptyState
                icon={Clock}
                title="No data yet"
                desc="Status breakdown appears once you have research jobs."
              />
            ) : (
              <>
                <AppPieChart data={pieData} height={200} innerRadius={52} />
                <div className="mt-3 space-y-1.5 border-t border-border-subtle pt-3">
                  {Object.entries(jobStatusCounts).map(([status, count]) => (
                    <div
                      key={status}
                      className="flex items-center justify-between text-xs"
                    >
                      <span className="text-text-muted capitalize">{status}</span>
                      <span className="font-semibold tabular-nums text-text">
                        {count}
                      </span>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Datasets table */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-3">
          <SectionLabel>Uploaded Datasets</SectionLabel>
          <Link
            href="/upload"
            className="text-xs text-brand-400 hover:text-brand-300 transition-colors flex items-center gap-1"
          >
            Upload new <ArrowRight className="w-3 h-3" />
          </Link>
        </div>

        <div className="card overflow-hidden">
          {datasetsLoading ? (
            <div className="divide-y divide-border-subtle">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="flex items-center gap-4 px-4 py-3">
                  <Skeleton className="w-8 h-8 rounded-md shrink-0" />
                  <div className="flex-1 space-y-1.5">
                    <Skeleton className="h-3.5 w-1/2 rounded" />
                    <Skeleton className="h-2.5 w-1/3 rounded" />
                  </div>
                  <Skeleton className="h-4 w-20 rounded" />
                </div>
              ))}
            </div>
          ) : !datasets || datasets.length === 0 ? (
            <EmptyState
              icon={Database}
              title="No datasets uploaded"
              desc="Upload a CSV file to begin. DataPilot-AI will profile it and run your research mission automatically."
              action={
                <Link href="/upload">
                  <Button
                    variant="primary"
                    size="sm"
                    icon={<Upload className="w-3.5 h-3.5" />}
                  >
                    Upload Dataset
                  </Button>
                </Link>
              }
            />
          ) : (
            <>
              {/* Table header — hidden on mobile */}
              <div className="hidden md:grid grid-cols-[1fr_90px_90px_110px_90px] gap-4 px-4 py-2 border-b border-border-subtle">
                {["Dataset", "Rows", "Cols", "Size", "Status"].map((h) => (
                  <span
                    key={h}
                    className="text-[10px] font-semibold uppercase tracking-wider text-text-muted"
                  >
                    {h}
                  </span>
                ))}
              </div>

              <motion.div
                variants={stagger.container}
                initial="hidden"
                animate="show"
                className="divide-y divide-border-subtle"
              >
                {datasets.map((ds) => (
                  <motion.div
                    key={ds.dataset_id}
                    variants={stagger.item}
                    className="
                      flex flex-col sm:grid sm:grid-cols-[1fr_90px_90px_110px_90px]
                      gap-2 sm:gap-4 px-4 py-3
                      hover:bg-surface-3 transition-colors
                      items-start sm:items-center
                    "
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div className="w-7 h-7 rounded-md bg-surface-3 border border-border flex items-center justify-center shrink-0">
                        <Database className="w-3.5 h-3.5 text-text-muted" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm text-text font-medium truncate leading-snug">
                          {ds.filename}
                        </p>
                        <p className="text-[10px] text-text-muted font-mono truncate">
                          {formatDate(ds.upload_timestamp)}
                        </p>
                      </div>
                    </div>

                    <span className="text-sm tabular-nums text-text-secondary">
                      {ds.row_count != null ? formatNumber(ds.row_count) : "—"}
                    </span>
                    <span className="text-sm tabular-nums text-text-secondary">
                      {ds.column_count != null ? formatNumber(ds.column_count) : "—"}
                    </span>
                    <span className="text-sm tabular-nums text-text-secondary">
                      {formatBytes(ds.file_size_bytes)}
                    </span>

                    <span
                      className={`
                        inline-flex text-[10px] font-semibold uppercase tracking-wide
                        px-2 py-0.5 rounded-full w-fit
                        ${ds.status === "profiled"
                          ? "text-success-400 bg-success-500/10"
                          : ds.status === "processing"
                          ? "text-brand-400 bg-brand-500/10"
                          : "text-text-muted bg-surface-3"
                        }
                      `}
                    >
                      {ds.status}
                    </span>
                  </motion.div>
                ))}
              </motion.div>
            </>
          )}
        </div>
      </div>

      {/* Quick-start CTA — only when there are no jobs */}
      {!dashLoading && dash && dash.total_jobs === 0 && (
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card p-8 flex flex-col sm:flex-row items-center gap-6"
        >
          <div className="w-14 h-14 rounded-xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center shrink-0">
            <Zap className="w-7 h-7 text-brand-400" />
          </div>
          <div className="text-center sm:text-left flex-1">
            <h2 className="text-base font-bold text-text mb-1">
              Start your first research run
            </h2>
            <p className="text-sm text-text-muted leading-relaxed">
              Upload a CSV, define your research mission, and let DataPilot-AI
              autonomously profile your data, run 10+ ML experiments, build a
              knowledge base, and deliver a production-ready recommendation.
            </p>
          </div>
          <Link href="/upload" className="shrink-0">
            <Button
              variant="primary"
              size="lg"
              icon={<ArrowRight className="w-4 h-4" />}
            >
              Upload Dataset
            </Button>
          </Link>
        </motion.div>
      )}

    </div>
  );
}
