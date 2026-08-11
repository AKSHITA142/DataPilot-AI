"use client";

import { AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "@/components/buttons/Button";
import { cn } from "@/utils/cn";
import type { ReactNode } from "react";

interface ErrorStateProps {
  title?: string;
  description: string;
  onRetry?: () => void;
  action?: ReactNode;
  className?: string;
}

export function ErrorState({
  title = "Failed to load data",
  description,
  onRetry,
  action,
  className,
}: ErrorStateProps) {
  return (
    <div
      className={cn(
        "card p-5 sm:p-6 border-l-4 border-l-error-500 bg-surface-2 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-border",
        className
      )}
    >
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-lg bg-error-500/10 border border-error-500/25 flex items-center justify-center shrink-0">
          <AlertTriangle className="w-5 h-5 text-error-400" />
        </div>
        <div>
          <h4 className="text-sm font-semibold text-text">{title}</h4>
          <p className="text-xs text-text-muted mt-0.5 leading-relaxed max-w-md">{description}</p>
        </div>
      </div>

      <div className="flex items-center gap-2 shrink-0 self-end sm:self-auto">
        {onRetry && (
          <Button
            variant="secondary"
            size="sm"
            icon={<RefreshCw className="w-3.5 h-3.5" />}
            onClick={onRetry}
          >
            Retry
          </Button>
        )}
        {action}
      </div>
    </div>
  );
}
