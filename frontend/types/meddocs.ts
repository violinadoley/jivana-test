export type MeddocsJobStatus =
  | "processing"
  | "completed"
  | "needs_review"
  | "failed";

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

export type MedReconciliationJob = {
  job_id: string;
  owner_uid?: string | null;
  status: MeddocsJobStatus;
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
  error_code?: string | null;
  error_message?: string | null;
};

export type ReconciliationReviewRequest = {
  note?: string | null;
  corrections_count?: number;
};
