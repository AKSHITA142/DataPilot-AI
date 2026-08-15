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
    default: "Evidra — Evidence-Driven AI for Data Science",
    template: "%s | Evidra",
  },
  description:
    "Evidra autonomously profiles your dataset, runs multi-model experiments, and delivers a final recommendation — all in real time. Upload a CSV and watch your AI data scientist work.",
  keywords: [
    "data science",
    "machine learning",
    "AutoML",
    "AI research",
    "automated ML",
    "data analysis",
  ],
  authors: [{ name: "Evidra Team" }],
  icons: {
    icon: "/icon.svg",
    shortcut: "/icon.svg",
    apple: "/icon.svg",
  },
  openGraph: {
    title: "Evidra — Evidence-Driven AI for Data Science",
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
    <html lang="en" data-scroll-behavior="smooth" className={`dark ${inter.variable} ${jetbrainsMono.variable}`}>
      <body className={`${inter.className} antialiased bg-bg text-text min-h-screen`}>
        <Providers>
          <ShellLayout>{children}</ShellLayout>
        </Providers>
      </body>
    </html>
  );
}

