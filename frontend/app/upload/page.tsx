"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload,
  FileSpreadsheet,
  X,
  CheckCircle2,
  AlertCircle,
  Sparkles,
} from "lucide-react";
import { Button } from "@/components/buttons/Button";
import { ProgressBar } from "@/components/loading/Loading";
import { uploadDataset, startJob } from "@/services/apiClient";
import { formatBytes } from "@/utils/formatters";

const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100 MB
const MISSION_MAX = 500;

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [mission, setMission] = useState("");
  const [status, setStatus] = useState<"idle" | "uploading" | "starting" | "error">("idle");
  const [errorMsg, setErrorMsg] = useState("");
  const [uploadProgress, setUploadProgress] = useState(0);

  const onDrop = useCallback((accepted: File[]) => {
    const f = accepted[0];
    if (!f) return;
    if (f.size > MAX_FILE_SIZE) {
      setErrorMsg("File size must be under 100 MB.");
      return;
    }
    setFile(f);
    setErrorMsg("");
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "text/csv": [".csv"] },
    maxFiles: 1,
    disabled: status === "uploading" || status === "starting",
  });

  const handleSubmit = async () => {
    if (!file || !mission.trim()) return;
    setStatus("uploading");
    setUploadProgress(0);
    setErrorMsg("");

    try {
      // Simulate progress during upload
      const progressInterval = setInterval(() => {
        setUploadProgress((p) => Math.min(p + 8, 85));
      }, 200);

      const uploadResult = await uploadDataset(file, mission.trim());
      clearInterval(progressInterval);
      setUploadProgress(90);

      setStatus("starting");
      const jobResult = await startJob(uploadResult.dataset_id, mission.trim());
      setUploadProgress(100);

      // Small delay for UX
      await new Promise((r) => setTimeout(r, 600));
      router.push(`/timeline/${jobResult.job_id}`);
    } catch (err) {
      setStatus("error");
      setErrorMsg(
        err instanceof Error ? err.message : "Upload failed. Please try again."
      );
      setUploadProgress(0);
    }
  };

  const isSubmittable =
    file !== null &&
    mission.trim().length >= 10 &&
    status === "idle";

  return (
    <div className="relative min-h-full">
      {/* Background radial highlight */}
      <div
        className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] pointer-events-none -z-0"
        style={{
          background:
            "radial-gradient(ellipse, rgba(18,179,163,0.08) 0%, transparent 70%)",
        }}
      />

      {/* Page content */}
      <div className="relative z-10 flex flex-col items-center px-4 sm:px-6 pt-8 pb-16 max-w-2xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-8"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-brand-500/10 border border-brand-500/25 text-brand-400 text-xs font-medium mb-4">
            <Sparkles className="w-3.5 h-3.5" />
            Start a New Research Run
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-text tracking-tight mb-2">
            Upload Your Dataset
          </h1>
          <p className="text-text-muted text-sm leading-relaxed max-w-md mx-auto">
            Upload a CSV file and describe your research goal. DataPilot-AI
            will autonomously run the entire data science pipeline.
          </p>
        </motion.div>

        {/* Drop Zone */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15, duration: 0.5 }}
          className="w-full mb-6"
        >
          <div
            {...getRootProps()}
            className={`
              relative w-full rounded-xl border-2 border-dashed p-8 sm:p-10 text-center
              cursor-pointer transition-all duration-200 select-none
              ${
                isDragActive
                  ? "border-brand-400 bg-brand-500/10 shadow-md"
                  : file
                  ? "border-success-500/50 bg-success-500/5"
                  : "border-border hover:border-brand-400/60 hover:bg-surface-3 bg-surface-2"
              }
            `}
          >
            <input {...getInputProps()} />

            <AnimatePresence mode="wait">
              {file ? (
                <motion.div
                  key="file-selected"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex flex-col items-center gap-3"
                >
                  <div className="w-12 h-12 rounded-xl bg-success-500/15 border border-success-500/30 flex items-center justify-center">
                    <FileSpreadsheet className="w-6 h-6 text-success-400" />
                  </div>
                  <div>
                    <p className="font-semibold text-success-400 text-sm">
                      {file.name}
                    </p>
                    <p className="text-xs text-text-muted mt-0.5 font-mono">
                      {formatBytes(file.size)} · CSV
                    </p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setFile(null);
                    }}
                    className="flex items-center gap-1.5 text-xs text-text-muted hover:text-error-400 transition-colors"
                  >
                    <X className="w-3.5 h-3.5" />
                    Remove file
                  </button>
                </motion.div>
              ) : (
                <motion.div
                  key="drop-prompt"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex flex-col items-center gap-3"
                >
                  <div
                    className={`w-12 h-12 rounded-xl flex items-center justify-center border transition-colors duration-200 ${
                      isDragActive
                        ? "bg-brand-500/20 border-brand-400/50"
                        : "bg-surface-3 border-border"
                    }`}
                  >
                    <Upload
                      className={`w-6 h-6 transition-colors ${
                        isDragActive ? "text-brand-400" : "text-text-muted"
                      }`}
                    />
                  </div>
                  <div>
                    <p className="text-text font-medium text-sm">
                      {isDragActive
                        ? "Drop your CSV here"
                        : "Drag & drop your CSV file"}
                    </p>
                    <p className="text-text-muted text-xs mt-1">
                      or click to browse · max 100 MB
                    </p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>

        {/* Mission input */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25, duration: 0.5 }}
          className="w-full mb-6"
        >
          <label className="block text-sm font-medium text-text mb-2">
            Research Mission / Goal{" "}
            <span className="text-brand-400">*</span>
          </label>
          <textarea
            value={mission}
            onChange={(e) => setMission(e.target.value.slice(0, MISSION_MAX))}
            placeholder="e.g., Predict customer churn with highest possible accuracy. Focus on recall for the positive class. Explain key factors driving churn."
            rows={4}
            disabled={status === "uploading" || status === "starting"}
            className="
              w-full px-4 py-3 rounded-lg text-sm
              bg-surface-2 border border-border
              text-text placeholder:text-text-muted
              focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500
              transition-all duration-200 resize-none
              disabled:opacity-50
            "
          />
          <div className="flex justify-between mt-1.5">
            <p className="text-xs text-text-muted">
              {mission.trim().length < 10 && mission.length > 0
                ? "At least 10 characters required"
                : "Be specific about your goal for best results"}
            </p>
            <p className="text-xs text-text-muted font-mono">
              {mission.length}/{MISSION_MAX}
            </p>
          </div>
        </motion.div>

        {/* Error message */}
        <AnimatePresence>
          {errorMsg && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="w-full mb-4 px-4 py-3 rounded-lg bg-error-500/10 border border-error-500/25 flex items-start gap-2.5"
            >
              <AlertCircle className="w-4 h-4 text-error-400 shrink-0 mt-0.5" />
              <p className="text-sm text-error-400">{errorMsg}</p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Progress during upload */}
        <AnimatePresence>
          {(status === "uploading" || status === "starting") && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="w-full mb-4"
            >
              <ProgressBar
                value={uploadProgress}
                label={
                  status === "starting"
                    ? "Starting research job…"
                    : "Uploading dataset…"
                }
                color="brand"
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Submit */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35, duration: 0.5 }}
          className="w-full"
        >
          <Button
            variant="primary"
            size="lg"
            className="w-full text-base"
            loading={status === "uploading" || status === "starting"}
            disabled={!isSubmittable}
            onClick={handleSubmit}
            icon={<CheckCircle2 className="w-4 h-4" />}
          >
            {status === "uploading"
              ? "Uploading Dataset…"
              : status === "starting"
              ? "Starting Research…"
              : "Launch Research Run"}
          </Button>
          {!file && (
            <p className="text-xs text-text-muted text-center mt-3">
              Upload a CSV file and enter your mission to get started
            </p>
          )}
        </motion.div>
      </div>
    </div>
  );
}
