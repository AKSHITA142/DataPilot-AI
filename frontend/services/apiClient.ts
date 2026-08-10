import type {
  Dataset,
  Job,
  StartJobResponse,
  UploadResponse,
  ExperimentResult,
  Report,
  DashboardData,
} from "@/types/api";

const BASE_URL = "/api/v1";

class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string
  ) {
    super(detail);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
    ...options,
  });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // ignore parse errors
    }
    throw new ApiError(res.status, detail);
  }

  return res.json() as Promise<T>;
}

// ── Dataset APIs ──────────────────────────────
export async function uploadDataset(
  file: File,
  mission: string
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("mission", mission);

  const res = await fetch(`${BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // ignore
    }
    throw new ApiError(res.status, detail);
  }

  return res.json();
}

export async function getDataset(datasetId: string): Promise<Dataset> {
  return request<Dataset>(`/datasets/${datasetId}`);
}

export async function listDatasets(): Promise<Dataset[]> {
  return request<Dataset[]>("/datasets");
}

// ── Job APIs ──────────────────────────────────
export async function startJob(
  datasetId: string,
  mission: string
): Promise<StartJobResponse> {
  return request<StartJobResponse>("/jobs/start", {
    method: "POST",
    body: JSON.stringify({ dataset_id: datasetId, mission }),
  });
}

export async function getJob(jobId: string): Promise<Job> {
  return request<Job>(`/jobs/${jobId}`);
}

export async function cancelJob(jobId: string): Promise<void> {
  await request(`/jobs/${jobId}/cancel`, { method: "POST" });
}

// ── Experiment APIs ───────────────────────────
export async function getExperiments(
  jobId: string
): Promise<ExperimentResult[]> {
  return request<ExperimentResult[]>(`/experiments/${jobId}`);
}

export async function getExperiment(
  experimentId: string
): Promise<ExperimentResult> {
  return request<ExperimentResult>(`/experiments/detail/${experimentId}`);
}

// ── Report APIs ───────────────────────────────
export async function getReport(jobId: string): Promise<Report> {
  return request<Report>(`/reports/${jobId}`);
}

export async function downloadReport(
  reportId: string,
  format: "html" | "markdown" = "markdown"
): Promise<Blob> {
  const res = await fetch(
    `${BASE_URL}/reports/${reportId}/download?format=${format}`
  );
  if (!res.ok) throw new ApiError(res.status, "Download failed");
  return res.blob();
}

// ── Dashboard APIs ────────────────────────────
export async function getDashboard(): Promise<DashboardData> {
  return request<DashboardData>("/dashboard");
}

export { ApiError };
