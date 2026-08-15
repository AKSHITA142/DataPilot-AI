"use client";

import { useEffect, useState } from "react";
import { useReducedMotion } from "framer-motion";
import { ArrowUpRight, Layers3, ShieldAlert, Waypoints } from "lucide-react";

const events = [
  { event: "job.status_changed", value: "understanding → planning", tone: "text-brand-300" },
  { event: "experiment.completed", value: "GradientBoosting · auc 0.914", tone: "text-success-400" },
  { event: "knowledge.updated", value: "hypothesis promoted", tone: "text-info-400" },
  { event: "experiment.completed", value: "XGBoost · auc 0.928", tone: "text-success-400" },
  { event: "job.status_changed", value: "evaluating → directing", tone: "text-brand-300" },
  { event: "job.completed", value: "report + artifacts exported", tone: "text-warning-400" },
];

const fallbackOrder = ["OpenRouter", "OpenAI", "Gemini", "Rule-based"];

export function TelemetryPanel() {
  const reducedMotion = useReducedMotion();
  const [visible, setVisible] = useState(reducedMotion ? events.length : 1);

  useEffect(() => {
    if (reducedMotion) return;
    const timer = window.setInterval(() => setVisible((count) => (count >= events.length ? 1 : count + 1)), 1400);
    return () => window.clearInterval(timer);
  }, [reducedMotion]);

  return (
    <section className="border-b border-border-subtle py-24 sm:py-32">
      <div className="mx-auto grid max-w-7xl gap-10 px-4 sm:px-6 lg:grid-cols-2 lg:items-center">
        <div className="flex flex-col gap-5">
          <p className="font-mono text-xs uppercase tracking-[0.24em] text-brand-300">Live &amp; resilient</p>
          <h2 className="text-balance text-4xl font-semibold tracking-tight text-text sm:text-5xl">Watch the research happen—and trust it to keep going.</h2>
          <p className="text-pretty text-lg leading-relaxed text-text-secondary">Every stage streams to the UI over WebSockets, so you follow decisions as they are made. When a model provider fails, the engine automatically falls through a resilient chain instead of stopping.</p>
          <div className="flex flex-wrap items-center gap-2 font-mono text-xs">
            {fallbackOrder.map((provider, index) => (
              <span key={provider} className="flex items-center gap-2">
                <span className="rounded-md border border-border bg-surface-2 px-3 py-1.5 text-text-secondary">{provider}</span>
                {index < fallbackOrder.length - 1 && <ArrowUpRight className="size-3.5 rotate-45 text-text-muted" aria-hidden="true" />}
              </span>
            ))}
          </div>
          <div className="flex flex-col gap-3 pt-2 sm:flex-row">
            {[[Waypoints, "Streamed over WebSockets"], [Layers3, "Durable job + experiment state"], [ShieldAlert, "Graceful provider fallback"]].map(([Icon, label]) => {
              const IconComponent = Icon as typeof Waypoints;
              return <div key={label as string} className="flex items-center gap-2 rounded-md border border-border-subtle bg-surface-2/70 px-3 py-2 text-xs text-text-secondary"><IconComponent className="size-4 text-brand-300" aria-hidden="true" />{label as string}</div>;
            })}
          </div>
        </div>

        <div className="overflow-hidden rounded-xl border border-border bg-surface-1 font-mono text-sm">
          <div className="flex items-center justify-between border-b border-border-subtle px-4 py-3 text-[11px] text-text-muted"><span>ws://research/stream</span><span className="flex items-center gap-2 text-success-400"><span className="size-1.5 rounded-full bg-success-400 animate-pulse-soft" /> live</span></div>
          <div className="flex min-h-72 flex-col gap-2 p-4">
            {events.slice(0, visible).map((item, index) => (
              <div key={`${item.event}-${index}`} className="flex items-center justify-between gap-3 rounded-md border border-border-subtle bg-surface-2/70 px-3 py-2.5">
                <span className={`shrink-0 ${item.tone}`}>{item.event}</span>
                <span className="truncate text-right text-text-muted">{item.value}</span>
              </div>
            ))}
            {!reducedMotion && <div className="flex items-center gap-1 px-1 text-text-muted"><span className="dot-1 size-1.5 rounded-full bg-brand-400" /><span className="dot-2 size-1.5 rounded-full bg-brand-400" /><span className="dot-3 size-1.5 rounded-full bg-brand-400" /></div>}
          </div>
        </div>
      </div>
    </section>
  );
}
