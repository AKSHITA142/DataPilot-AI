import Link from "next/link";
import { ArrowRight, Code2, Database, GitBranch, Server, Workflow } from "lucide-react";
import { FeatureGrid } from "@/components/landing/FeatureGrid";
import { Hero, LandingNav } from "@/components/landing/Hero";
import { TelemetryPanel } from "@/components/landing/TelemetryPanel";
import { WorkflowDiagram } from "@/components/landing/WorkflowDiagram";

const stack = [
  { icon: GitBranch, label: "LangGraph", detail: "cyclic orchestration" },
  { icon: Server, label: "FastAPI", detail: "async API runtime" },
  { icon: Code2, label: "Next.js", detail: "research workspace" },
  { icon: Database, label: "PostgreSQL", detail: "durable state" },
  { icon: Workflow, label: "scikit-learn", detail: "ML execution" },
];

export default function LandingPage() {
  return (
    <main className="min-h-screen overflow-x-hidden bg-bg text-text">
      <LandingNav />
      <Hero />
      <WorkflowDiagram />
      <FeatureGrid />
      <TelemetryPanel />

      <section id="stack" className="scroll-mt-20 border-b border-border-subtle py-20">
        <div className="mx-auto flex max-w-7xl flex-col gap-8 px-4 sm:px-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <div className="flex max-w-2xl flex-col gap-3"><p className="font-mono text-xs uppercase tracking-[0.24em] text-brand-300">Built on proven tools</p><h2 className="text-3xl font-semibold tracking-tight text-text sm:text-4xl">Open architecture. Inspectable decisions.</h2></div>
            <p className="max-w-md text-sm leading-relaxed text-text-muted">A production-shaped stack designed for real experiments, durable state, and transparent orchestration.</p>
          </div>
          <div className="grid overflow-hidden rounded-xl border border-border-subtle sm:grid-cols-2 lg:grid-cols-5">
            {stack.map((item) => { const Icon = item.icon; return <div key={item.label} className="flex items-center gap-3 border-b border-border-subtle bg-surface-2/60 p-5 last:border-b-0 sm:border-r lg:border-b-0"><Icon className="size-5 shrink-0 text-brand-300" aria-hidden="true" /><div className="flex flex-col"><span className="font-semibold text-text">{item.label}</span><span className="font-mono text-[10px] text-text-muted">{item.detail}</span></div></div>; })}
          </div>
        </div>
      </section>

      <section className="py-24 sm:py-32">
        <div className="mx-auto max-w-5xl px-4 text-center sm:px-6">
          <div className="flex flex-col items-center gap-7 rounded-2xl border border-brand-500/25 bg-brand-500/[0.06] px-6 py-16 sm:px-12">
            <p className="font-mono text-xs uppercase tracking-[0.24em] text-brand-300">From CSV to recommendation</p>
            <h2 className="max-w-3xl text-balance text-4xl font-semibold tracking-tight text-text sm:text-6xl">Stop babysitting experiments. Start directing research.</h2>
            <p className="max-w-2xl text-pretty text-lg leading-relaxed text-text-secondary">Give Evindra a dataset and a mission. It will build the profile, run the loop, and return the evidence.</p>
            <Link href="/overview" className="inline-flex h-12 items-center justify-center gap-2 rounded-md bg-brand-500 px-6 font-semibold text-bg transition-colors hover:bg-brand-400">Open the workspace <ArrowRight className="size-4" aria-hidden="true" /></Link>
          </div>
        </div>
      </section>

      <footer className="border-t border-border-subtle py-8">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 text-sm text-text-muted sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <div className="flex items-center gap-2"><GitBranch className="size-4 text-brand-300" aria-hidden="true" /><span className="font-semibold text-text">Evindra</span><span>Autonomous ML research.</span></div>
          <div className="flex items-center gap-5"><a className="transition-colors hover:text-text" href="https://github.com/AKSHITA142/Evindra" target="_blank" rel="noreferrer">GitHub</a><span>MIT License</span></div>
        </div>
      </footer>
    </main>
  );
}
