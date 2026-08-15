"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { BrainCircuit, CheckCircle2, ClipboardList, FlaskConical, GitBranch, PlayCircle, RotateCcw } from "lucide-react";

const stages = [
  { label: "Understand", detail: "Profile schema, quality, target, and semantic intent.", icon: BrainCircuit, tone: "brand" },
  { label: "Plan", detail: "Generate ranked hypotheses and experiment strategy.", icon: ClipboardList, tone: "info" },
  { label: "Execute", detail: "Build leakage-safe pipelines and train candidate models.", icon: PlayCircle, tone: "warning" },
  { label: "Evaluate", detail: "Score generalization, stability, efficiency, and constraints.", icon: FlaskConical, tone: "success" },
  { label: "Direct", detail: "Synthesize evidence and update research knowledge.", icon: CheckCircle2, tone: "brand" },
  { label: "Route", detail: "Loop if gain exceeds 0.5% and budget remains; otherwise report.", icon: GitBranch, tone: "info" },
] as const;

const narratives = [
  "Building a semantic profile from schema and quality signals.",
  "Turning evidence into a focused experiment strategy.",
  "Executing reproducible, leakage-safe model pipelines.",
  "Comparing candidates across more than one headline metric.",
  "Updating the research memory with what worked—and why.",
  "Routing back to planning or onward to the final report.",
];

export function WorkflowDiagram() {
  const reducedMotion = useReducedMotion();
  const [active, setActive] = useState(0);
  const iteration = Math.min(5, Math.floor(active / stages.length) + 2);

  useEffect(() => {
    if (reducedMotion) return;
    const timer = window.setInterval(() => setActive((current) => (current + 1) % stages.length), 1800);
    return () => window.clearInterval(timer);
  }, [reducedMotion]);

  return (
    <section id="workflow" className="scroll-mt-20 border-b border-border-subtle py-24 sm:py-32">
      <div className="mx-auto flex max-w-7xl flex-col gap-12 px-4 sm:px-6">
        <div className="flex max-w-3xl flex-col gap-4">
          <p className="font-mono text-xs uppercase tracking-[0.24em] text-brand-300">The autonomous loop</p>
          <h2 className="text-balance text-4xl font-semibold tracking-tight text-text sm:text-5xl">Research that knows what to try next.</h2>
          <p className="text-pretty text-lg leading-relaxed text-text-secondary">A cyclic LangGraph workflow keeps planning, execution, evaluation, direction, and routing connected—without hiding the decision that closes the loop.</p>
        </div>

        <div className="overflow-hidden rounded-xl border border-border bg-surface-1">
          <div className="flex flex-col gap-3 border-b border-border-subtle p-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
            <div className="flex items-center gap-2 font-mono text-xs text-text-secondary"><span className="size-2 rounded-full bg-success-400 animate-pulse-soft" /> LANGGRAPH / RUNNING</div>
            <div className="flex items-center gap-3"><span className="rounded-full border border-brand-500/30 bg-brand-500/10 px-3 py-1 font-mono text-xs text-brand-300">Iteration {iteration} of 5</span><span className="font-mono text-[11px] text-text-muted">gain &gt; 0.5% → loop</span></div>
          </div>

          <div className="relative p-5 sm:p-8 lg:p-12">
            <svg className="pointer-events-none absolute inset-0 hidden size-full lg:block" viewBox="0 0 1200 440" preserveAspectRatio="none" aria-hidden="true">
              <path d="M170 218 C240 85 380 75 470 175 C540 254 620 254 690 175 C780 75 920 85 1010 218 C920 350 780 360 690 262 C620 185 540 185 470 262 C380 360 240 350 170 218Z" fill="none" stroke="rgba(255,255,255,.10)" strokeWidth="2" strokeDasharray="7 9" />
              {!reducedMotion && <circle r="5" fill="#6bdbcd"><animateMotion dur="8s" repeatCount="indefinite" path="M170 218 C240 85 380 75 470 175 C540 254 620 254 690 175 C780 75 920 85 1010 218 C920 350 780 360 690 262 C620 185 540 185 470 262 C380 360 240 350 170 218Z" /></circle>}
            </svg>

            <div className="relative grid gap-4 md:grid-cols-2 lg:grid-cols-3 lg:gap-x-12 lg:gap-y-20">
              {stages.map((stage, index) => {
                const Icon = stage.icon;
                const isActive = active === index;
                return (
                  <button key={stage.label} type="button" onClick={() => setActive(index)} aria-pressed={isActive} className={`group flex min-h-32 flex-col items-start gap-4 rounded-lg border p-5 text-left transition-all ${isActive ? "border-brand-500/60 bg-brand-500/10 shadow-[0_0_30px_rgba(18,179,163,.08)]" : "border-border-subtle bg-surface-2/90 hover:border-border"}`}>
                    <div className="flex w-full items-center justify-between"><span className="flex size-9 items-center justify-center rounded-md border border-border bg-surface-3 text-brand-300"><Icon className="size-4" aria-hidden="true" /></span><span className="font-mono text-[10px] text-text-muted">0{index + 1}</span></div>
                    <div className="flex flex-col gap-1"><span className="font-semibold text-text">{stage.label}</span><span className="text-sm leading-relaxed text-text-muted">{stage.detail}</span></div>
                  </button>
                );
              })}
            </div>

            <div className="mt-8 flex flex-col gap-4 rounded-lg border border-border-subtle bg-bg/60 p-5 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-start gap-3"><RotateCcw className="mt-1 size-4 shrink-0 text-brand-300" aria-hidden="true" /><div className="flex flex-col gap-1"><span className="font-mono text-[10px] uppercase tracking-widest text-text-muted">Current decision</span><AnimatePresence mode="wait"><motion.p key={active} initial={reducedMotion ? false : { opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="text-sm text-text-secondary">{narratives[active]}</motion.p></AnimatePresence></div></div>
              <div className="flex gap-1.5" aria-label="Select workflow stage">{stages.map((stage, index) => <button key={stage.label} onClick={() => setActive(index)} className={`h-1.5 rounded-full transition-all ${active === index ? "w-8 bg-brand-400" : "w-3 bg-surface-4 hover:bg-text-muted"}`} aria-label={`Show ${stage.label} stage`} />)}</div>
            </div>
          </div>

          <div className="grid border-t border-border-subtle sm:grid-cols-3">
            {["SemanticProfile → state", "WebSocket telemetry → UI", "Report + artifacts → storage"].map((item) => <div key={item} className="border-b border-border-subtle px-5 py-4 font-mono text-[11px] text-text-muted last:border-b-0 sm:border-b-0 sm:border-r sm:last:border-r-0">{item}</div>)}
          </div>
        </div>
      </div>
    </section>
  );
}
