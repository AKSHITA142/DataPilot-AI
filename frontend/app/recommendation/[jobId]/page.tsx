"use client";

import { use } from "react";
import { motion } from "framer-motion";
import {
  Brain,
  Trophy,
  Download,
  CheckCircle2,
  Lightbulb,
  Wrench,
  ChevronLeft,
  ArrowRight,
  ShieldAlert,
  Sparkles,
  BarChart3,
  Layers,
  FlaskConical,
  BookOpen,
} from "lucide-react";
import { Button } from "@/components/buttons/Button";
import { GlassCard } from "@/components/cards/GlassCard";
import { MetricCard } from "@/components/cards/MetricCard";
import { SkeletonCard } from "@/components/loading/Loading";
import { HorizontalBarChart } from "@/components/charts/Charts";
import { useReport, useExperiments, useDataset } from "@/hooks/useResearch";
import { downloadReport } from "@/services/apiClient";
import { formatMetric } from "@/utils/formatters";
import { useRouter } from "next/navigation";

export default function RecommendationPage({
  params,
}: {
  params: Promise<{ jobId: string }>;
}) {
  const { jobId } = use(params);
  const router = useRouter();
  const { data: report, isLoading } = useReport(jobId);
  const { data: experiments } = useExperiments(jobId);
  const { data: dataset } = useDataset(report?.dataset_id ?? null);

  const rec = report?.recommendation;

  // Feature importance for winner experiment
  const winnerExp = experiments?.find(
    (e) => e.experiment_id === rec?.experiment_id
  );
  const featureData = winnerExp?.feature_importance
    ? Object.entries(winnerExp.feature_importance)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 10)
        .map(([name, value]) => ({ name, value }))
    : [];

  const qualityWarnings = dataset?.profile?.quality_warnings ?? [];

  const handleDownload = async (format: "html" | "markdown") => {
    if (!report?.report_id) return;
    try {
      const blob = await downloadReport(report.report_id, format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `datapilot-report.${format === "html" ? "html" : "md"}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      // ignore download errors
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6 md:py-8">
      {/* ── Page Header / Action Bar ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="sm"
            icon={<ChevronLeft className="w-3.5 h-3.5" />}
            onClick={() => router.push(`/experiments/${jobId}`)}
          >
            Leaderboard
          </Button>
          <span className="text-text-muted text-xs">•</span>
          <span className="text-xs font-mono text-text-muted">Job {jobId.slice(0, 8)}</span>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            icon={<BookOpen className="w-3.5 h-3.5" />}
            onClick={() => router.push(`/knowledge/${jobId}`)}
          >
            Knowledge Base
          </Button>
          <Button
            variant="secondary"
            size="sm"
            icon={<Download className="w-3.5 h-3.5" />}
            onClick={() => handleDownload("markdown")}
          >
            Export Report
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-6">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : !rec ? (
        <GlassCard className="text-center py-16 flex flex-col items-center gap-3">
          <FlaskConical className="w-10 h-10 text-text-muted" />
          <p className="text-text font-semibold text-base">Recommendation Not Ready</p>
          <p className="text-text-muted text-xs max-w-sm">
            The AI research engine is still evaluating model experiments. Check the timeline for real-time progress.
          </p>
          <Button
            variant="primary"
            size="sm"
            onClick={() => router.push(`/timeline/${jobId}`)}
            className="mt-2"
          >
            View Timeline
          </Button>
        </GlassCard>
      ) : (
        <>
          {/* ── 1. PRIMARY RESULT HERO BANNER ── */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="relative card p-6 sm:p-8 mb-8 overflow-hidden border border-success-500/30 bg-surface-2"
          >
            {/* Background subtle radial glow */}
            <div
              className="absolute -top-24 -right-24 w-80 h-80 rounded-full pointer-events-none"
              style={{
                background:
                  "radial-gradient(circle, rgba(34,197,94,0.12) 0%, transparent 70%)",
              }}
            />

            <div className="relative z-10 flex flex-col lg:flex-row items-start justify-between gap-6">
              <div className="flex-1 min-w-0">
                {/* Winner Pill */}
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-success-500/10 border border-success-500/25 text-success-400 text-xs font-semibold mb-3">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Top Recommended Pipeline
                </div>

                <h1 className="text-2xl sm:text-3xl font-bold text-text mb-3 tracking-tight">
                  {rec.recommended_model}
                </h1>

                {/* Connected Pipeline Steps Flow */}
                <div className="flex items-center gap-1.5 flex-wrap">
                  <span className="text-xs text-text-muted font-medium mr-1 flex items-center gap-1">
                    <Layers className="w-3.5 h-3.5 text-brand-400" /> Pipeline:
                  </span>
                  {rec.recommended_pipeline.map((step, idx) => (
                    <div key={step} className="flex items-center gap-1.5">
                      <span className="text-xs px-2.5 py-1 rounded-md bg-surface-3 border border-border text-text font-mono">
                        {step}
                      </span>
                      {idx < rec.recommended_pipeline.length - 1 && (
                        <ArrowRight className="w-3 h-3 text-text-muted" />
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Confidence Score Gauge Card (Tremor Style) */}
              <div className="flex items-center gap-4 bg-surface-3 p-4 rounded-xl border border-border shrink-0 self-stretch sm:self-auto justify-center">
                <div className="relative w-16 h-16 shrink-0">
                  <svg viewBox="0 0 80 80" className="w-16 h-16 -rotate-90">
                    <circle cx="40" cy="40" r="32" fill="none" stroke="var(--border)" strokeWidth="6" />
                    <circle
                      cx="40" cy="40" r="32" fill="none"
                      stroke="var(--success)" strokeWidth="6"
                      strokeLinecap="round"
                      strokeDasharray={`${2 * Math.PI * 32}`}
                      strokeDashoffset={`${2 * Math.PI * 32 * (1 - rec.confidence_score)}`}
                      style={{ transition: "stroke-dashoffset 1s ease" }}
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-base font-bold text-success-400 font-mono">
                      {(rec.confidence_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
                <div>
                  <p className="text-xs text-text-muted uppercase tracking-wider font-semibold">
                    Confidence
                  </p>
                  <p className="text-sm font-bold text-text mt-0.5">High Certainty</p>
                  <p className="text-[10px] text-text-muted">Based on cross-validation</p>
                </div>
              </div>
            </div>
          </motion.div>

          {/* ── 2. SUPPORTING METRICS GRID ── */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-8">
            <MetricCard
              label={rec.primary_metric_name}
              value={formatMetric(rec.primary_metric_value)}
              icon={<Trophy className="w-5 h-5" />}
              subtext="Primary validation score"
              accent="success"
            />
            <MetricCard
              label="Composite Score"
              value={formatMetric(rec.composite_score)}
              icon={<Sparkles className="w-5 h-5" />}
              subtext="Multi-objective score"
              accent="brand"
            />
            <MetricCard
              label="Experiments Run"
              value={report?.experiment_count ?? "—"}
              icon={<FlaskConical className="w-5 h-5" />}
              subtext="Pipelines evaluated"
              accent="neutral"
            />
            <MetricCard
              label="Findings Extracted"
              value={report?.knowledge_findings_count ?? "—"}
              icon={<Lightbulb className="w-5 h-5" />}
              subtext="Knowledge base insights"
              accent="neutral"
            />
          </div>

          {/* ── 3. REASONING & STRATEGIC EXPLANATION ── */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="mb-8"
          >
            <div className="card p-6 border-l-4 border-l-brand-500 bg-surface-2">
              <p className="text-xs text-brand-400 uppercase tracking-widest font-semibold mb-2.5 flex items-center gap-2">
                <Brain className="w-4 h-4" />
                AI Scientist Reasoning & Strategy
              </p>
              <p className="text-sm text-text leading-relaxed text-slate-200">
                {rec.reasoning}
              </p>
            </div>
          </motion.div>

          {/* ── 4. DATA QUALITY WARNINGS (IF GENUINE WARNINGS EXIST) ── */}
          {qualityWarnings.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="mb-8"
            >
              <div className="card p-6 border-l-4 border-l-warning-500 bg-surface-2">
                <p className="text-xs text-warning-400 uppercase tracking-widest font-semibold mb-3 flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4" />
                  Dataset Quality Alerts ({qualityWarnings.length})
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {qualityWarnings.map((w, idx) => (
                    <div key={idx} className="p-3 rounded-lg bg-surface-3 border border-border-subtle text-xs">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-semibold text-text font-mono">{w.column ?? "Dataset"}</span>
                        <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded ${
                          w.severity === "high" ? "bg-error-500/20 text-error-400" : "bg-warning-500/20 text-warning-400"
                        }`}>
                          {w.severity}
                        </span>
                      </div>
                      <p className="text-text-muted">{w.message}</p>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {/* ── 5. KEY FINDINGS + IMPLEMENTATION GUIDE (SIDE-BY-SIDE) ── */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            {/* Key Findings */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.25 }}
            >
              <div className="card p-6 h-full flex flex-col">
                <p className="text-xs text-text-muted uppercase tracking-widest font-semibold mb-4 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-success-400" />
                  Key Findings & Insights
                </p>
                <ul className="space-y-3 flex-1">
                  {rec.key_findings.map((f, i) => (
                    <li key={i} className="flex items-start gap-3 text-xs leading-relaxed text-text-secondary">
                      <span className="w-5 h-5 rounded-full bg-success-500/15 text-success-400 font-semibold flex items-center justify-center shrink-0 mt-0.5 text-[10px]">
                        ✓
                      </span>
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </motion.div>

            {/* Implementation Tips */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <div className="card p-6 h-full flex flex-col">
                <p className="text-xs text-text-muted uppercase tracking-widest font-semibold mb-4 flex items-center gap-2">
                  <Wrench className="w-4 h-4 text-brand-400" />
                  Deployment & Implementation Steps
                </p>
                <ol className="space-y-3 flex-1">
                  {rec.implementation_tips.map((tip, i) => (
                    <li key={i} className="flex items-start gap-3 text-xs leading-relaxed text-text-secondary">
                      <span className="w-5 h-5 rounded-full bg-brand-500/15 text-brand-400 font-bold font-mono flex items-center justify-center shrink-0 mt-0.5 text-[10px]">
                        {i + 1}
                      </span>
                      <span>{tip}</span>
                    </li>
                  ))}
                </ol>
              </div>
            </motion.div>
          </div>

          {/* ── 6. FEATURE IMPORTANCE VISUALIZER ── */}
          {featureData.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.35 }}
              className="mb-8"
            >
              <div className="card p-6">
                <div className="flex items-center justify-between mb-4">
                  <p className="text-xs text-text-muted uppercase tracking-widest font-semibold flex items-center gap-2">
                    <BarChart3 className="w-4 h-4 text-brand-400" />
                    Feature Importance — Top Predictors
                  </p>
                  <span className="text-[10px] text-text-muted font-mono">{rec.recommended_model}</span>
                </div>
                <HorizontalBarChart data={featureData} height={240} />
              </div>
            </motion.div>
          )}

          {/* ── 7. DOWNLOAD & EXPORT ACTIONS ── */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="card p-6 flex flex-col sm:flex-row items-center justify-between gap-4"
          >
            <div>
              <p className="text-sm font-bold text-text mb-0.5">Export Production Report</p>
              <p className="text-xs text-text-muted">
                Download full standalone HTML or Markdown research summary for your team.
              </p>
            </div>
            <div className="flex flex-wrap gap-2.5 shrink-0">
              <Button
                variant="primary"
                size="sm"
                icon={<Download className="w-3.5 h-3.5" />}
                onClick={() => handleDownload("html")}
              >
                HTML Report
              </Button>
              <Button
                variant="secondary"
                size="sm"
                icon={<Download className="w-3.5 h-3.5" />}
                onClick={() => handleDownload("markdown")}
              >
                Markdown Report
              </Button>
            </div>
          </motion.div>
        </>
      )}
    </div>
  );
}
