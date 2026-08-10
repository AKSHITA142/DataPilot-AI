"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import {
  Brain,
  BarChart3,
  Zap,
  FileText,
  ArrowRight,
  GitFork,
  Activity,
  Database,
  FlaskConical,
} from "lucide-react";
import { Button } from "@/components/buttons/Button";

/* ─────────────────────────────────────────────
   Landing Page — DataPilot-AI Hero
   ───────────────────────────────────────────── */

const features = [
  {
    icon: <Database className="w-6 h-6" />,
    title: "Deep Dataset Profiling",
    desc: "Automatic semantic profiling, quality analysis, missing value detection, and distribution intelligence.",
    accent: "indigo",
  },
  {
    icon: <FlaskConical className="w-6 h-6" />,
    title: "Multi-Model Experimentation",
    desc: "Runs 10+ ML pipelines simultaneously, evaluating preprocessing + model combinations exhaustively.",
    accent: "violet",
  },
  {
    icon: <Activity className="w-6 h-6" />,
    title: "Live Research Progress",
    desc: "Watch the AI work in real time — GitHub-Actions-style pipeline view powered by WebSocket streams.",
    accent: "cyan",
  },
  {
    icon: <Brain className="w-6 h-6" />,
    title: "AI Knowledge Engine",
    desc: "LangGraph reasoning agents build a structured knowledge base across iterations, learning with each run.",
    accent: "emerald",
  },
];

const stats = [
  { label: "ML Models", value: "10+" },
  { label: "Pipeline Stages", value: "7" },
  { label: "Real-time Events", value: "WebSocket" },
  { label: "Report Formats", value: "HTML + MD" },
];

const accentIconColors: Record<string, string> = {
  indigo: "text-indigo-400 bg-indigo-500/10 border-indigo-500/20",
  violet: "text-violet-400 bg-violet-500/10 border-violet-500/20",
  cyan: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20",
  emerald: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
};

export default function LandingPage() {
  return (
    <main className="relative min-h-screen overflow-hidden">
      {/* ── Animated mesh background ── */}
      <div className="animated-gradient absolute inset-0 -z-10" />

      {/* ── Radial accent glows ── */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[900px] h-[600px] -z-10"
        style={{
          background:
            "radial-gradient(ellipse at center, rgba(99,102,241,0.15) 0%, transparent 70%)",
        }}
      />
      <div className="absolute bottom-0 right-0 w-[500px] h-[500px] -z-10"
        style={{
          background:
            "radial-gradient(ellipse at center, rgba(139,92,246,0.10) 0%, transparent 70%)",
        }}
      />

      {/* ── Navigation ── */}
      <nav className="relative z-10 flex items-center justify-between px-8 py-5 border-b border-slate-800/60 backdrop-blur-sm bg-slate-950/30">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
          className="flex items-center gap-2.5"
        >
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-lg tracking-tight text-slate-100">
            DataPilot<span className="text-indigo-400">-AI</span>
          </span>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
          className="flex items-center gap-3"
        >
          <a
            href="https://github.com/AKSHITA142/DataPilot-AI"
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800/60 transition-colors"
            aria-label="GitHub repository"
          >
            <GitFork className="w-5 h-5" />
          </a>
          <Link href="/upload">
            <Button size="sm" variant="primary">
              Launch App
            </Button>
          </Link>
        </motion.div>
      </nav>

      {/* ── Hero Section ── */}
      <section className="relative z-10 flex flex-col items-center text-center px-6 pt-24 pb-16">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.5 }}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/25 text-indigo-300 text-xs font-medium mb-8"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
          Autonomous AI Data Science Research Engine
        </motion.div>

        {/* Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="text-5xl sm:text-6xl md:text-7xl font-black leading-none tracking-tighter mb-6 max-w-4xl"
        >
          <span className="text-slate-100">Your AI</span>{" "}
          <span className="gradient-text">Data Scientist</span>
          <br />
          <span className="text-slate-300">Works Overnight.</span>
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35, duration: 0.6 }}
          className="text-slate-400 text-lg sm:text-xl max-w-2xl leading-relaxed mb-10"
        >
          Upload a CSV and a mission. DataPilot-AI autonomously profiles your
          dataset, runs multi-model ML experiments, builds a knowledge base of
          findings, and delivers a production-ready recommendation — all
          visible in real time.
        </motion.p>

        {/* CTAs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.5 }}
          className="flex flex-col sm:flex-row gap-3 items-center"
        >
          <Link href="/upload">
            <Button
              size="lg"
              variant="primary"
              icon={<Zap className="w-4 h-4" />}
              className="text-base px-8 py-3.5"
            >
              Start Research Now
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
          <a
            href="https://github.com/AKSHITA142/DataPilot-AI"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Button size="lg" variant="ghost" className="text-base">
              <GitFork className="w-4 h-4" />
              View on GitHub
            </Button>
          </a>
        </motion.div>

        {/* Stats row */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.65, duration: 0.5 }}
          className="flex flex-wrap justify-center gap-8 mt-16 pt-10 border-t border-slate-800/60 w-full max-w-2xl"
        >
          {stats.map((stat) => (
            <div key={stat.label} className="text-center">
              <p className="text-2xl font-bold text-indigo-300">{stat.value}</p>
              <p className="text-xs text-slate-500 mt-0.5 uppercase tracking-wider">
                {stat.label}
              </p>
            </div>
          ))}
        </motion.div>
      </section>

      {/* ── Feature Cards ── */}
      <section className="relative z-10 px-6 pb-24 max-w-6xl mx-auto">
        {/* Pipeline flow label */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
          className="flex items-center gap-3 mb-8"
        >
          <div className="flex-1 h-px bg-slate-800" />
          <span className="text-xs text-slate-500 uppercase tracking-widest font-medium px-3">
            What DataPilot-AI does for you
          </span>
          <div className="flex-1 h-px bg-slate-800" />
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 + i * 0.1, duration: 0.5 }}
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
              className="glass-card p-6 flex flex-col gap-4"
            >
              <div
                className={`w-11 h-11 rounded-xl flex items-center justify-center border ${accentIconColors[f.accent]}`}
              >
                {f.icon}
              </div>
              <div>
                <h3 className="font-semibold text-slate-100 text-sm mb-2">
                  {f.title}
                </h3>
                <p className="text-xs text-slate-500 leading-relaxed">{f.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Pipeline flow diagram */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2, duration: 0.6 }}
          className="mt-12 glass-card p-6"
        >
          <p className="text-xs text-slate-500 uppercase tracking-widest font-medium mb-5 text-center">
            Research Pipeline Flow
          </p>
          <div className="flex flex-wrap items-center justify-center gap-2">
            {[
              { icon: <Database className="w-3.5 h-3.5" />, label: "Upload" },
              { icon: <BarChart3 className="w-3.5 h-3.5" />, label: "Profile" },
              { icon: <Brain className="w-3.5 h-3.5" />, label: "Understand" },
              { icon: <FlaskConical className="w-3.5 h-3.5" />, label: "Experiment" },
              { icon: <Activity className="w-3.5 h-3.5" />, label: "Evaluate" },
              { icon: <FileText className="w-3.5 h-3.5" />, label: "Recommend" },
            ].map((step, i, arr) => (
              <div key={step.label} className="flex items-center gap-2">
                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/60 border border-slate-700/50 text-xs text-slate-300 font-medium">
                  <span className="text-indigo-400">{step.icon}</span>
                  {step.label}
                </div>
                {i < arr.length - 1 && (
                  <ArrowRight className="w-3.5 h-3.5 text-slate-600 shrink-0" />
                )}
              </div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* ── Footer ── */}
      <footer className="relative z-10 border-t border-slate-800/60 px-8 py-6 text-center">
        <p className="text-xs text-slate-600">
          DataPilot-AI — Built with FastAPI, LangGraph, Next.js &amp; ❤️
        </p>
      </footer>
    </main>
  );
}
