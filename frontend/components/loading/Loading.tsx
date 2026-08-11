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
      className={cn("animate-spin text-brand-400", spinnerSizes[size], className)}
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
  color?: "brand" | "success" | "warning" | "error";
}

const progressColors: Record<NonNullable<ProgressBarProps["color"]>, string> = {
  brand: "bg-brand-500",
  success: "bg-success-500",
  warning: "bg-warning-500",
  error: "bg-error-500",
};

const progressTextColors: Record<NonNullable<ProgressBarProps["color"]>, string> = {
  brand: "text-brand-400",
  success: "text-success-400",
  warning: "text-warning-400",
  error: "text-error-400",
};

export function ProgressBar({
  value,
  className,
  label,
  showPercent = true,
  color = "brand",
}: ProgressBarProps) {
  const clamped = Math.min(100, Math.max(0, value));
  return (
    <div className={cn("w-full", className)}>
      {(label || showPercent) && (
        <div className="flex justify-between mb-1.5">
          {label && (
            <span className="text-xs text-text-secondary font-medium">{label}</span>
          )}
          {showPercent && (
            <span className={cn("text-xs font-semibold ml-auto", progressTextColors[color])}>
              {clamped.toFixed(0)}%
            </span>
          )}
        </div>
      )}
      <div className="w-full h-1.5 bg-surface-3 rounded-full overflow-hidden">
        <div
          className={cn(
            "h-full rounded-full transition-all duration-700 ease-out",
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
    <div className="card p-5 space-y-3">
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
