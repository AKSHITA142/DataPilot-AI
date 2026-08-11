"use client";

import type { ElementType, ReactNode } from "react";
import { cn } from "@/utils/cn";

interface EmptyStateProps {
  icon: ElementType;
  title: string;
  description: string;
  action?: ReactNode;
  className?: string;
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "card p-8 sm:p-12 text-center flex flex-col items-center justify-center gap-3 border border-border bg-surface-2",
        className
      )}
    >
      <div className="w-12 h-12 rounded-xl bg-surface-3 border border-border flex items-center justify-center mb-1 shrink-0">
        <Icon className="w-6 h-6 text-text-muted" />
      </div>
      <h3 className="text-base font-semibold text-text tracking-tight">{title}</h3>
      <p className="text-xs text-text-muted max-w-sm leading-relaxed">{description}</p>
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}
