import type {
  ActivityListResponse,
  ApiErrorBody,
  FileUploadResponse,
  GenerateAIResponse,
} from "@/types/api";
import type {
  CopilotChatResponse,
  EnterpriseSearchResponse,
  MedRecMetrics,
  PlatformCapabilities,
  ProductivityMetrics,
  WorkflowStep,
} from "@/types/enterprise";
import type {
  CaseCreateRequest,
  CaseFinalizeRequest,
  CaseListFilter,
  ItemReviewPatchRequest,
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

export async function createMedRecCase(
  body: CaseCreateRequest
): Promise<MedReconciliationJob> {
  const response = await fetch(`${getBaseUrl()}/api/v1/meddocs/cases`, {
    method: "POST",
    headers: await buildHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw await parseError(response);
  }
  return (await response.json()) as MedReconciliationJob;
}

export async function listMedRecCases(
  status: CaseListFilter = "all"
): Promise<MedReconciliationJob[]> {
  const response = await fetch(
    `${getBaseUrl()}/api/v1/meddocs/cases?status=${encodeURIComponent(status)}`,
    { headers: await buildHeaders(), cache: "no-store" }
  );
  if (!response.ok) {
    throw await parseError(response);
  }
  return (await response.json()) as MedReconciliationJob[];
}

export async function fetchMedRecCase(jobId: string): Promise<MedReconciliationJob> {
  const response = await fetch(`${getBaseUrl()}/api/v1/meddocs/cases/${jobId}`, {
    headers: await buildHeaders(),
    cache: "no-store",
  });
  if (!response.ok) {
    throw await parseError(response);
  }
  return (await response.json()) as MedReconciliationJob;
}

export async function reconcileMedRecCase(
  caseId: string,
  files: File[]
): Promise<MedReconciliationJob> {
  const form = new FormData();
  for (const file of files) {
    form.append("files", file);
  }
  const response = await fetch(
    `${getBaseUrl()}/api/v1/meddocs/cases/${caseId}/reconcile`,
    {
      method: "POST",
      headers: await buildHeaders(),
      body: form,
    }
  );
  if (!response.ok) {
    throw await parseError(response);
  }
  return (await response.json()) as MedReconciliationJob;
}

export async function patchMedRecCaseItem(
  caseId: string,
  itemId: string,
  body: ItemReviewPatchRequest
): Promise<MedReconciliationJob> {
  const response = await fetch(
    `${getBaseUrl()}/api/v1/meddocs/cases/${caseId}/items/${itemId}`,
    {
      method: "PATCH",
      headers: await buildHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify(body),
    }
  );
  if (!response.ok) {
    throw await parseError(response);
  }
  return (await response.json()) as MedReconciliationJob;
}

export async function beginMedRecItemReview(
  caseId: string
): Promise<MedReconciliationJob> {
  const response = await fetch(
    `${getBaseUrl()}/api/v1/meddocs/cases/${caseId}/begin-item-review`,
    { method: "POST", headers: await buildHeaders() }
  );
  if (!response.ok) {
    throw await parseError(response);
  }
  return (await response.json()) as MedReconciliationJob;
}

export async function completeMedRecItemReview(
  caseId: string
): Promise<MedReconciliationJob> {
  const response = await fetch(
    `${getBaseUrl()}/api/v1/meddocs/cases/${caseId}/complete-item-review`,
    { method: "POST", headers: await buildHeaders() }
  );
  if (!response.ok) {
    throw await parseError(response);
  }
  return (await response.json()) as MedReconciliationJob;
}

export async function finalizeMedRecCaseReview(
  caseId: string,
  body: CaseFinalizeRequest
): Promise<MedReconciliationJob> {
  const response = await fetch(
    `${getBaseUrl()}/api/v1/meddocs/cases/${caseId}/finalize-review`,
    {
      method: "POST",
      headers: await buildHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify(body),
    }
  );
  if (!response.ok) {
    throw await parseError(response);
  }
  return (await response.json()) as MedReconciliationJob;
}

export function medRecReviewSummaryUrl(caseId: string): string {
  return `${getBaseUrl()}/api/v1/meddocs/cases/${caseId}/review-summary`;
}

export async function fetchMedRecReviewSummaryHtml(caseId: string): Promise<string> {
  const response = await fetch(medRecReviewSummaryUrl(caseId), {
    headers: await buildHeaders({ Accept: "text/html" }),
    cache: "no-store",
  });
  if (!response.ok) {
    throw await parseError(response);
  }
  return response.text();
}

export function openHtmlSummaryInNewTab(html: string): void {
  const blob = new Blob([html], { type: "text/html;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  window.open(url, "_blank", "noopener,noreferrer");
  window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
}

export async function fetchMedRecMetrics(): Promise<MedRecMetrics> {
  const response = await fetch(`${getBaseUrl()}/api/v1/analytics/medrec`, {
    headers: await buildHeaders(),
    cache: "no-store",
  });
  if (!response.ok) {
    throw await parseError(response);
  }
  const data = (await response.json()) as MedRecMetrics & { success?: boolean };
  return {
    cases_awaiting_review: data.cases_awaiting_review,
    cases_legacy_bulk_acknowledged: data.cases_legacy_bulk_acknowledged,
    cases_review_documented: data.cases_review_documented,
    open_items_total: data.open_items_total,
    items_awaiting_external_action: data.items_awaiting_external_action,
  };
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

export async function enterpriseSearch(query: string): Promise<EnterpriseSearchResponse> {
  const response = await fetch(
    `${getBaseUrl()}/api/v1/search?q=${encodeURIComponent(query)}`,
    { headers: await buildHeaders(), cache: "no-store" }
  );
  if (!response.ok) {
    throw await parseError(response);
  }
  return (await response.json()) as EnterpriseSearchResponse;
}

export async function copilotChat(
  message: string,
  sessionId?: string | null
): Promise<CopilotChatResponse> {
  const response = await fetch(`${getBaseUrl()}/api/v1/copilot/chat`, {
    method: "POST",
    headers: await buildHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ message, session_id: sessionId ?? null }),
  });
  if (!response.ok) {
    throw await parseError(response);
  }
  return (await response.json()) as CopilotChatResponse;
}

export async function analyzeMeeting(
  transcript: string,
  title?: string
): Promise<{ title: string; analysis_markdown: string }> {
  const response = await fetch(`${getBaseUrl()}/api/v1/meetings/intelligence`, {
    method: "POST",
    headers: await buildHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ transcript, title }),
  });
  if (!response.ok) {
    throw await parseError(response);
  }
  return (await response.json()) as { title: string; analysis_markdown: string };
}

export async function researchSynthesize(
  question: string
): Promise<{ answer_markdown: string; sources: EnterpriseSearchResponse["results"] }> {
  const response = await fetch(`${getBaseUrl()}/api/v1/research/synthesize`, {
    method: "POST",
    headers: await buildHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ question }),
  });
  if (!response.ok) {
    throw await parseError(response);
  }
  return (await response.json()) as {
    answer_markdown: string;
    sources: EnterpriseSearchResponse["results"];
  };
}

export async function fetchPlatformCapabilities(): Promise<PlatformCapabilities> {
  const response = await fetch(`${getBaseUrl()}/api/v1/platform/capabilities`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw await parseError(response);
  }
  const data = (await response.json()) as PlatformCapabilities & { success?: boolean };
  return { environment: data.environment, capabilities: data.capabilities };
}

export async function runWorkflowAgent(
  goal: string
): Promise<{ plan_markdown: string; tools_used: string[]; steps: WorkflowStep[] }> {
  const response = await fetch(`${getBaseUrl()}/api/v1/workflows/agent-run`, {
    method: "POST",
    headers: await buildHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ goal }),
  });
  if (!response.ok) {
    throw await parseError(response);
  }
  return (await response.json()) as {
    plan_markdown: string;
    tools_used: string[];
    steps: WorkflowStep[];
  };
}

export async function fetchProductivityMetrics(): Promise<ProductivityMetrics> {
  const response = await fetch(`${getBaseUrl()}/api/v1/analytics/productivity`, {
    headers: await buildHeaders(),
    cache: "no-store",
  });
  if (!response.ok) {
    throw await parseError(response);
  }
  const data = (await response.json()) as ProductivityMetrics & { success?: boolean };
  return { totals: data.totals, bigquery_configured: data.bigquery_configured, notes: data.notes };
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
