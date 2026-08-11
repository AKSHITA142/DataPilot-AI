"use client";

import { use } from "react";
import { motion } from "framer-motion";
import {
  CheckCircle2,
  Lightbulb,
  ChevronRight,
  BookOpen,
} from "lucide-react";
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
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-6 md:py-8">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-brand-500/10 border border-brand-500/25 text-brand-400 text-xs font-medium mb-3">
              <Lightbulb className="w-3.5 h-3.5" />
              Knowledge Base
            </div>
            <h1 className="text-xl font-bold text-text tracking-tight">
              Research Knowledge Evolution
            </h1>
            <p className="text-sm text-text-muted mt-1 leading-relaxed">
              Key findings and insights accumulated by the AI research engine
              across all experiments.
            </p>
          </div>
          <Button
            variant="primary"
            size="sm"
            icon={<ChevronRight className="w-3.5 h-3.5" />}
            onClick={() => router.push(`/recommendation/${jobId}`)}
            className="shrink-0"
          >
            Final Report
          </Button>
        </div>
      </motion.div>

      {isLoading ? (
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <Skeleton key={i} className="h-20 w-full rounded-xl" />
          ))}
        </div>
      ) : findings.length === 0 ? (
        <GlassCard className="text-center py-12 flex flex-col items-center gap-2">
          <BookOpen className="w-8 h-8 text-text-muted mb-1" />
          <p className="text-text-muted text-sm">
            No knowledge findings available yet. Wait for the research job to proceed.
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
              className="card p-5 flex gap-4 items-start"
            >
              {/* Iteration badge */}
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-brand-500/15 border border-brand-500/25 flex items-center justify-center">
                <span className="text-xs font-bold text-brand-400">
                  {i + 1}
                </span>
              </div>

              <div className="flex-1 min-w-0">
                <p className="text-sm text-text leading-relaxed">
                  {finding}
                </p>
              </div>

              <CheckCircle2 className="w-4 h-4 text-success-400 shrink-0 mt-0.5" />
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
