"use client";

import { motion, useReducedMotion } from "framer-motion";
import { Blocks, Database, Layers, LineChart, RadioTower, ShieldCheck, Workflow } from "lucide-react";

const features = [
  { icon: Database, title: "Semantic data profiling", body: "Detects target type, quality issues, and column intent to build a SemanticProfile before any model runs." },
  { icon: Workflow, title: "Multi-agent orchestration", body: "A LangGraph pipeline coordinates understanding, planning, execution, evaluation, and direction as connected nodes." },
  { icon: Layers, title: "Strategy planning", body: "The planner proposes and ranks experiment hypotheses, then hands executable strategies to the ML runtime." },
  { icon: LineChart, title: "Multi-dimensional ranking", body: "Candidates are scored on generalization, stability, efficiency, and business fit—not a single leaderboard metric." },
  { icon: RadioTower, title: "Real-time telemetry", body: "WebSocket events stream job status, completed experiments, and knowledge updates straight to the workspace." },
  { icon: ShieldCheck, title: "Leakage-safe execution", body: "Identifier isolation and disciplined pipelines keep training honest and results trustworthy." },
  { icon: Blocks, title: "Reports & artifacts", body: "The director synthesizes findings into a shareable report with exported model artifacts and stored knowledge." },
];

const ranking = [
  { label: "Generalization", weight: "35%" },
  { label: "Stability", weight: "25%" },
  { label: "Efficiency", weight: "20%" },
  { label: "Business fit", weight: "20%" },
];

export function FeatureGrid() {
  const reducedMotion = useReducedMotion();
  return (
    <section id="capabilities" className="scroll-mt-20 border-b border-border-subtle py-24 sm:py-32">
      <div className="mx-auto flex max-w-7xl flex-col gap-12 px-4 sm:px-6">
        <div className="flex max-w-3xl flex-col gap-4">
          <p className="font-mono text-xs uppercase tracking-[0.24em] text-brand-300">Capabilities</p>
          <h2 className="text-balance text-4xl font-semibold tracking-tight text-text sm:text-5xl">Everything a diligent data scientist does—automated.</h2>
          <p className="text-pretty text-lg leading-relaxed text-text-secondary">Each capability maps to a real stage of the Evidra engine, from first profile to final report.</p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <motion.article key={feature.title} initial={reducedMotion ? false : { opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: (index % 3) * 0.06 }} className="flex flex-col gap-4 rounded-xl border border-border-subtle bg-surface-2/80 p-6 transition-colors hover:border-border">
                <span className="flex size-11 items-center justify-center rounded-lg border border-border bg-surface-3 text-brand-300"><Icon className="size-5" aria-hidden="true" /></span>
                <div className="flex flex-col gap-2"><h3 className="text-lg font-semibold text-text">{feature.title}</h3><p className="text-sm leading-relaxed text-text-muted">{feature.body}</p></div>
              </motion.article>
            );
          })}

          <motion.div initial={reducedMotion ? false : { opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="flex flex-col gap-5 rounded-xl border border-brand-500/25 bg-brand-500/[0.06] p-6">
            <div className="flex flex-col gap-1"><h3 className="text-lg font-semibold text-text">Ranking dimensions</h3><p className="text-sm text-text-muted">How the evaluation engine weighs each candidate.</p></div>
            <div className="flex flex-col gap-3">
              {ranking.map((dimension) => (
                <div key={dimension.label} className="flex flex-col gap-1.5">
                  <div className="flex items-center justify-between text-sm"><span className="text-text-secondary">{dimension.label}</span><span className="font-mono text-text">{dimension.weight}</span></div>
                  <div className="h-1.5 overflow-hidden rounded-full bg-surface-4"><div className="h-full rounded-full bg-brand-400" style={{ width: dimension.weight }} /></div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
