"use client";

import { motion, AnimatePresence } from "framer-motion";
import {
  CheckCircle2,
  Circle,
  Loader2,
  XCircle,
  Clock,
} from "lucide-react";
import { cn } from "@/utils/cn";
import { Badge } from "@/components/badges/Badge";
import type { PipelineStage, JobStatus } from "@/types/api";

export interface TimelineStage {
  id: PipelineStage | string;
  label: string;
  description?: string;
  status: JobStatus | "waiting";
  duration?: string;
  startedAt?: string;
}

interface StageTimelineProps {
  stages: TimelineStage[];
  className?: string;
}

const StageIcon = ({ status }: { status: TimelineStage["status"] }) => {
  switch (status) {
    case "completed":
      return <CheckCircle2 className="w-5 h-5 text-emerald-400" />;
    case "running":
      return <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />;
    case "failed":
      return <XCircle className="w-5 h-5 text-red-400" />;
    case "waiting":
      return <Circle className="w-5 h-5 text-slate-600" />;
    default:
      return <Clock className="w-5 h-5 text-slate-500" />;
  }
};

const statusToJobStatus = (
  status: TimelineStage["status"]
): JobStatus | "neutral" => {
  if (status === "waiting") return "neutral";
  return status as JobStatus;
};

export function StageTimeline({ stages, className }: StageTimelineProps) {
  return (
    <div className={cn("relative", className)}>
      {/* Vertical connector line */}
      <div className="absolute left-5 top-5 bottom-5 w-px bg-slate-800" />

      <div className="space-y-0">
        {stages.map((stage, idx) => (
          <AnimatePresence key={stage.id} mode="wait">
            <motion.div
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.07, duration: 0.3 }}
              className={cn(
                "relative flex items-start gap-4 p-4 rounded-xl",
                "transition-colors duration-200",
                stage.status === "running" &&
                  "bg-blue-500/5 border border-blue-500/15",
                stage.status === "completed" &&
                  "bg-emerald-500/3 border border-transparent",
                stage.status === "failed" &&
                  "bg-red-500/5 border border-red-500/15",
                stage.status === "waiting" && "border border-transparent opacity-50"
              )}
            >
              {/* Icon with white bg circle */}
              <div className="relative z-10 flex-shrink-0 w-10 h-10 rounded-full bg-slate-900 border border-slate-700 flex items-center justify-center">
                <StageIcon status={stage.status} />
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0 pt-1">
                <div className="flex items-center gap-3 flex-wrap">
                  <span
                    className={cn(
                      "font-semibold text-sm",
                      stage.status === "completed" && "text-emerald-300",
                      stage.status === "running" && "text-blue-300",
                      stage.status === "failed" && "text-red-300",
                      stage.status === "waiting" && "text-slate-500",
                      stage.status === "queued" && "text-slate-400"
                    )}
                  >
                    {stage.label}
                  </span>
                  <Badge
                    variant={statusToJobStatus(stage.status)}
                    label={stage.status === "waiting" ? "Waiting" : stage.status}
                    dot={stage.status === "running"}
                  />
                  {stage.duration && (
                    <span className="text-xs text-slate-500 ml-auto">
                      {stage.duration}
                    </span>
                  )}
                </div>

                {stage.description && (
                  <p className="text-xs text-slate-500 mt-1">
                    {stage.description}
                  </p>
                )}

                {/* Running animation bar */}
                {stage.status === "running" && (
                  <motion.div
                    className="mt-2 h-0.5 bg-blue-500/30 rounded-full overflow-hidden"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                  >
                    <motion.div
                      className="h-full w-1/3 bg-blue-400 rounded-full"
                      animate={{ x: ["0%", "300%"] }}
                      transition={{
                        duration: 1.4,
                        repeat: Infinity,
                        ease: "easeInOut",
                      }}
                    />
                  </motion.div>
                )}
              </div>
            </motion.div>
          </AnimatePresence>
        ))}
      </div>
    </div>
  );
}
