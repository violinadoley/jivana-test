import type {
  ActivityListResponse,
  ApiErrorBody,
  FileUploadResponse,
  GenerateAIResponse,
} from "@/types/api";
import type {
  MedReconciliationJob,
  ReconciliationReviewRequest,
} from "@/types/meddocs";

const DEFAULT_API_URL = "http://localhost:8000";

function getBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? DEFAULT_API_URL;
}

let authTokenProvider: (() => Promise<string | null>) | null = null;

export function setAuthTokenProvider(
  provider: (() => Promise<string | null>) | null
): void {
  authTokenProvider = provider;
}

async function buildHeaders(
  extra?: HeadersInit
): Promise<HeadersInit> {
  const headers: Record<string, string> = {
    ...(extra as Record<string, string>),
  };
  if (authTokenProvider) {
    const token = await authTokenProvider();
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
  }
  return headers;
}

async function parseError(response: Response): Promise<Error> {
  try {
    const body = (await response.json()) as ApiErrorBody;
    if (body?.error?.message) {
      return new Error(body.error.message);
    }
  } catch {
    // ignore JSON parse errors
  }
  return new Error(`Request failed (${response.status})`);
}

export async function generateAI(message: string): Promise<string> {
  const response = await fetch(`${getBaseUrl()}/api/v1/ai/generate`, {
    method: "POST",
    headers: await buildHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    throw await parseError(response);
  }

  const data = (await response.json()) as GenerateAIResponse;
  return data.response;
}

export async function uploadFile(file: File): Promise<FileUploadResponse> {
  const form = new FormData();
  form.append("file", file);

  const response = await fetch(`${getBaseUrl()}/api/v1/files/upload`, {
    method: "POST",
    headers: await buildHeaders(),
    body: form,
  });

  if (!response.ok) {
    throw await parseError(response);
  }

  return (await response.json()) as FileUploadResponse;
}

export async function listActivity(limit = 20): Promise<ActivityListResponse["items"]> {
  const response = await fetch(
    `${getBaseUrl()}/api/v1/activity?limit=${limit}`,
    {
      headers: await buildHeaders(),
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw await parseError(response);
  }

  const data = (await response.json()) as ActivityListResponse;
  return data.items;
}

export async function createMedReconciliation(
  files: File[]
): Promise<MedReconciliationJob> {
  const form = new FormData();
  for (const file of files) {
    form.append("files", file);
  }
  const response = await fetch(`${getBaseUrl()}/api/v1/meddocs/reconciliation`, {
    method: "POST",
    headers: await buildHeaders(),
    body: form,
  });
  if (!response.ok) {
    throw await parseError(response);
  }
  return (await response.json()) as MedReconciliationJob;
}

export async function fetchMedReconciliation(
  jobId: string
): Promise<MedReconciliationJob> {
  const response = await fetch(
    `${getBaseUrl()}/api/v1/meddocs/reconciliation/${jobId}`,
    { headers: await buildHeaders(), cache: "no-store" }
  );
  if (!response.ok) {
    throw await parseError(response);
  }
  return (await response.json()) as MedReconciliationJob;
}

export async function fetchMedReviewQueue(): Promise<MedReconciliationJob[]> {
  const response = await fetch(`${getBaseUrl()}/api/v1/meddocs/review-queue`, {
    headers: await buildHeaders(),
    cache: "no-store",
  });
  if (!response.ok) {
    throw await parseError(response);
  }
  return (await response.json()) as MedReconciliationJob[];
}

export async function submitMedReconciliationReview(
  jobId: string,
  body: ReconciliationReviewRequest
): Promise<{ job_id: string; status: string; human_review: MedReconciliationJob["human_review"] }> {
  const response = await fetch(
    `${getBaseUrl()}/api/v1/meddocs/reconciliation/${jobId}/review`,
    {
      method: "POST",
      headers: await buildHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify(body),
    }
  );
  if (!response.ok) {
    throw await parseError(response);
  }
  return (await response.json()) as {
    job_id: string;
    status: string;
    human_review: MedReconciliationJob["human_review"];
  };
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${getBaseUrl()}/health`, {
      cache: "no-store",
    });
    return response.ok;
  } catch {
    return false;
  }
}
