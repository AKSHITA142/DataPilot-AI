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
  queued:    { cls: "status-queued",    dotColor: "bg-slate-400" },
  running:   { cls: "status-running",   dotColor: "bg-blue-400 animate-pulse" },
  completed: { cls: "status-completed", dotColor: "bg-emerald-400" },
  failed:    { cls: "status-failed",    dotColor: "bg-red-400" },
  cancelled: { cls: "status-cancelled", dotColor: "bg-amber-400" },
  info:      { cls: "status-running",   dotColor: "bg-blue-400" },
  neutral:   { cls: "status-queued",    dotColor: "bg-slate-400" },
  warning:   { cls: "status-cancelled", dotColor: "bg-amber-400" },
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
