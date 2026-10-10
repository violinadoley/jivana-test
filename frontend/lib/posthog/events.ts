import posthog from "posthog-js";

import {
  isPostHogEnabled,
  postHogEnvironment,
  type WorkflowType,
} from "@/lib/posthog/config";

type ProductEventName =
  | "workflow_started"
  | "input_submitted"
  | "ai_workflow_completed"
  | "ai_workflow_failed"
  | "recommendation_reviewed"
  | "action_approved"
  | "feedback_submitted";

type BaseProps = {
  workflow_type: WorkflowType;
  environment?: string;
};

function capture(
  event: ProductEventName,
  properties: Record<string, string | number | boolean | undefined> & BaseProps
): void {
  if (!isPostHogEnabled() || typeof window === "undefined") {
    return;
  }
  posthog.capture(event, {
    environment: postHogEnvironment(),
    ...properties,
  });
}

export function trackWorkflowStarted(workflowType: WorkflowType): void {
  capture("workflow_started", { workflow_type: workflowType });
}

export function trackInputSubmitted(
  workflowType: WorkflowType,
  props: {
    input_length_bucket?: string;
    file_extension?: string;
    size_bytes_bucket?: string;
  }
): void {
  capture("input_submitted", {
    workflow_type: workflowType,
    ...props,
  });
}

export function trackAiWorkflowCompleted(
  workflowType: WorkflowType,
  durationMs: number
): void {
  capture("ai_workflow_completed", {
    workflow_type: workflowType,
    duration_ms: durationMs,
  });
}

export function trackAiWorkflowFailed(
  workflowType: WorkflowType,
  durationMs: number,
  errorKind: string
): void {
  capture("ai_workflow_failed", {
    workflow_type: workflowType,
    duration_ms: durationMs,
    error_kind: errorKind.slice(0, 80),
  });
}

export function trackRecommendationReviewed(workflowType: WorkflowType): void {
  capture("recommendation_reviewed", { workflow_type: workflowType });
}

export function trackActionApproved(workflowType: WorkflowType): void {
  capture("action_approved", { workflow_type: workflowType });
}

export function trackFeedbackSubmitted(
  workflowType: WorkflowType,
  useful: boolean
): void {
  capture("feedback_submitted", {
    workflow_type: workflowType,
    useful,
  });
}

export function bucketInputLength(length: number): string {
  if (length <= 0) {
    return "empty";
  }
  if (length <= 50) {
    return "1-50";
  }
  if (length <= 200) {
    return "51-200";
  }
  if (length <= 1000) {
    return "201-1000";
  }
  return "1000+";
}

export function bucketFileSize(bytes: number): string {
  if (bytes < 10_000) {
    return "under_10kb";
  }
  if (bytes < 100_000) {
    return "10kb_100kb";
  }
  if (bytes < 1_000_000) {
    return "100kb_1mb";
  }
  return "over_1mb";
}

export function fileExtension(filename: string): string {
  const parts = filename.split(".");
  if (parts.length < 2) {
    return "unknown";
  }
  return parts.at(-1)?.toLowerCase() ?? "unknown";
}
