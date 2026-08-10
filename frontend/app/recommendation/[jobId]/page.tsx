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
} from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/buttons/Button";
import { GlassCard } from "@/components/cards/GlassCard";
import { MetricCard } from "@/components/cards/MetricCard";
import { SkeletonCard } from "@/components/loading/Loading";
import { HorizontalBarChart } from "@/components/charts/Charts";
import { useReport, useExperiments } from "@/hooks/useResearch";
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
      // ignore
    }
  };

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
          <Button
            variant="ghost"
            size="sm"
            icon={<ChevronLeft className="w-3.5 h-3.5" />}
            onClick={() => router.push(`/experiments/${jobId}`)}
          >
            Experiments
          </Button>
          <Button
            variant="secondary"
            size="sm"
            icon={<Download className="w-3.5 h-3.5" />}
            onClick={() => handleDownload("markdown")}
          >
            Download Report
          </Button>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-10">
        {isLoading ? (
          <div className="space-y-6">
            <SkeletonCard />
            <SkeletonCard />
          </div>
        ) : !rec ? (
          <GlassCard className="text-center py-16">
            <p className="text-slate-600 text-sm">
              Report not available yet. Wait for the research job to complete.
            </p>
          </GlassCard>
        ) : (
          <>
            {/* ── Winner Hero Card ── */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="relative glass-card p-8 mb-8 overflow-hidden"
            >
              {/* Background glow */}
              <div
                className="absolute -top-20 -right-20 w-64 h-64 rounded-full pointer-events-none"
                style={{
                  background:
                    "radial-gradient(circle, rgba(245,158,11,0.12) 0%, transparent 70%)",
                }}
              />

              <div className="relative z-10 flex flex-col sm:flex-row items-start gap-6">
                {/* Trophy icon */}
                <div className="w-16 h-16 rounded-2xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center shrink-0">
                  <Trophy className="w-8 h-8 text-amber-400" />
                </div>

                <div className="flex-1 min-w-0">
                  <p className="text-xs text-amber-400 uppercase tracking-widest font-medium mb-1">
                    Recommended Model
                  </p>
                  <h1 className="text-3xl font-black text-slate-100 mb-2">
                    {rec.recommended_model}
                  </h1>
                  <div className="flex flex-wrap gap-2">
                    {rec.recommended_pipeline.map((step) => (
                      <span
                        key={step}
                        className="text-xs px-2.5 py-1 rounded-lg bg-slate-800 border border-slate-700 text-slate-400 font-mono"
                      >
                        {step}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Confidence ring */}
                <div className="text-center shrink-0">
                  <div className="relative w-20 h-20">
                    <svg viewBox="0 0 80 80" className="w-20 h-20 -rotate-90">
                      <circle cx="40" cy="40" r="32" fill="none" stroke="rgba(99,102,241,0.15)" strokeWidth="8" />
                      <circle
                        cx="40" cy="40" r="32" fill="none"
                        stroke="#6366f1" strokeWidth="8"
                        strokeLinecap="round"
                        strokeDasharray={`${2 * Math.PI * 32}`}
                        strokeDashoffset={`${2 * Math.PI * 32 * (1 - rec.confidence_score)}`}
                        style={{ transition: "stroke-dashoffset 1s ease" }}
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-lg font-black text-indigo-300">
                        {(rec.confidence_score * 100).toFixed(0)}%
                      </span>
                      <span className="text-[10px] text-slate-600">conf.</span>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* ── Metric cards ── */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
              <MetricCard
                label={rec.primary_metric_name}
                value={formatMetric(rec.primary_metric_value)}
                icon={<Trophy className="w-5 h-5" />}
                accent="amber"
              />
              <MetricCard
                label="Composite Score"
                value={formatMetric(rec.composite_score)}
                icon={<CheckCircle2 className="w-5 h-5" />}
                accent="indigo"
              />
              <MetricCard
                label="Total Experiments"
                value={report?.experiment_count ?? "—"}
                icon={<Lightbulb className="w-5 h-5" />}
                accent="violet"
              />
            </div>

            {/* ── Reasoning ── */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="mb-6"
            >
              <GlassCard>
                <p className="text-xs text-slate-500 uppercase tracking-wider font-medium mb-3 flex items-center gap-1.5">
                  <Brain className="w-3.5 h-3.5" />
                  AI Reasoning
                </p>
                <p className="text-sm text-slate-300 leading-relaxed">
                  {rec.reasoning}
                </p>
              </GlassCard>
            </motion.div>

            {/* ── Key Findings + Implementation Tips ── */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                <GlassCard>
                  <p className="text-xs text-slate-500 uppercase tracking-wider font-medium mb-3 flex items-center gap-1.5">
                    <Lightbulb className="w-3.5 h-3.5 text-amber-400" />
                    Key Findings
                  </p>
                  <ul className="space-y-2">
                    {rec.key_findings.map((f, i) => (
                      <li key={i} className="flex items-start gap-2.5">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                        <span className="text-xs text-slate-300 leading-relaxed">{f}</span>
                      </li>
                    ))}
                  </ul>
                </GlassCard>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                <GlassCard>
                  <p className="text-xs text-slate-500 uppercase tracking-wider font-medium mb-3 flex items-center gap-1.5">
                    <Wrench className="w-3.5 h-3.5 text-cyan-400" />
                    Implementation Tips
                  </p>
                  <ul className="space-y-2">
                    {rec.implementation_tips.map((tip, i) => (
                      <li key={i} className="flex items-start gap-2.5">
                        <span className="text-xs text-indigo-400 font-bold shrink-0 w-4">
                          {i + 1}.
                        </span>
                        <span className="text-xs text-slate-300 leading-relaxed">{tip}</span>
                      </li>
                    ))}
                  </ul>
                </GlassCard>
              </motion.div>
            </div>

            {/* ── Feature Importance ── */}
            {featureData.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="mb-8"
              >
                <GlassCard>
                  <p className="text-xs text-slate-500 uppercase tracking-wider font-medium mb-4">
                    Feature Importance — Winning Model
                  </p>
                  <HorizontalBarChart data={featureData} height={250} />
                </GlassCard>
              </motion.div>
            )}

            {/* ── Download actions ── */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="flex flex-wrap gap-3"
            >
              <Button
                variant="primary"
                icon={<Download className="w-4 h-4" />}
                onClick={() => handleDownload("html")}
              >
                Download HTML Report
              </Button>
              <Button
                variant="secondary"
                icon={<Download className="w-4 h-4" />}
                onClick={() => handleDownload("markdown")}
              >
                Download Markdown Report
              </Button>
              <Button
                variant="ghost"
                icon={<Lightbulb className="w-4 h-4" />}
                onClick={() => router.push(`/knowledge/${jobId}`)}
              >
                View Knowledge Base
              </Button>
            </motion.div>
          </>
        )}
      </div>
    </main>
  );
}
