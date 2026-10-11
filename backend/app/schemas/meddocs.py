from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field

TransitionType = Literal["discharge", "transfer", "admission"]
ReviewGranularity = Literal["per_item", "legacy_bulk"]
ItemReviewPhase = Literal["in_progress", "complete"]


class EvidenceStatus(StrEnum):
    VERIFIED = "verified"
    LOW = "low"
    VERTEX_ONLY = "vertex_only"


class JobStatus(StrEnum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    NEEDS_REVIEW = "needs_review"
    FAILED = "failed"


class CaseStatus(StrEnum):
    DRAFT = "draft"
    PROCESSING = "processing"
    AWAITING_REVIEW = "awaiting_review"
    LEGACY_BULK_ACKNOWLEDGED = "legacy_bulk_acknowledged"
    REVIEW_DOCUMENTED = "review_documented"
    FAILED = "failed"


class DiscrepancyItemStatus(StrEnum):
    OPEN = "open"
    PENDING_CLARIFICATION = "pending_clarification"
    AWAITING_EXTERNAL_ACTION = "awaiting_external_action"
    RESOLVED_INTENTIONAL = "resolved_intentional"
    RESOLVED_EXTERNALLY_CLOSED = "resolved_externally_closed"
    RESOLVED_NOT_RELEVANT = "resolved_not_relevant"
    LEGACY_UNREVIEWED = "legacy_unreviewed"


CLOSURE_ITEM_STATUSES = frozenset(
    {
        DiscrepancyItemStatus.RESOLVED_INTENTIONAL,
        DiscrepancyItemStatus.RESOLVED_EXTERNALLY_CLOSED,
        DiscrepancyItemStatus.RESOLVED_NOT_RELEVANT,
    }
)

NON_CLOSURE_ITEM_STATUSES = frozenset(
    {
        DiscrepancyItemStatus.OPEN,
        DiscrepancyItemStatus.PENDING_CLARIFICATION,
        DiscrepancyItemStatus.AWAITING_EXTERNAL_ACTION,
        DiscrepancyItemStatus.LEGACY_UNREVIEWED,
    }
)


class DocumentType(StrEnum):
    PRIOR_MEDICATION_RECORD = "prior_medication_record"
    DISCHARGE_SUMMARY = "discharge_summary"
    CURRENT_PRESCRIPTION = "current_prescription"
    LAB_REPORT = "lab_report"
    REFERRAL = "referral"
    INSURANCE_FORM = "insurance_form"
    UNKNOWN = "unknown"


class DiscrepancyType(StrEnum):
    OMITTED_MED = "omitted_med"
    ADDED_MED = "added_med"
    DOSE_MISMATCH = "dose_mismatch"
    CONFLICTING_STRENGTH = "conflicting_strength"
    AMBIGUOUS_MATCH = "ambiguous_match"
    DOCUMENTED_CHANGE = "documented_change"


class BoundingBox(BaseModel):
    x: float
    y: float
    width: float
    height: float


class SourceBlock(BaseModel):
    source_block_id: str
    document_id: str
    page_number: int | None = None
    text: str
    bounding_box: BoundingBox | None = None
    confidence: float | None = None
    evidence_status: EvidenceStatus


class SourceRef(BaseModel):
    document_id: str
    page_number: int | None = None
    source_text: str | None = None
    text_anchor: str | None = None
    bounding_box: BoundingBox | None = None
    extraction_method: str
    confidence: float | None = None
    evidence_status: EvidenceStatus


class ExtractedField(BaseModel):
    name: str
    value: str | None = None
    normalized_value: str | None = None
    source_ref: SourceRef


class ValidationFinding(BaseModel):
    code: str
    severity: str = "warning"
    message: str
    related_fields: list[str] = Field(default_factory=list)
    source_refs: list[SourceRef] = Field(default_factory=list)
    requires_review: bool = True


class MedicationLine(BaseModel):
    medication_name: str
    strength: str | None = None
    dose: str | None = None
    route: str | None = None
    frequency: str | None = None
    source_ref: SourceRef
    evidence_status: EvidenceStatus


class MedDiscrepancy(BaseModel):
    discrepancy_type: DiscrepancyType
    summary: str
    requires_human_review: bool = True
    left_source: SourceRef | None = None
    right_source: SourceRef | None = None


class DocumentMeta(BaseModel):
    document_id: str
    filename: str
    content_type: str
    document_type: DocumentType = DocumentType.UNKNOWN
    storage_key: str | None = None
    content_hash: str | None = None


class JobMetrics(BaseModel):
    started_at: str | None = None
    completed_at: str | None = None
    processing_ms: int | None = None
    extraction_field_count: int = 0
    validation_issue_count: int = 0
    discrepancy_count: int = 0


class HumanReview(BaseModel):
    reviewed_at: str
    reviewer_uid: str | None = None
    corrections_count: int = 0
    note: str | None = None


class ItemReviewEvent(BaseModel):
    event_id: str
    from_status: DiscrepancyItemStatus
    to_status: DiscrepancyItemStatus
    reviewed_at: str
    reviewer_uid: str | None = None
    reviewer_display: str | None = None
    note: str
    clarification_note: str | None = None
    external_action_required: str | None = None
    external_evidence: str | None = None
    verification_basis: str | None = None
    dismissal_rationale: str | None = None
    reopen_reason: str | None = None


class DiscrepancyItem(BaseModel):
    item_id: str
    kind: Literal["medication_discrepancy", "validation_finding"] = "medication_discrepancy"
    discrepancy: MedDiscrepancy | None = None
    finding: ValidationFinding | None = None
    status: DiscrepancyItemStatus = DiscrepancyItemStatus.OPEN
    review: ItemReviewEvent | None = None
    review_history: list[ItemReviewEvent] = Field(default_factory=list)


class CaseAttestation(BaseModel):
    attested_at: str
    attested_by_uid: str | None = None
    attested_by_display: str | None = None
    no_discrepancies: bool = False
    weak_evidence_acknowledged: bool = False
    note: str | None = None


class CaseFinalizationRecord(BaseModel):
    """Append-only ledger entry for each successful finalize-review (never deleted on reopen)."""

    finalized_at: str
    finalized_by_uid: str | None = None
    finalized_by_display: str | None = None
    fhir_export_resource: str | None = None
    superseded_at: str | None = None
    superseded_reason: str | None = None


class MedReconciliationJob(BaseModel):
    job_id: str
    owner_uid: str | None = None
    status: JobStatus
    case_label: str = ""
    synthetic_mrn: str | None = None
    transition_type: TransitionType = "discharge"
    case_status: CaseStatus = CaseStatus.DRAFT
    review_granularity: ReviewGranularity = "per_item"
    legacy_bulk_review: HumanReview | None = None
    legacy_item_review_started: bool = False
    item_review_phase: ItemReviewPhase | None = None
    attestation: CaseAttestation | None = None
    discrepancy_items: list[DiscrepancyItem] = Field(default_factory=list)
    finalized_by_uid: str | None = None
    finalized_by_display: str | None = None
    finalized_at: str | None = None
    finalization_history: list[CaseFinalizationRecord] = Field(
        default_factory=list,
        description=(
            "Append-only finalize ledger. Reopen marks the active record superseded; "
            "re-finalize appends a new CaseFinalizationRecord."
        ),
    )
    documents: list[DocumentMeta] = Field(default_factory=list)
    medications_by_document: dict[str, list[MedicationLine]] = Field(default_factory=dict)
    validation_findings: list[ValidationFinding] = Field(default_factory=list)
    discrepancies: list[MedDiscrepancy] = Field(default_factory=list)
    review_reasons: list[str] = Field(default_factory=list)
    reconciliation_used_weak_evidence: bool = False
    metrics: JobMetrics = Field(default_factory=JobMetrics)
    human_review: HumanReview | None = None
    fhir_export_resource: str | None = None
    error_code: str | None = None
    error_message: str | None = None


class VertexFieldOutput(BaseModel):
    name: str
    value: str | None = None
    source_block_ids: list[str] = Field(default_factory=list)


class VertexExtractOutput(BaseModel):
    document_type: DocumentType = DocumentType.UNKNOWN
    classification_confidence: float = 0.0
    fields: list[VertexFieldOutput] = Field(default_factory=list)
    medications: list[dict[str, Any]] = Field(default_factory=list)


class ReconciliationReviewRequest(BaseModel):
    note: str | None = None
    corrections_count: int = 0


class ReconciliationReviewResponse(BaseModel):
    job_id: str
    status: JobStatus
    human_review: HumanReview


class CaseCreateRequest(BaseModel):
    case_label: str
    synthetic_mrn: str | None = None
    transition_type: TransitionType = "discharge"


class ItemReviewPatchRequest(BaseModel):
    to_status: DiscrepancyItemStatus
    note: str
    clarification_note: str | None = None
    external_action_required: str | None = None
    external_evidence: str | None = None
    verification_basis: str | None = None
    dismissal_rationale: str | None = None
    reopen_reason: str | None = None


class CaseFinalizeRequest(BaseModel):
    attestation_note: str | None = None
    weak_evidence_acknowledged: bool = False
    no_discrepancies_attestation: bool = False


class CaseListFilter(StrEnum):
    ALL = "all"
    DRAFT = "draft"
    AWAITING_REVIEW = "awaiting_review"
    LEGACY_BULK_ACKNOWLEDGED = "legacy_bulk_acknowledged"
    REVIEW_DOCUMENTED = "review_documented"
    FAILED = "failed"
