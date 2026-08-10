"use client";

import { motion } from "framer-motion";
import { cn } from "@/utils/cn";
import type { ReactNode } from "react";

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  glow?: boolean;
  padding?: "none" | "sm" | "md" | "lg";
  onClick?: () => void;
}

const paddingStyles = {
  none: "",
  sm: "p-3",
  md: "p-5",
  lg: "p-6",
};

export function GlassCard({
  children,
  className,
  hover = true,
  glow = false,
  padding = "md",
  onClick,
}: GlassCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      whileHover={
        hover
          ? {
              borderColor: "rgba(99,102,241,0.35)",
              boxShadow:
                "0 8px 40px rgba(0,0,0,0.6), 0 0 30px rgba(99,102,241,0.2)",
            }
          : undefined
      }
      onClick={onClick}
      className={cn(
        "glass-card",
        paddingStyles[padding],
        glow && "glow-primary",
        onClick && "cursor-pointer",
        className
      )}
    >
      {children}
    </motion.div>
  );
}

// Simple static card (no animation — for performance in long lists)
export function Card({
  children,
  className,
  padding = "md",
}: Pick<GlassCardProps, "children" | "className" | "padding">) {
  return (
    <div
      className={cn(
        "rounded-xl border",
        "bg-slate-900/60",
        "border-slate-700/50",
        paddingStyles[padding],
        className
      )}
    >
      {children}
    </div>
  );
}
