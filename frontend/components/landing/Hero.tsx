"use client";

import Link from "next/link";
import Image from "next/image";
import { motion, useReducedMotion } from "framer-motion";
import { ArrowRight, Play, Sparkles } from "lucide-react";

const particles = Array.from({ length: 28 }, (_, index) => ({
  id: index,
  left: (index * 37) % 100,
  top: (index * 61) % 88,
  delay: (index % 8) * 0.35,
  duration: 5 + (index % 5),
}));

function AmbientParticles() {
  const reducedMotion = useReducedMotion();
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
      <div className="hero-grid absolute inset-0 opacity-60" />
      {particles.map((particle) => (
        <motion.span
          key={particle.id}
          className="absolute size-1 rounded-full bg-brand-300/60"
          style={{ left: `${particle.left}%`, top: `${particle.top}%` }}
          animate={reducedMotion ? undefined : { opacity: [0.12, 0.75, 0.12], y: [0, -18, 0] }}
          transition={{ duration: particle.duration, delay: particle.delay, repeat: Infinity, ease: "easeInOut" }}
        />
      ))}
      <div className="hero-vignette absolute inset-0" />
    </div>
  );
}

export function LandingNav() {
  return (
    <header className="fixed inset-x-0 top-0 z-40 border-b border-border-subtle bg-bg/80 backdrop-blur-xl">
      <nav className="mx-auto flex h-22 max-w-7xl items-center justify-between px-4 sm:px-6" aria-label="Primary navigation">
        <Link href="/" className="flex items-center">
          <Image
            src="/evidra-second-logo.png"
            alt="Evidra"
            width={947}
            height={380}
            priority
            className="h-14 sm:h-16 md:h-18 w-auto object-contain drop-shadow-sm"
          />
        </Link>
        <div className="hidden items-center gap-7 text-sm text-text-secondary md:flex">
          <a href="#workflow" className="transition-colors hover:text-text">Workflow</a>
          <a href="#capabilities" className="transition-colors hover:text-text">Capabilities</a>
          <a href="#stack" className="transition-colors hover:text-text">Stack</a>
        </div>
        <Link href="/overview" className="inline-flex h-11 items-center gap-2 rounded-md bg-text px-5 text-sm font-semibold text-bg transition-opacity hover:opacity-90">
          Open workspace <ArrowRight className="size-4" aria-hidden="true" />
        </Link>
      </nav>
    </header>
  );
}

export function Hero() {
  const reducedMotion = useReducedMotion();
  return (
    <section className="relative flex min-h-[820px] items-center overflow-hidden border-b border-border-subtle pt-24">
      <AmbientParticles />
      <div className="relative mx-auto grid w-full max-w-7xl items-center gap-16 px-4 py-24 sm:px-6 lg:grid-cols-[1.08fr_.92fr]">
        <motion.div initial={reducedMotion ? false : { opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }} className="flex flex-col items-start gap-7">
          <div className="inline-flex items-center gap-2 rounded-full border border-border bg-surface-2/70 px-3 py-1.5 font-mono text-xs text-text-secondary">
            <Sparkles className="size-3.5 text-brand-300" aria-hidden="true" />
            Evidence-Driven Autonomous AI Data Scientist
          </div>
          <div className="flex flex-col gap-5">
            <h1 className="max-w-4xl text-balance text-5xl font-semibold leading-[1.02] tracking-[-0.045em] text-text sm:text-6xl lg:text-7xl">
              Your Autonomous AI Data Scientist, Running on Evidence.
            </h1>
            <p className="max-w-2xl text-pretty text-lg leading-relaxed text-text-secondary sm:text-xl">
              Evidra autonomously profiles raw datasets, formulates hypotheses, executes multi-model ML pipelines with strict leakage prevention, and delivers auditable, production-ready recommendations.
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row">
            <Link href="/overview" className="inline-flex h-12 items-center justify-center gap-2 rounded-md bg-brand-500 px-6 font-semibold text-bg transition-colors hover:bg-brand-400">
              Start a research run <ArrowRight className="size-4" aria-hidden="true" />
            </Link>
            <a href="#workflow" className="inline-flex h-12 items-center justify-center gap-2 rounded-md border border-border bg-surface-2/60 px-6 font-semibold text-text transition-colors hover:bg-surface-3">
              <Play className="size-4" aria-hidden="true" /> See the workflow
            </a>
          </div>
          <div className="flex flex-wrap gap-x-6 gap-y-2 font-mono text-xs text-text-muted">
            <span>LangGraph orchestration</span><span>Real-time WebSockets</span><span>5-iteration research budget</span>
          </div>
        </motion.div>

        <motion.div initial={reducedMotion ? false : { opacity: 0, x: 24 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.8, delay: 0.15 }} className="relative mx-auto w-full max-w-xl">
          <div className="rounded-xl border border-border bg-surface-1/90 p-3 shadow-2xl shadow-black/30">
            <div className="flex items-center justify-between border-b border-border-subtle px-3 pb-3 font-mono text-[11px] text-text-muted">
              <span>research_run / live</span><span className="flex items-center gap-2 text-success-400"><span className="size-1.5 rounded-full bg-success-400 animate-pulse-soft" /> connected</span>
            </div>
            <div className="flex flex-col gap-3 p-3 font-mono text-xs sm:p-5 sm:text-sm">
              {[
                ["01", "UNDERSTAND", "Semantic profile ready", "text-brand-300"],
                ["02", "PLAN", "4 hypotheses queued", "text-info-400"],
                ["03", "EXECUTE", "XGBoost · fold 3/5", "text-warning-400"],
                ["04", "EVALUATE", "+1.8% normalized metric", "text-success-400"],
                ["05", "ROUTE", "iterate → planner", "text-brand-300"],
              ].map(([number, label, value, color]) => (
                <div key={number} className="grid grid-cols-[24px_92px_1fr] items-center gap-3 rounded-md border border-border-subtle bg-surface-2/70 px-3 py-3">
                  <span className="text-text-muted">{number}</span><span className={color}>{label}</span><span className="truncate text-right text-text-secondary">{value}</span>
                </div>
              ))}
              <div className="mt-1 h-1 overflow-hidden rounded-full bg-surface-4"><motion.div className="h-full bg-brand-400" initial={{ width: "20%" }} animate={reducedMotion ? undefined : { width: ["20%", "84%", "20%"] }} transition={{ duration: 7, repeat: Infinity, ease: "easeInOut" }} /></div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
