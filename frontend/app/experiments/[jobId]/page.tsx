"use client";

import { use, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Brain,
  Filter,
  GitCompare,
  ChevronDown,
  ChevronUp,
  Trophy,
  ArrowRight,
} from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/buttons/Button";
import { Badge } from "@/components/badges/Badge";
import { GlassCard } from "@/components/cards/GlassCard";
import { SkeletonTable } from "@/components/loading/Loading";
import { HorizontalBarChart, AppScatterChart } from "@/components/charts/Charts";
import { Modal } from "@/components/modals/Modal";
import { useExperiments } from "@/hooks/useResearch";
import { useExperimentStore } from "@/store/experimentStore";
import { formatMetric, formatDuration, snakeToTitle } from "@/utils/formatters";
import type { ExperimentResult } from "@/types/api";
import { useRouter } from "next/navigation";

function ExperimentRow({
  exp,
  rank,
  selected,
  onToggleSelect,
}: {
  exp: ExperimentResult;
  rank: number;
  selected: boolean;
  onToggleSelect: () => void;
}) {
  const [expanded, setExpanded] = useState(false);

  const featureData = exp.feature_importance
    ? Object.entries(exp.feature_importance)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 8)
        .map(([name, value]) => ({ name, value }))
    : [];

  return (
    <>
      <motion.tr
        layout
        initial={{ opacity: 0, y: 4 }}
        animate={{ opacity: 1, y: 0 }}
        className={`border-b border-slate-800/60 hover:bg-slate-800/30 transition-colors cursor-pointer ${
          selected ? "bg-indigo-500/5 border-l-2 border-l-indigo-500" : ""
        }`}
        onClick={() => setExpanded((p) => !p)}
      >
        {/* Rank */}
        <td className="px-4 py-3 text-center">
          {rank === 1 ? (
            <Trophy className="w-4 h-4 text-amber-400 mx-auto" />
          ) : (
            <span className="text-xs text-slate-600">#{rank}</span>
          )}
        </td>
        {/* Select */}
        <td className="px-3 py-3" onClick={(e) => { e.stopPropagation(); onToggleSelect(); }}>
          <input
            type="checkbox"
            checked={selected}
            onChange={onToggleSelect}
            className="w-3.5 h-3.5 accent-indigo-500 cursor-pointer"
          />
        </td>
        {/* Model */}
        <td className="px-4 py-3">
          <div>
            <p className="text-sm font-medium text-slate-200">{exp.model_name}</p>
            <p className="text-xs text-slate-600 mt-0.5">{exp.model_type}</p>
          </div>
        </td>
        {/* Pipeline */}
        <td className="px-4 py-3">
          <div className="flex flex-wrap gap-1">
            {exp.pipeline_steps?.slice(0, 3).map((step) => (
              <span
                key={step}
                className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono"
              >
                {step}
              </span>
            ))}
            {(exp.pipeline_steps?.length ?? 0) > 3 && (
              <span className="text-[10px] text-slate-600">
                +{(exp.pipeline_steps?.length ?? 0) - 3}
              </span>
            )}
          </div>
        </td>
        {/* Primary metric */}
        <td className="px-4 py-3 text-right">
          {exp.primary_metric_value !== undefined ? (
            <span className="text-sm font-semibold text-indigo-300">
              {formatMetric(exp.primary_metric_value)}
            </span>
          ) : "—"}
          {exp.primary_metric_name && (
            <p className="text-[10px] text-slate-600">{exp.primary_metric_name}</p>
          )}
        </td>
        {/* Composite score */}
        <td className="px-4 py-3 text-right">
          <span className="text-sm font-bold text-violet-300">
            {exp.composite_score !== undefined
              ? formatMetric(exp.composite_score)
              : "—"}
          </span>
        </td>
        {/* Runtime */}
        <td className="px-4 py-3 text-right text-xs text-slate-500">
          {exp.runtime_seconds
            ? formatDuration(exp.runtime_seconds)
            : "—"}
        </td>
        {/* Status */}
        <td className="px-4 py-3">
          <Badge variant={exp.status === "pending" ? "queued" : (exp.status as "running" | "completed" | "failed")} label={exp.status} />
        </td>
        {/* Expand */}
        <td className="px-3 py-3 text-slate-600">
          {expanded ? (
            <ChevronUp className="w-4 h-4" />
          ) : (
            <ChevronDown className="w-4 h-4" />
          )}
        </td>
      </motion.tr>

      {/* Expanded detail row */}
      <AnimatePresence>
        {expanded && (
          <tr>
            <td colSpan={9} className="bg-slate-900/50 border-b border-slate-800/60">
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="px-6 py-5 grid grid-cols-1 md:grid-cols-2 gap-6"
              >
                {/* Metrics */}
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wider mb-3 font-medium">
                    All Metrics
                  </p>
                  <div className="grid grid-cols-2 gap-2">
                    {[
                      ["Accuracy", exp.accuracy],
                      ["F1 Score", exp.f1_score],
                      ["Precision", exp.precision],
                      ["Recall", exp.recall],
                      ["ROC-AUC", exp.roc_auc],
                      ["RMSE", exp.rmse],
                      ["MAE", exp.mae],
                      ["R²", exp.r2],
                    ]
                      .filter(([, v]) => v !== undefined)
                      .map(([label, value]) => (
                        <div
                          key={label as string}
                          className="flex justify-between items-center px-3 py-2 rounded-lg bg-slate-800/50"
                        >
                          <span className="text-xs text-slate-500">{label as string}</span>
                          <span className="text-xs font-semibold text-slate-200">
                            {formatMetric(value as number)}
                          </span>
                        </div>
                      ))}
                  </div>
                </div>

                {/* Feature Importance */}
                {featureData.length > 0 && (
                  <div>
                    <p className="text-xs text-slate-500 uppercase tracking-wider mb-3 font-medium">
                      Feature Importance
                    </p>
                    <HorizontalBarChart data={featureData} height={200} />
                  </div>
                )}
              </motion.div>
            </td>
          </tr>
        )}
      </AnimatePresence>
    </>
  );
}

export default function ExperimentsPage({
  params,
}: {
  params: Promise<{ jobId: string }>;
}) {
  const { jobId } = use(params);
  const router = useRouter();
  const { data: experiments, isLoading } = useExperiments(jobId);

  const {
    filterModelType,
    filterStatus,
    selectedIds,
    compareModalOpen,
    setFilterModelType,
    setFilterStatus,
    toggleSelectExperiment,
    clearSelection,
    setCompareModalOpen,
  } = useExperimentStore();

  // Filter experiments
  const filtered = (experiments ?? [])
    .filter((e) => !filterModelType || e.model_type === filterModelType)
    .filter((e) => !filterStatus || e.status === filterStatus)
    .sort(
      (a, b) => (b.composite_score ?? 0) - (a.composite_score ?? 0)
    );

  // Scatter data: runtime vs composite score
  const scatterData = filtered
    .filter((e) => e.runtime_seconds && e.composite_score !== undefined)
    .map((e) => ({
      x: e.runtime_seconds!,
      y: e.composite_score!,
      name: e.model_name,
    }));

  const modelTypes = [...new Set((experiments ?? []).map((e) => e.model_type))];
  const selectedExps = (experiments ?? []).filter((e) =>
    selectedIds.has(e.experiment_id)
  );

  return (
    <main className="min-h-screen bg-slate-950">
      {/* Nav */}
      <nav className="sticky top-0 z-30 flex items-center justify-between px-6 py-4 bg-slate-950/90 backdrop-blur-md border-b border-slate-800/60">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
            <Brain className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-sm tracking-tight">
            DataPilot<span className="text-indigo-400">-AI</span>
          </span>
        </Link>

        <div className="flex items-center gap-2">
          {selectedIds.size >= 2 && (
            <Button
              variant="secondary"
              size="sm"
              icon={<GitCompare className="w-3.5 h-3.5" />}
              onClick={() => setCompareModalOpen(true)}
            >
              Compare ({selectedIds.size})
            </Button>
          )}
          <Button
            variant="primary"
            size="sm"
            icon={<ArrowRight className="w-3.5 h-3.5" />}
            onClick={() => router.push(`/recommendation/${jobId}`)}
          >
            Final Report
          </Button>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Page header */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-2xl font-black text-slate-100 mb-1">
            Experiment Leaderboard
          </h1>
          <p className="text-sm text-slate-500">
            {filtered.length} experiments ranked by composite score
          </p>
        </motion.div>

        {/* Scatter chart */}
        {scatterData.length > 0 && (
          <GlassCard className="mb-6">
            <p className="text-xs text-slate-500 uppercase tracking-wider font-medium mb-4">
              Runtime vs. Score Trade-off
            </p>
            <AppScatterChart
              data={scatterData}
              xLabel="Runtime (s)"
              yLabel="Composite Score"
              height={220}
            />
          </GlassCard>
        )}

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3 mb-4">
          <div className="flex items-center gap-1.5 text-xs text-slate-500">
            <Filter className="w-3.5 h-3.5" />
            Filters:
          </div>
          <select
            value={filterModelType ?? ""}
            onChange={(e) => setFilterModelType(e.target.value || null)}
            className="text-xs px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 focus:outline-none"
          >
            <option value="">All Model Types</option>
            {modelTypes.map((t) => (
              <option key={t} value={t}>{snakeToTitle(t)}</option>
            ))}
          </select>
          <select
            value={filterStatus ?? ""}
            onChange={(e) => setFilterStatus(e.target.value || null)}
            className="text-xs px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 focus:outline-none"
          >
            <option value="">All Statuses</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
            <option value="running">Running</option>
          </select>
          {(filterModelType || filterStatus) && (
            <button
              onClick={() => { setFilterModelType(null); setFilterStatus(null); }}
              className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors"
            >
              Clear filters
            </button>
          )}
          {selectedIds.size > 0 && (
            <button
              onClick={clearSelection}
              className="text-xs text-slate-500 hover:text-slate-300 transition-colors ml-auto"
            >
              Clear selection
            </button>
          )}
        </div>

        {/* Leaderboard table */}
        <GlassCard padding="none">
          {isLoading ? (
            <div className="p-6">
              <SkeletonTable rows={6} />
            </div>
          ) : filtered.length === 0 ? (
            <div className="p-12 text-center">
              <p className="text-slate-600 text-sm">No experiments found.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-slate-800/60">
                    {["#", "✓", "Model", "Pipeline", "Primary Metric", "Score", "Runtime", "Status", ""].map((h) => (
                      <th key={h} className="px-4 py-3 text-xs font-medium text-slate-500 uppercase tracking-wider whitespace-nowrap">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((exp, i) => (
                    <ExperimentRow
                      key={exp.experiment_id}
                      exp={exp}
                      rank={i + 1}
                      selected={selectedIds.has(exp.experiment_id)}
                      onToggleSelect={() => toggleSelectExperiment(exp.experiment_id)}
                    />
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </GlassCard>
      </div>

      {/* Compare Modal */}
      <Modal
        open={compareModalOpen}
        onClose={() => setCompareModalOpen(false)}
        title={`Comparing ${selectedExps.length} Experiments`}
        size="xl"
      >
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left text-xs text-slate-500 py-2 pr-4">Metric</th>
                {selectedExps.map((e) => (
                  <th key={e.experiment_id} className="text-center text-xs text-slate-300 py-2 px-4">
                    {e.model_name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[
                ["Composite Score", "composite_score"],
                ["Accuracy", "accuracy"],
                ["F1 Score", "f1_score"],
                ["ROC-AUC", "roc_auc"],
                ["Runtime (s)", "runtime_seconds"],
              ].map(([label, key]) => (
                <tr key={key} className="border-b border-slate-800/40">
                  <td className="text-xs text-slate-500 py-2 pr-4">{label}</td>
                  {selectedExps.map((e) => {
                    const val = e[key as keyof ExperimentResult] as number | undefined;
                    return (
                      <td key={e.experiment_id} className="text-center text-xs font-semibold text-slate-200 py-2 px-4">
                        {val !== undefined ? formatMetric(val) : "—"}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Modal>
    </main>
  );
}
