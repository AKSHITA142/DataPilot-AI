"use client";

import { cn } from "@/utils/cn";
import type { JobStatus, PipelineStage } from "@/types/api";

type BadgeVariant = JobStatus | PipelineStage | "info" | "neutral" | "warning" | string;

interface BadgeProps {
  variant?: BadgeVariant;
  label: string;
  dot?: boolean;
  className?: string;
}

const variantMap: Record<string, { cls: string; dotColor: string }> = {
  queued:        { cls: "status-queued",    dotColor: "bg-text-muted" },
  running:       { cls: "status-running",   dotColor: "bg-brand-400 animate-pulse-soft" },
  completed:     { cls: "status-completed", dotColor: "bg-success-400" },
  failed:        { cls: "status-failed",    dotColor: "bg-error-400" },
  cancelled:     { cls: "status-cancelled", dotColor: "bg-warning-400" },
  // Pipeline stage variants
  profiling:     { cls: "status-running",   dotColor: "bg-brand-400 animate-pulse-soft" },
  understanding: { cls: "status-running",   dotColor: "bg-brand-400 animate-pulse-soft" },
  planning:      { cls: "status-running",   dotColor: "bg-brand-400 animate-pulse-soft" },
  executing:     { cls: "status-running",   dotColor: "bg-brand-400 animate-pulse-soft" },
  evaluating:    { cls: "status-running",   dotColor: "bg-brand-400 animate-pulse-soft" },
  decision:      { cls: "status-running",   dotColor: "bg-brand-400 animate-pulse-soft" },
  reporting:     { cls: "status-running",   dotColor: "bg-brand-400 animate-pulse-soft" },
  // Helper variants
  info:          { cls: "status-running",   dotColor: "bg-brand-400" },
  neutral:       { cls: "status-queued",    dotColor: "bg-text-muted" },
  warning:       { cls: "status-cancelled", dotColor: "bg-warning-400" },
};

export function Badge({ variant = "neutral", label, dot = true, className }: BadgeProps) {
  const config = (variant && variantMap[variant]) ? variantMap[variant] : variantMap.neutral;
  const { cls, dotColor } = config;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full",
        "text-xs font-medium uppercase tracking-wider",
        cls,
        className
      )}
    >
      {dot && (
        <span className={cn("w-1.5 h-1.5 rounded-full shrink-0", dotColor)} />
      )}
      {label}
    </span>
  );
}

