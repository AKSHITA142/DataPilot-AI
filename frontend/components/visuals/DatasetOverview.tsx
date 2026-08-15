"use client";

import React from "react";
import { Badge } from "@/components/badges/Badge";
import { GlassCard } from "@/components/cards/GlassCard";
import { FileText, Database, Target, AlertTriangle, Layers, BarChart2 } from "lucide-react";
import type { Dataset, ColumnProfile, QualityWarning } from "@/types/api";
import { formatBytes } from "@/utils/formatters";

interface DatasetOverviewProps {
  dataset: Dataset;
  className?: string;
}

interface ColumnData extends Omit<Partial<ColumnProfile>, "distinct_count"> {
  name: string;
  type?: string;
  dtype?: string;
  missing_pct?: number;
  missing_percent?: number;
  missing_count?: number;
  distinct_count?: number | string;
  unique_count?: number;
  sample_values?: (string | number | null)[];
  mean?: number;
  std?: number;
  min?: number;
  max?: number;
  skewness?: number | null;
  encoding_recommendation?: string;
  scaling_recommendation?: string;
}

interface QualityIssueItem extends Partial<QualityWarning> {
  problem?: string;
  warning_type?: string;
  severity?: "low" | "medium" | "high";
  message?: string;
  description?: string;
  affected_columns?: string[];
}

export function DatasetOverview({ dataset, className = "" }: DatasetOverviewProps) {
  const profile = (dataset.profile || {}) as Record<string, unknown>;
  const datasetSummary = (profile.dataset_summary || {}) as Record<string, unknown>;
  const columnProfiles: ColumnData[] = (profile.column_profiles || []) as ColumnData[];
  const qualityIssues: QualityIssueItem[] = (profile.quality_issues || profile.quality_warnings || []) as QualityIssueItem[];

  const targetInfo = (datasetSummary.target || {}) as Record<string, unknown>;
  const targetCol = String(targetInfo.target_column || profile.detected_target_column || "N/A");
  const taskType = String(targetInfo.task_type || profile.detected_task_type || "N/A");

  const rows = dataset.row_count || (datasetSummary.rows as number) || (profile.row_count as number) || 0;
  const cols = dataset.column_count || (datasetSummary.columns as number) || (profile.column_count as number) || 0;
  const fileSize = dataset.file_size_bytes || (datasetSummary.file_size_bytes as number) || (profile.file_size_bytes as number) || 0;

  return (
    <div className={`space-y-6 ${className}`}>
      {/* 1. Mission Brief Banner */}
      {dataset.mission_brief && (
        <GlassCard className="p-5 border-l-4 border-indigo-500 bg-gradient-to-r from-indigo-900/20 to-purple-900/10">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400">
              <Target className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-indigo-400 mb-1">
                Dataset Mission & Objective
              </h4>
              <p className="text-sm text-gray-200 font-medium">
                {dataset.mission_brief}
              </p>
            </div>
          </div>
        </GlassCard>
      )}

      {/* 2. Top Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <GlassCard className="p-4 flex items-center gap-3">
          <div className="p-3 rounded-lg bg-blue-500/10 text-blue-400">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs text-gray-400">Total Rows</div>
            <div className="text-lg font-bold text-gray-100">{rows.toLocaleString()}</div>
          </div>
        </GlassCard>

        <GlassCard className="p-4 flex items-center gap-3">
          <div className="p-3 rounded-lg bg-emerald-500/10 text-emerald-400">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs text-gray-400">Total Columns</div>
            <div className="text-lg font-bold text-gray-100">{cols.toLocaleString()}</div>
          </div>
        </GlassCard>

        <GlassCard className="p-4 flex items-center gap-3">
          <div className="p-3 rounded-lg bg-purple-500/10 text-purple-400">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs text-gray-400">File Size</div>
            <div className="text-lg font-bold text-gray-100">{formatBytes(fileSize)}</div>
          </div>
        </GlassCard>

        <GlassCard className="p-4 flex items-center gap-3 border-l-4 border-indigo-500">
          <div className="p-3 rounded-lg bg-amber-500/10 text-amber-400 shrink-0">
            <BarChart2 className="w-5 h-5" />
          </div>
          <div className="overflow-hidden">
            <div className="text-xs text-gray-400 flex items-center gap-1.5">
              <span>Target & Task</span>
              <span className="px-1.5 py-0.2 text-[9px] font-mono bg-indigo-500/20 text-indigo-300 rounded border border-indigo-500/30">
                AUTO-DETECTED
              </span>
            </div>
            <div className="text-sm font-semibold text-gray-100 truncate flex items-center gap-1.5 mt-0.5">
              <span className="text-indigo-400 font-mono">{targetCol}</span>
              <span className="text-xs text-gray-400 font-normal">({taskType})</span>
            </div>
          </div>
        </GlassCard>
      </div>

      {/* 3. Detailed Column Profiles Table */}
      <GlassCard className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-semibold text-gray-100 flex items-center gap-2">
            <Database className="w-4 h-4 text-indigo-400" />
            Column Schema & Statistical Profiles ({columnProfiles.length})
          </h3>
        </div>

        {columnProfiles.length === 0 ? (
          <div className="text-center py-8 text-gray-400 text-sm">
            No column profiles available for this dataset.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-gray-800 text-gray-400 uppercase tracking-wider font-semibold">
                  <th className="py-3 px-3">Column Name</th>
                  <th className="py-3 px-3">Type</th>
                  <th className="py-3 px-3">Missing</th>
                  <th className="py-3 px-3">Unique</th>
                  <th className="py-3 px-3">Distribution Stats</th>
                  <th className="py-3 px-3">Recommendations</th>
                  <th className="py-3 px-3">Sample Values</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/50 text-gray-300">
                {columnProfiles.map((col: ColumnData) => {
                  const missingPct = col.missing_pct ?? col.missing_percent ?? 0;
                  const missingCount = col.missing_count ?? 0;
                  const distinctCount = col.distinct_count ?? col.unique_count ?? "N/A";
                  const colType = col.type || col.dtype || "unknown";

                  return (
                    <tr key={col.name} className="hover:bg-gray-800/30 transition-colors">
                      <td className="py-3 px-3 font-medium text-gray-200">
                        {col.name}
                        {col.name === targetCol && (
                          <span className="ml-2 px-1.5 py-0.5 text-[10px] bg-indigo-500/20 text-indigo-300 rounded border border-indigo-500/30 font-mono">
                            TARGET
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-3">
                        <Badge
                          label={String(colType).replace("_", " ")}
                          variant={String(colType).includes("high") ? "warning" : String(colType) === "numeric" ? "info" : "neutral"}
                        />
                      </td>
                      <td className="py-3 px-3">
                        <span className={missingPct > 0 ? "text-amber-400 font-semibold" : "text-gray-400"}>
                          {missingCount} ({missingPct}%)
                        </span>
                      </td>
                      <td className="py-3 px-3 font-mono text-gray-300">
                        {typeof distinctCount === "number" ? distinctCount.toLocaleString() : distinctCount}
                      </td>
                      <td className="py-3 px-3 text-gray-400 font-mono">
                        {col.mean !== undefined && col.mean !== null ? (
                          <div>
                            <div>mean: {col.mean} | std: {col.std}</div>
                            <div>min: {col.min} | max: {col.max}</div>
                            {col.skewness !== null && col.skewness !== undefined && (
                              <div className="text-gray-500 text-[10px]">skew: {col.skewness}</div>
                            )}
                          </div>
                        ) : (
                          <span className="text-gray-600">—</span>
                        )}
                      </td>
                      <td className="py-3 px-3">
                        <div className="flex flex-col gap-1">
                          {col.encoding_recommendation && (
                            <span className="text-[10px] px-1.5 py-0.5 bg-purple-500/10 text-purple-300 border border-purple-500/20 rounded">
                              Enc: {col.encoding_recommendation}
                            </span>
                          )}
                          {col.scaling_recommendation && (
                            <span className="text-[10px] px-1.5 py-0.5 bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 rounded">
                              Scale: {col.scaling_recommendation}
                            </span>
                          )}
                          {!col.encoding_recommendation && !col.scaling_recommendation && (
                            <span className="text-gray-600 text-[10px]">—</span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-3 max-w-[200px] truncate text-gray-400 font-mono">
                        {col.sample_values && col.sample_values.length > 0
                          ? col.sample_values.join(", ")
                          : "N/A"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </GlassCard>

      {/* 4. Quality Issues & Warnings */}
      {qualityIssues.length > 0 && (
        <GlassCard className="p-6 border-l-4 border-amber-500">
          <h3 className="text-base font-semibold text-amber-400 flex items-center gap-2 mb-3">
            <AlertTriangle className="w-5 h-5" />
            Detected Data Quality Issues ({qualityIssues.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {qualityIssues.map((issue: QualityIssueItem, idx: number) => (
              <div key={idx} className="p-3 bg-gray-900/60 rounded-lg border border-amber-500/20 text-xs">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-semibold text-gray-200">
                    {issue.problem || issue.warning_type || "Quality Issue"}
                  </span>
                  <Badge
                    label={issue.severity || "medium"}
                    variant={issue.severity === "high" ? "cancelled" : "warning"}
                  />
                </div>
                <p className="text-gray-400 mb-1">{issue.description || issue.message}</p>
                {issue.affected_columns && issue.affected_columns.length > 0 && (
                  <div className="text-[10px] text-amber-400/80">
                    Columns: {issue.affected_columns.join(", ")}
                  </div>
                )}
              </div>
            ))}
          </div>
        </GlassCard>
      )}
    </div>
  );
}
