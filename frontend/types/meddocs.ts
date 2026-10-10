export type MeddocsJobStatus =
  | "processing"
  | "completed"
  | "needs_review"
  | "failed";

export type CaseStatus =
  | "draft"
  | "processing"
  | "awaiting_review"
  | "legacy_bulk_acknowledged"
  | "review_documented"
  | "failed";

export type CaseListFilter =
  | "all"
  | "draft"
  | "awaiting_review"
  | "legacy_bulk_acknowledged"
  | "review_documented"
  | "failed";

export type DiscrepancyItemStatus =
  | "open"
  | "pending_clarification"
  | "awaiting_external_action"
  | "resolved_intentional"
  | "resolved_externally_closed"
  | "resolved_not_relevant"
  | "legacy_unreviewed";

export type EvidenceStatus = "verified" | "low" | "vertex_only";

export type SourceRef = {
  document_id: string;
  page_number?: number | null;
  source_text?: string | null;
  text_anchor?: string | null;
  extraction_method: string;
  confidence?: number | null;
  evidence_status: EvidenceStatus;
};

export type MedDiscrepancy = {
  discrepancy_type: string;
  summary: string;
  requires_human_review: boolean;
  left_source?: SourceRef | null;
  right_source?: SourceRef | null;
};

export type ValidationFinding = {
  code: string;
  message: string;
  requires_review: boolean;
};

export type MedicationLine = {
  medication_name: string;
  strength?: string | null;
  dose?: string | null;
  route?: string | null;
  frequency?: string | null;
  source_ref: SourceRef;
  evidence_status: EvidenceStatus;
};

export type ItemReviewEvent = {
  event_id: string;
  from_status: DiscrepancyItemStatus;
  to_status: DiscrepancyItemStatus;
  reviewed_at: string;
  reviewer_uid?: string | null;
  reviewer_display?: string | null;
  note: string;
  clarification_note?: string | null;
  external_action_required?: string | null;
  external_evidence?: string | null;
  verification_basis?: string | null;
  dismissal_rationale?: string | null;
  reopen_reason?: string | null;
};

export type DiscrepancyItem = {
  item_id: string;
  kind: "medication_discrepancy" | "validation_finding";
  discrepancy?: MedDiscrepancy | null;
  finding?: ValidationFinding | null;
  status: DiscrepancyItemStatus;
  review?: ItemReviewEvent | null;
  review_history: ItemReviewEvent[];
};

export type CaseAttestation = {
  attested_at: string;
  no_discrepancies: boolean;
  weak_evidence_acknowledged: boolean;
  note?: string | null;
};

export type CaseFinalizationRecord = {
  finalized_at: string;
  finalized_by_uid?: string | null;
  finalized_by_display?: string | null;
  fhir_export_resource?: string | null;
  superseded_at?: string | null;
  superseded_reason?: string | null;
};

export type MedReconciliationJob = {
  job_id: string;
  owner_uid?: string | null;
  status: MeddocsJobStatus;
  case_label?: string;
  synthetic_mrn?: string | null;
  transition_type: string;
  case_status: CaseStatus;
  review_granularity?: string;
  legacy_item_review_started?: boolean;
  item_review_phase?: string | null;
  attestation?: CaseAttestation | null;
  discrepancy_items: DiscrepancyItem[];
  finalized_at?: string | null;
  finalized_by_display?: string | null;
  finalization_history?: CaseFinalizationRecord[];
  documents: {
    document_id: string;
    filename: string;
    content_type: string;
    document_type: string;
  }[];
  medications_by_document: Record<string, MedicationLine[]>;
  validation_findings: ValidationFinding[];
  discrepancies: MedDiscrepancy[];
  review_reasons: string[];
  reconciliation_used_weak_evidence: boolean;
  human_review?: {
    reviewed_at: string;
    note?: string | null;
    corrections_count: number;
  } | null;
  fhir_export_resource?: string | null;
  error_code?: string | null;
  error_message?: string | null;
};

export type CaseCreateRequest = {
  case_label?: string;
  synthetic_mrn?: string | null;
  transition_type?: "discharge";
};

export type ItemReviewPatchRequest = {
  to_status: DiscrepancyItemStatus;
  note: string;
  clarification_note?: string | null;
  external_action_required?: string | null;
  external_evidence?: string | null;
  verification_basis?: string | null;
  dismissal_rationale?: string | null;
  reopen_reason?: string | null;
};

export type CaseFinalizeRequest = {
  attestation_note?: string | null;
  weak_evidence_acknowledged?: boolean;
  no_discrepancies_attestation?: boolean;
};

export type ReconciliationReviewRequest = {
  note?: string | null;
  corrections_count?: number;
};
