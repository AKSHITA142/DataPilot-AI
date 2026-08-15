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
    default: "Evindra — Autonomous ML Research",
    template: "%s | Evindra",
  },
  description:
    "Evindra autonomously profiles datasets, plans and runs ML experiments, evaluates evidence, and delivers research recommendations in real time.",
  keywords: ["machine learning", "AI research", "AutoML", "data science", "LangGraph"],
  authors: [{ name: "Evindra" }],
  openGraph: {
    title: "Evindra — Autonomous ML Research",
    description: "Your AI research team, running in a loop.",
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
    <html lang="en" data-scroll-behavior="smooth" className={`dark bg-bg ${inter.variable} ${jetbrainsMono.variable}`}>
      <body className={`${inter.className} antialiased bg-bg text-text min-h-screen`}>
        <Providers>
          <ShellLayout>{children}</ShellLayout>
        </Providers>
      </body>
    </html>
  );
}
