"use client";

import { motion } from "framer-motion";
import { cn } from "@/utils/cn";
import type { ReactNode } from "react";

interface MetricCardProps {
  label: string;
  value: string | number;
  icon?: ReactNode;
  subtext?: string;
  trend?: "up" | "down" | "neutral";
  trendValue?: string;
  className?: string;
  /** Semantic, not decorative — pick the one that matches what the metric means */
  accent?: "brand" | "success" | "warning" | "error" | "neutral";
}

const accentMap = {
  brand: {
    icon: "text-brand-400",
    bg: "bg-brand-500/10",
    border: "border-brand-500/25",
    value: "text-text",
  },
  success: {
    icon: "text-success-400",
    bg: "bg-success-500/10",
    border: "border-success-500/25",
    value: "text-text",
  },
  warning: {
    icon: "text-warning-400",
    bg: "bg-warning-500/10",
    border: "border-warning-500/25",
    value: "text-text",
  },
  error: {
    icon: "text-error-400",
    bg: "bg-error-500/10",
    border: "border-error-500/25",
    value: "text-text",
  },
  neutral: {
    icon: "text-text-secondary",
    bg: "bg-surface-3",
    border: "border-border",
    value: "text-text",
  },
};

export function MetricCard({
  label,
  value,
  icon,
  subtext,
  trend,
  trendValue,
  className,
  accent = "neutral",
}: MetricCardProps) {
  const colors = accentMap[accent];

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      whileHover={{ y: -2, boxShadow: "var(--shadow-md)" }}
      className={cn("card p-5 flex items-start gap-4", className)}
    >
      {icon && (
        <div
          className={cn(
            "w-10 h-10 rounded-md flex items-center justify-center shrink-0 border",
            colors.bg,
            colors.border
          )}
        >
          <span className={cn("w-5 h-5", colors.icon)}>{icon}</span>
        </div>
      )}
      <div className="min-w-0 flex-1">
        <p className="text-xs text-text-secondary font-medium mb-1 uppercase tracking-wider">
          {label}
        </p>
        <p className={cn("text-2xl font-bold leading-none tabular-nums", colors.value)}>
          {value}
        </p>
        {subtext && (
          <p className="text-xs text-text-muted mt-1.5 truncate">{subtext}</p>
        )}
        {trend && trendValue && (
          <p
            className={cn(
              "text-xs font-medium mt-1.5",
              trend === "up" && "text-success-400",
              trend === "down" && "text-error-400",
              trend === "neutral" && "text-text-secondary"
            )}
          >
            {trend === "up" ? "↑" : trend === "down" ? "↓" : "→"} {trendValue}
          </p>
        )}
      </div>
    </motion.div>
  );
}
