/** Clinician-facing labels (never expose internal enum names in UI). */

export const CASE_STATUS_LABELS: Record<string, string> = {
  draft: "Not started",
  processing: "Analyzing documents",
  awaiting_review: "Ready for your review",
  legacy_bulk_acknowledged: "Imported list — review each item",
  review_documented: "Review complete",
  failed: "Processing failed",
};

export const ITEM_STATUS_LABELS: Record<string, string> = {
  open: "Needs review",
  pending_clarification: "Waiting for clarification",
  awaiting_external_action: "Action needed outside JIVANA",
  resolved_intentional: "Verified — intentional",
  resolved_externally_closed: "Resolved externally",
  resolved_not_relevant: "Not applicable",
  legacy_unreviewed: "Not yet reviewed individually",
};

export function labelCaseStatus(status: string): string {
  return CASE_STATUS_LABELS[status] ?? status.replace(/_/g, " ");
}

export function labelItemStatus(status: string): string {
  return ITEM_STATUS_LABELS[status] ?? status.replace(/_/g, " ");
}

const DETECTION_LABELS: Record<string, string> = {
  dose_mismatch: "Dose differs between sources",
  documented_change: "Change noted on discharge summary",
  omitted_med: "Medication missing from a list",
  added_med: "New medication on one list only",
  conflicting_strength: "Strength does not match",
  ambiguous_match: "Unclear if same medication",
};

export function labelDetectionType(type: string): string {
  return DETECTION_LABELS[type] ?? type.replace(/_/g, " ");
}

const TRANSITION_LABELS: Record<string, string> = {
  discharge: "Discharge",
  admission: "Admission",
  transfer: "Transfer",
};

export function labelTransitionType(type: string): string {
  return TRANSITION_LABELS[type] ?? type;
}
