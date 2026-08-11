"use client";

import { cn } from "@/utils/cn";
import type { JobStatus } from "@/types/api";

type BadgeVariant = JobStatus | "info" | "neutral" | "warning";

interface BadgeProps {
  variant?: BadgeVariant;
  label: string;
  dot?: boolean;
  className?: string;
}

const variantMap: Record<BadgeVariant, { cls: string; dotColor: string }> = {
  queued:    { cls: "status-queued",    dotColor: "bg-text-muted" },
  running:   { cls: "status-running",   dotColor: "bg-brand-400 animate-pulse-soft" },
  completed: { cls: "status-completed", dotColor: "bg-success-400" },
  failed:    { cls: "status-failed",    dotColor: "bg-error-400" },
  cancelled: { cls: "status-cancelled", dotColor: "bg-warning-400" },
  info:      { cls: "status-running",   dotColor: "bg-brand-400" },
  neutral:   { cls: "status-queued",    dotColor: "bg-text-muted" },
  warning:   { cls: "status-cancelled", dotColor: "bg-warning-400" },
};

export function Badge({ variant = "neutral", label, dot = true, className }: BadgeProps) {
  const { cls, dotColor } = variantMap[variant];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full",
        "text-xs font-medium",
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
