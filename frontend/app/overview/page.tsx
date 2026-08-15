import Link from "next/link";
import { ArrowLeft, ArrowRight, Database, Upload } from "lucide-react";

export default function OverviewBridgePage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-bg px-4 py-20 text-text">
      <div className="flex w-full max-w-3xl flex-col gap-8 rounded-xl border border-border bg-surface-1 p-6 sm:p-10">
        <Link href="/" className="inline-flex w-fit items-center gap-2 text-sm text-text-muted transition-colors hover:text-text"><ArrowLeft className="size-4" aria-hidden="true" /> Back to Evindra</Link>
        <div className="flex flex-col gap-4"><span className="flex size-11 items-center justify-center rounded-lg border border-brand-500/30 bg-brand-500/10 text-brand-300"><Database className="size-5" aria-hidden="true" /></span><h1 className="text-balance text-4xl font-semibold tracking-tight sm:text-5xl">Start with a dataset.</h1><p className="max-w-2xl text-pretty text-lg leading-relaxed text-text-secondary">Upload a CSV, define the research mission, and Evindra will create the semantic profile before launching the autonomous experiment loop.</p></div>
        <div className="flex flex-col gap-3 sm:flex-row"><Link href="/upload" className="inline-flex h-12 items-center justify-center gap-2 rounded-md bg-brand-500 px-6 font-semibold text-bg transition-colors hover:bg-brand-400"><Upload className="size-4" aria-hidden="true" /> Upload dataset</Link><Link href="/datasets" className="inline-flex h-12 items-center justify-center gap-2 rounded-md border border-border bg-surface-2 px-6 font-semibold text-text transition-colors hover:bg-surface-3">View datasets <ArrowRight className="size-4" aria-hidden="true" /></Link></div>
      </div>
    </main>
  );
}
