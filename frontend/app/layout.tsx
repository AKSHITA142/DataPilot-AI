import type { Metadata, Viewport } from "next";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: {
    default: "DataPilot-AI — Autonomous Data Science Research Engine",
    template: "%s | DataPilot-AI",
  },
  description:
    "DataPilot-AI autonomously profiles your dataset, runs multi-model experiments, and delivers a final recommendation — all in real time. Upload a CSV and watch your AI data scientist work.",
  keywords: [
    "data science",
    "machine learning",
    "AutoML",
    "AI research",
    "automated ML",
    "data analysis",
  ],
  authors: [{ name: "DataPilot-AI Team" }],
  openGraph: {
    title: "DataPilot-AI — Autonomous Data Science Research Engine",
    description:
      "Upload a CSV and let AI run your entire data science pipeline automatically.",
    type: "website",
  },
};

export const viewport: Viewport = {
  themeColor: "#020617",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
