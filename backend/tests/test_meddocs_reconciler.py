from app.schemas.meddocs import (
    DiscrepancyType,
    DocumentType,
    EvidenceStatus,
    JobStatus,
    MedDiscrepancy,
    MedicationLine,
    SourceRef,
)
from app.services.documents.job_status import compute_job_status
from app.services.documents.med_reconciler import ReconcileInput, reconcile_medications


def _ref(doc_id: str, status: EvidenceStatus = EvidenceStatus.VERIFIED) -> SourceRef:
    return SourceRef(
        document_id=doc_id,
        page_number=1,
        source_text="snippet",
        text_anchor=f"{doc_id}:p1:b1",
        extraction_method="document_ai",
        evidence_status=status,
    )


def _med(
    name: str,
    dose: str,
    doc_id: str,
    status: EvidenceStatus = EvidenceStatus.VERIFIED,
    *,
    strength: str | None = None,
) -> MedicationLine:
    return MedicationLine(
        medication_name=name,
        dose=dose,
        strength=strength,
        source_ref=_ref(doc_id, status),
        evidence_status=status,
    )


def test_baseline_match_only_when_zero_discrepancies() -> None:
    data = ReconcileInput()
    data.document_types = {
        "p": DocumentType.PRIOR_MEDICATION_RECORD,
        "d": DocumentType.DISCHARGE_SUMMARY,
        "r": DocumentType.CURRENT_PRESCRIPTION,
    }
    med = _med("lisinopril", "10 mg", "p")
    data.medications_by_document = {
        "p": [med],
        "d": [_med("lisinopril", "10 mg", "d")],
        "r": [_med("lisinopril", "10 mg", "r")],
    }
    data.identifier_fields = {"p": {"mrn": "1"}, "d": {"mrn": "1"}, "r": {"mrn": "1"}}
    result = reconcile_medications(data)
    assert result.discrepancies == []
    assert compute_job_status(result.discrepancies, result.findings, False) == JobStatus.COMPLETED


def test_documented_change_routes_needs_review() -> None:
    data = ReconcileInput()
    data.discharge_has_documented_change_hint = True
    data.document_types = {
        "d": DocumentType.DISCHARGE_SUMMARY,
        "r": DocumentType.CURRENT_PRESCRIPTION,
    }
    data.medications_by_document = {
        "d": [_med("lisinopril", "20 mg", "d", strength=None)],
        "r": [_med("lisinopril", "10 mg", "r", strength=None)],
    }
    data.identifier_fields = {"d": {"mrn": "1"}, "r": {"mrn": "1"}}
    result = reconcile_medications(data)
    documented = [
        d for d in result.discrepancies if d.discrepancy_type == DiscrepancyType.DOCUMENTED_CHANGE
    ]
    assert documented
    disc = result.discrepancies[0]
    assert disc.requires_human_review is True
    status = compute_job_status(result.discrepancies, result.findings, result.weak_evidence_used)
    assert status == JobStatus.NEEDS_REVIEW


def test_no_auto_complete_when_any_discrepancy() -> None:
    discrepancies = [
        MedDiscrepancy(
            discrepancy_type=DiscrepancyType.DOSE_MISMATCH,
            summary="x",
            requires_human_review=True,
        )
    ]
    assert compute_job_status(discrepancies, [], False) == JobStatus.NEEDS_REVIEW
