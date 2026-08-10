"use client";

import { use } from "react";
import { motion } from "framer-motion";
import {
  Brain,
  CheckCircle2,
  Lightbulb,
  ChevronRight,
} from "lucide-react";
import Link from "next/link";
import { GlassCard } from "@/components/cards/GlassCard";
import { Skeleton } from "@/components/loading/Loading";
import { useReport } from "@/hooks/useResearch";
import { useRouter } from "next/navigation";
import { Button } from "@/components/buttons/Button";

export default function KnowledgePage({
  params,
}: {
  params: Promise<{ jobId: string }>;
}) {
  const { jobId } = use(params);
  const router = useRouter();
  const { data: report, isLoading } = useReport(jobId);

  const findings = report?.recommendation?.key_findings ?? [];

  return (
    <main className="min-h-screen bg-slate-950">
      <nav className="sticky top-0 z-30 flex items-center justify-between px-6 py-4 bg-slate-950/90 backdrop-blur-md border-b border-slate-800/60">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
            <Brain className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-sm tracking-tight">
            DataPilot<span className="text-indigo-400">-AI</span>
          </span>
        </Link>
        <Button
          variant="primary"
          size="sm"
          icon={<ChevronRight className="w-3.5 h-3.5" />}
          onClick={() => router.push(`/recommendation/${jobId}`)}
        >
          Final Report
        </Button>
      </nav>

      <div className="max-w-3xl mx-auto px-6 py-10">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-violet-500/10 border border-violet-500/25 text-violet-300 text-xs font-medium mb-4">
            <Lightbulb className="w-3.5 h-3.5" />
            Knowledge Base
          </div>
          <h1 className="text-2xl font-black text-slate-100">
            Research Knowledge Evolution
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Key findings and insights accumulated by the AI research engine
            across all experiments.
          </p>
        </motion.div>

        {isLoading ? (
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} className="h-20 w-full rounded-xl" />
            ))}
          </div>
        ) : findings.length === 0 ? (
          <GlassCard className="text-center py-12">
            <p className="text-slate-600 text-sm">
              No knowledge findings available yet. Run a research job first.
            </p>
          </GlassCard>
        ) : (
          <div className="space-y-3">
            {findings.map((finding, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.06, duration: 0.35 }}
                className="glass-card p-5 flex gap-4 items-start"
              >
                {/* Iteration badge */}
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-violet-500/15 border border-violet-500/25 flex items-center justify-center">
                  <span className="text-xs font-bold text-violet-400">
                    {i + 1}
                  </span>
                </div>

                <div className="flex-1 min-w-0">
                  <p className="text-sm text-slate-200 leading-relaxed">
                    {finding}
                  </p>
                </div>

                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
