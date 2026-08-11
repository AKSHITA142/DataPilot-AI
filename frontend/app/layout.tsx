import type { Metadata, Viewport } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";
import { ShellLayout } from "@/components/shell/ShellLayout";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

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
  themeColor: "#0a0a0b",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`dark ${inter.variable} ${jetbrainsMono.variable}`}>
      <body className={`${inter.className} antialiased bg-bg text-text min-h-screen`}>
        <Providers>
          <ShellLayout>{children}</ShellLayout>
        </Providers>
      </body>
    </html>
  );
}
