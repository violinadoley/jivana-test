from app.services.knowledge.institutional_knowledge import InstitutionalKnowledgeService


def test_knowledge_retrieve_medication_query() -> None:
    service = InstitutionalKnowledgeService()
    hits = service.retrieve("medication reconciliation discharge", limit=3)
    assert len(hits) >= 1
    assert any("reconciliation" in hit["title"].lower() for hit in hits)


def test_fhir_bundle_contains_detected_issue() -> None:
    from app.schemas.meddocs import (
        DiscrepancyType,
        JobStatus,
        MedDiscrepancy,
        MedReconciliationJob,
    )
    from app.services.healthcare.fhir_export_service import build_reconciliation_bundle

    job = MedReconciliationJob(
        job_id="abc123",
        status=JobStatus.NEEDS_REVIEW,
        discrepancies=[
            MedDiscrepancy(
                discrepancy_type=DiscrepancyType.DOSE_MISMATCH,
                summary="Lisinopril 10 mg vs 20 mg",
            )
        ],
    )
    bundle = build_reconciliation_bundle(job)
    assert bundle["resourceType"] == "Bundle"
    types = {entry["resource"]["resourceType"] for entry in bundle["entry"]}
    assert "DetectedIssue" in types
    assert "Provenance" in types
