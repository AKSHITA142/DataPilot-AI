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
// Coherent analytical palette anchored on the brand teal, not a rainbow.
// Use CHART_COLORS for neutral categorical series (e.g. pie/donut segments
// with no inherent severity meaning). For severity-coded data, use the
// semantic tokens directly (success/warning/error) instead of this array.
export const CHART_COLORS = [
  "#12b3a3", // brand-500
  "#6bdbcd", // brand-300
  "#0a6e65", // brand-700
  "#7c8ba1", // info / neutral steel
  "#f59e0b", // warning-500 (attention)
  "#a6a6a2", // text-secondary (other/neutral)
  "#33c7b6", // brand-400
  "#4ade80", // success-400 (only if a "healthy" segment applies)
];

const tooltipStyle = {
  backgroundColor: "var(--surface-3)",
  border: "1px solid var(--border)",
  borderRadius: "10px",
  color: "var(--text)",
  fontSize: "12px",
};

const axisTick = { fontSize: 11, fill: "#a6a6a2" };
const gridStroke = "rgba(255,255,255,0.05)";
const brandCursor = { fill: "rgba(18,179,163,0.08)" };

type TooltipValue = number | string | ReadonlyArray<number | string> | undefined;
type TooltipName = number | string | undefined;

function formatVal(v: TooltipValue): string {
  if (typeof v === "number") return v.toFixed(4);
  if (typeof v === "string") return v;
  if (Array.isArray(v)) return v.join(", ");
  return "";
}

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
  color = "#12b3a3",
  height = 240,
}: AppBarChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
        <XAxis
          dataKey="name"
          tick={axisTick}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          tick={axisTick}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          contentStyle={tooltipStyle}
          cursor={brandCursor}
          formatter={(v: TooltipValue) => [formatVal(v), label]}
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
        <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} horizontal={false} />
        <XAxis
          type="number"
          tick={axisTick}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          dataKey="name"
          type="category"
          tick={axisTick}
          axisLine={false}
          tickLine={false}
          width={100}
        />
        <Tooltip
          contentStyle={tooltipStyle}
          cursor={brandCursor}
          formatter={(v: TooltipValue) => [formatVal(v), label]}
        />
        <Bar dataKey="value" fill="#12b3a3" radius={[0, 4, 4, 0]} />
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
          formatter={(v: TooltipValue) => [formatVal(v), ""]}
        />
        <Legend
          iconType="circle"
          iconSize={8}
          formatter={(value: string) => (
            <span style={{ color: "#a6a6a2", fontSize: 11 }}>{value}</span>
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
        <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
        <XAxis
          type="number"
          dataKey="x"
          name={xLabel}
          tick={axisTick}
          axisLine={false}
          tickLine={false}
          label={{ value: xLabel, position: "insideBottom", offset: -4, fill: "#6e6e6b", fontSize: 11 }}
        />
        <YAxis
          type="number"
          dataKey="y"
          name={yLabel}
          tick={axisTick}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          contentStyle={tooltipStyle}
          cursor={{ strokeDasharray: "3 3", stroke: "rgba(18,179,163,0.4)" }}
          formatter={(v: TooltipValue, name: TooltipName) => [
            formatVal(v),
            name ?? "",
          ]}
        />
        <Scatter data={data} fill="#12b3a3" opacity={0.85} />
      </ScatterChart>
    </ResponsiveContainer>
  );
}
