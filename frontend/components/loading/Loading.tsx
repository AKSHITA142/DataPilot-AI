"use client";

import { cn } from "@/utils/cn";

// ── Spinner ────────────────────────────────────
interface SpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
}

const spinnerSizes = { sm: "w-4 h-4", md: "w-6 h-6", lg: "w-10 h-10" };

export function Spinner({ size = "md", className }: SpinnerProps) {
  return (
    <svg
      className={cn("animate-spin text-indigo-400", spinnerSizes[size], className)}
      viewBox="0 0 24 24"
      fill="none"
    >
      <circle
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="3"
        strokeOpacity="0.2"
      />
      <path
        d="M12 2a10 10 0 0 1 10 10"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
      />
    </svg>
  );
}

// ── ProgressBar ────────────────────────────────
interface ProgressBarProps {
  value: number; // 0-100
  className?: string;
  label?: string;
  showPercent?: boolean;
  color?: "indigo" | "emerald" | "amber" | "cyan";
}

const progressColors = {
  indigo: "from-indigo-600 to-violet-500",
  emerald: "from-emerald-600 to-teal-400",
  amber: "from-amber-500 to-orange-400",
  cyan: "from-cyan-500 to-blue-400",
};

export function ProgressBar({
  value,
  className,
  label,
  showPercent = true,
  color = "indigo",
}: ProgressBarProps) {
  const clamped = Math.min(100, Math.max(0, value));
  return (
    <div className={cn("w-full", className)}>
      {(label || showPercent) && (
        <div className="flex justify-between mb-1.5">
          {label && (
            <span className="text-xs text-slate-400 font-medium">{label}</span>
          )}
          {showPercent && (
            <span className="text-xs text-indigo-400 font-semibold ml-auto">
              {clamped.toFixed(0)}%
            </span>
          )}
        </div>
      )}
      <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
        <div
          className={cn(
            "h-full rounded-full bg-gradient-to-r transition-all duration-700 ease-out",
            "shadow-[0_0_8px_rgba(99,102,241,0.6)]",
            progressColors[color]
          )}
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  );
}

// ── Skeleton placeholders ──────────────────────
interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className }: SkeletonProps) {
  return <div className={cn("skeleton", className)} />;
}

export function SkeletonCard() {
  return (
    <div className="glass-card p-5 space-y-3">
      <Skeleton className="h-4 w-1/3 rounded" />
      <Skeleton className="h-8 w-2/3 rounded" />
      <Skeleton className="h-3 w-full rounded" />
      <Skeleton className="h-3 w-4/5 rounded" />
    </div>
  );
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, i) => (
        <Skeleton key={i} className="h-12 w-full rounded-lg" />
      ))}
    </div>
  );
}
