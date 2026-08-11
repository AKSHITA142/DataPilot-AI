"use client";

import { motion } from "framer-motion";
import { cn } from "@/utils/cn";
import type { ReactNode } from "react";

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  /** Reserve for genuinely important/selected cards only — not default state */
  emphasis?: boolean;
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
  emphasis = false,
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
              y: -2,
              borderColor: "var(--border)",
              boxShadow: "var(--shadow-md)",
            }
          : undefined
      }
      onClick={onClick}
      className={cn(
        "card depth-hover",
        paddingStyles[padding],
        emphasis && "ring-brand-emphasis",
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
        "rounded-lg border",
        "bg-surface-2 border-border-subtle",
        paddingStyles[padding],
        className
      )}
    >
      {children}
    </div>
  );
}
