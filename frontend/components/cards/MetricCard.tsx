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
  accent?: "indigo" | "emerald" | "amber" | "cyan" | "violet";
}

const accentMap = {
  indigo: {
    icon: "text-indigo-400",
    bg: "bg-indigo-500/10",
    border: "border-indigo-500/20",
    value: "text-indigo-300",
  },
  emerald: {
    icon: "text-emerald-400",
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/20",
    value: "text-emerald-300",
  },
  amber: {
    icon: "text-amber-400",
    bg: "bg-amber-500/10",
    border: "border-amber-500/20",
    value: "text-amber-300",
  },
  cyan: {
    icon: "text-cyan-400",
    bg: "bg-cyan-500/10",
    border: "border-cyan-500/20",
    value: "text-cyan-300",
  },
  violet: {
    icon: "text-violet-400",
    bg: "bg-violet-500/10",
    border: "border-violet-500/20",
    value: "text-violet-300",
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
  accent = "indigo",
}: MetricCardProps) {
  const colors = accentMap[accent];

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      whileHover={{ y: -2, boxShadow: "0 12px 40px rgba(0,0,0,0.5)" }}
      className={cn(
        "glass-card p-5 flex items-start gap-4",
        className
      )}
    >
      {icon && (
        <div
          className={cn(
            "w-10 h-10 rounded-lg flex items-center justify-center shrink-0",
            colors.bg,
            `border ${colors.border}`
          )}
        >
          <span className={cn("w-5 h-5", colors.icon)}>{icon}</span>
        </div>
      )}
      <div className="min-w-0 flex-1">
        <p className="text-xs text-slate-400 font-medium mb-1 uppercase tracking-wider">
          {label}
        </p>
        <p className={cn("text-2xl font-bold leading-none", colors.value)}>
          {value}
        </p>
        {subtext && (
          <p className="text-xs text-slate-500 mt-1.5 truncate">{subtext}</p>
        )}
        {trend && trendValue && (
          <p
            className={cn(
              "text-xs font-medium mt-1.5",
              trend === "up" && "text-emerald-400",
              trend === "down" && "text-red-400",
              trend === "neutral" && "text-slate-400"
            )}
          >
            {trend === "up" ? "↑" : trend === "down" ? "↓" : "→"} {trendValue}
          </p>
        )}
      </div>
    </motion.div>
  );
}
