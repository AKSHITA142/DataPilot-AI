"use client";

import { motion } from "framer-motion";
import { cn } from "@/utils/cn";
import type { ReactNode } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger" | "success";
type Size = "sm" | "md" | "lg";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
  icon?: ReactNode;
  children: ReactNode;
}

const variantStyles: Record<Variant, string> = {
  primary:
    "bg-brand-500 hover:bg-brand-400 text-[#052620] font-semibold border border-brand-400/60 shadow-sm",
  secondary:
    "bg-surface-3 hover:bg-surface-4 text-text border border-border",
  ghost:
    "bg-transparent hover:bg-surface-3 text-text-secondary border border-border-subtle",
  danger:
    "bg-error-500/12 hover:bg-error-500/20 text-error-400 border border-error-500/30",
  success:
    "bg-success-500/12 hover:bg-success-500/20 text-success-400 border border-success-500/30",
};

const sizeStyles: Record<Size, string> = {
  sm: "px-3 py-1.5 text-xs gap-1.5",
  md: "px-4 py-2 text-sm gap-2",
  lg: "px-6 py-3 text-base gap-2.5",
};

export function Button({
  variant = "primary",
  size = "md",
  loading = false,
  icon,
  className,
  disabled,
  children,
  ...props
}: ButtonProps) {
  return (
    <motion.button
      whileHover={{ scale: 1.015 }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: "spring", stiffness: 420, damping: 24 }}
      className={cn(
        "inline-flex items-center justify-center rounded-md font-medium",
        "transition-colors duration-150 cursor-pointer select-none",
        "disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none",
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
      disabled={disabled || loading}
      {...(props as React.ComponentProps<typeof motion.button>)}
    >
      {loading ? (
        <span className="flex items-center gap-2">
          <svg
            className="w-4 h-4 animate-spin"
            viewBox="0 0 24 24"
            fill="none"
          >
            <circle
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="3"
              strokeOpacity="0.25"
            />
            <path
              d="M12 2a10 10 0 0 1 10 10"
              stroke="currentColor"
              strokeWidth="3"
              strokeLinecap="round"
            />
          </svg>
          {children}
        </span>
      ) : (
        <>
          {icon && <span className="shrink-0">{icon}</span>}
          {children}
        </>
      )}
    </motion.button>
  );
}
