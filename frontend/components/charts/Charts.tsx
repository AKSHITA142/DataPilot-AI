"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
  Legend,
} from "recharts";

// ── Shared chart colours ──────────────────────
export const CHART_COLORS = [
  "#6366f1", // indigo-500
  "#8b5cf6", // violet-500
  "#22d3ee", // cyan-400
  "#10b981", // emerald-500
  "#f59e0b", // amber-500
  "#ef4444", // red-500
  "#3b82f6", // blue-500
  "#a78bfa", // violet-400
];

const tooltipStyle = {
  backgroundColor: "#1e293b",
  border: "1px solid rgba(148,163,184,0.15)",
  borderRadius: "10px",
  color: "#f1f5f9",
  fontSize: "12px",
};

// ── Vertical Bar Chart ────────────────────────
interface BarItem {
  name: string;
  value: number;
}

interface AppBarChartProps {
  data: BarItem[];
  label?: string;
  color?: string;
  height?: number;
}

export function AppBarChart({
  data,
  label = "Value",
  color = "#6366f1",
  height = 240,
}: AppBarChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.06)" />
        <XAxis
          dataKey="name"
          tick={{ fontSize: 11, fill: "#94a3b8" }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          tick={{ fontSize: 11, fill: "#94a3b8" }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          contentStyle={tooltipStyle}
          cursor={{ fill: "rgba(99,102,241,0.08)" }}
          formatter={(v: any) => [typeof v === 'number' ? v.toFixed(4) : v, label]}
        />
        <Bar dataKey="value" fill={color} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

// ── Horizontal Bar Chart (Feature Importance) ──
export function HorizontalBarChart({
  data,
  label = "Importance",
  height = 240,
}: AppBarChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart
        data={data}
        layout="vertical"
        margin={{ top: 4, right: 20, left: 4, bottom: 0 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.06)" horizontal={false} />
        <XAxis
          type="number"
          tick={{ fontSize: 11, fill: "#94a3b8" }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          dataKey="name"
          type="category"
          tick={{ fontSize: 11, fill: "#94a3b8" }}
          axisLine={false}
          tickLine={false}
          width={100}
        />
        <Tooltip
          contentStyle={tooltipStyle}
          cursor={{ fill: "rgba(99,102,241,0.08)" }}
          formatter={(v: any) => [typeof v === 'number' ? v.toFixed(4) : v, label]}
        />
        <Bar dataKey="value" fill="#6366f1" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

// ── Pie / Donut Chart ─────────────────────────
interface PieItem {
  name: string;
  value: number;
}

interface AppPieChartProps {
  data: PieItem[];
  height?: number;
  innerRadius?: number;
}

export function AppPieChart({
  data,
  height = 240,
  innerRadius = 60,
}: AppPieChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={innerRadius}
          outerRadius={innerRadius + 40}
          paddingAngle={3}
          dataKey="value"
        >
          {data.map((_, i) => (
            <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={tooltipStyle}
          formatter={(v: any) => [typeof v === 'number' ? v.toFixed(4) : v, '']}
        />
        <Legend
          iconType="circle"
          iconSize={8}
          formatter={(value: string) => (
            <span style={{ color: "#94a3b8", fontSize: 11 }}>{value}</span>
          )}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}

// ── Scatter Chart (Runtime vs Accuracy) ───────
interface ScatterItem {
  x: number;
  y: number;
  name: string;
}

interface AppScatterChartProps {
  data: ScatterItem[];
  xLabel?: string;
  yLabel?: string;
  height?: number;
}

export function AppScatterChart({
  data,
  xLabel = "Runtime (s)",
  yLabel = "Score",
  height = 260,
}: AppScatterChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <ScatterChart margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.06)" />
        <XAxis
          type="number"
          dataKey="x"
          name={xLabel}
          tick={{ fontSize: 11, fill: "#94a3b8" }}
          axisLine={false}
          tickLine={false}
          label={{ value: xLabel, position: "insideBottom", offset: -4, fill: "#475569", fontSize: 11 }}
        />
        <YAxis
          type="number"
          dataKey="y"
          name={yLabel}
          tick={{ fontSize: 11, fill: "#94a3b8" }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          contentStyle={tooltipStyle}
          cursor={{ strokeDasharray: "3 3", stroke: "rgba(99,102,241,0.4)" }}
          formatter={(v: any, name: any) => [typeof v === 'number' ? v.toFixed(4) : v, name]}
        />
        <Scatter data={data} fill="#6366f1" opacity={0.8} />
      </ScatterChart>
    </ResponsiveContainer>
  );
}
