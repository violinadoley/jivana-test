import logging
import uuid
from datetime import UTC, datetime
from typing import Annotated

from app.core.deps import (
    get_activity_service,
    get_document_store,
    get_meddocs_pipeline,
    require_user,
)
from app.core.exceptions import AppException, FileUploadError
from app.schemas.meddocs import (
    CaseCreateRequest,
    CaseFinalizeRequest,
    CaseListFilter,
    CaseStatus,
    HumanReview,
    ItemReviewPatchRequest,
    JobStatus,
    MedReconciliationJob,
    ReconciliationReviewRequest,
    ReconciliationReviewResponse,
)
from app.services.documents.case_workflow import (
    assert_discharge_transition,
    begin_item_review,
    complete_item_review,
    finalize_case,
    patch_item,
)
from app.services.documents.document_store import DocumentStore
from app.services.documents.intake_pipeline import MeddocsIntakePipeline, UploadedPart
from app.services.documents.review_summary import render_review_summary_html
from app.services.firebase.activity_service import ActivityService
from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import HTMLResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/meddocs", tags=["meddocs"])


def _normalize_content_type(content_type: str | None, filename: str) -> str:
    from app.services.storage.storage_service import ALLOWED_CONTENT_TYPES

    if content_type and content_type.split(";")[0].strip() in ALLOWED_CONTENT_TYPES:
        return content_type.split(";")[0].strip()
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return "application/pdf"
    if lower.endswith(".txt"):
        return "text/plain"
    return content_type or "application/octet-stream"


def _assert_owner(job: MedReconciliationJob, user: dict | None) -> None:
    from app.core.config import get_settings

    settings = get_settings()
    if not settings.auth_required:
        return
    uid = str(user["uid"]) if user and user.get("uid") else None
    if job.owner_uid and uid and job.owner_uid != uid:
        raise AppException("FORBIDDEN", "Not authorized for this job.", status_code=403)


def _get_case(store: DocumentStore, case_id: str, user: dict | None) -> MedReconciliationJob:
    job = store.get_job(case_id)
    if not job:
        raise AppException("NOT_FOUND", "Case not found.", status_code=404)
    _assert_owner(job, user)
    return job


@router.post("/cases", response_model=MedReconciliationJob)
async def create_case(
    body: CaseCreateRequest,
    store: Annotated[DocumentStore, Depends(get_document_store)],
    user: Annotated[dict | None, Depends(require_user)],
) -> MedReconciliationJob:
    assert_discharge_transition(body.transition_type)
    uid = str(user["uid"]) if user and user.get("uid") else None
    job_id = uuid.uuid4().hex
    job = MedReconciliationJob(
        job_id=job_id,
        owner_uid=uid,
        status=JobStatus.NEEDS_REVIEW,
        case_status=CaseStatus.DRAFT,
        case_label=body.case_label,
        synthetic_mrn=body.synthetic_mrn,
        transition_type=body.transition_type,
    )
    store.save_job(job)
    return job


@router.get("/cases", response_model=list[MedReconciliationJob])
async def list_cases(
    store: Annotated[DocumentStore, Depends(get_document_store)],
    user: Annotated[dict | None, Depends(require_user)],
    status: CaseListFilter = Query(default=CaseListFilter.ALL),
) -> list[MedReconciliationJob]:
    uid = str(user["uid"]) if user and user.get("uid") else None
    return store.list_cases(uid, status_filter=status)


@router.get("/cases/{case_id}", response_model=MedReconciliationJob)
async def get_case(
    case_id: str,
    store: Annotated[DocumentStore, Depends(get_document_store)],
    user: Annotated[dict | None, Depends(require_user)],
) -> MedReconciliationJob:
    return _get_case(store, case_id, user)


@router.post("/cases/{case_id}/reconcile", response_model=MedReconciliationJob)
async def reconcile_case(
    case_id: str,
    pipeline: Annotated[MeddocsIntakePipeline, Depends(get_meddocs_pipeline)],
    store: Annotated[DocumentStore, Depends(get_document_store)],
    user: Annotated[dict | None, Depends(require_user)],
    activity: Annotated[ActivityService, Depends(get_activity_service)],
    files: list[UploadFile] = File(...),
) -> MedReconciliationJob:
    job = _get_case(store, case_id, user)
    assert_discharge_transition(job.transition_type)
    if job.case_status not in (CaseStatus.DRAFT, CaseStatus.AWAITING_REVIEW):
        raise AppException(
            "INVALID_STATE",
            "Case cannot accept a new reconcile run in its current state.",
            status_code=409,
        )

    parts: list[UploadedPart] = []
    for f in files:
        if not f.filename:
            raise FileUploadError("Filename is required.")
        data = await f.read()
        ctype = _normalize_content_type(f.content_type, f.filename)
        parts.append(UploadedPart(f.filename, ctype, data))

    uid = str(user["uid"]) if user and user.get("uid") else None
    try:
        job = pipeline.run_reconciliation(parts, owner_uid=uid or job.owner_uid, existing_job=job)
    except AppException:
        raise
    except Exception as exc:
        logger.exception("MedDocs reconciliation failed")
        raise AppException("MEDDOCS_ERROR", "Reconciliation failed.", status_code=500) from exc

    activity.log_meddocs_reconciliation(
        user_id=uid,
        job_id=job.job_id,
        status=job.status.value,
        discrepancy_count=len(job.discrepancies),
    )
    return job


@router.patch("/cases/{case_id}/items/{item_id}", response_model=MedReconciliationJob)
async def patch_case_item(
    case_id: str,
    item_id: str,
    body: ItemReviewPatchRequest,
    store: Annotated[DocumentStore, Depends(get_document_store)],
    user: Annotated[dict | None, Depends(require_user)],
) -> MedReconciliationJob:
    job = _get_case(store, case_id, user)
    job = patch_item(job, item_id, body, user)
    store.update_job(job)
    return job


@router.post("/cases/{case_id}/begin-item-review", response_model=MedReconciliationJob)
async def begin_case_item_review(
    case_id: str,
    store: Annotated[DocumentStore, Depends(get_document_store)],
    user: Annotated[dict | None, Depends(require_user)],
) -> MedReconciliationJob:
    job = _get_case(store, case_id, user)
    job = begin_item_review(job, user)
    store.update_job(job)
    return job


@router.post("/cases/{case_id}/complete-item-review", response_model=MedReconciliationJob)
async def complete_case_item_review(
    case_id: str,
    store: Annotated[DocumentStore, Depends(get_document_store)],
    user: Annotated[dict | None, Depends(require_user)],
) -> MedReconciliationJob:
    job = _get_case(store, case_id, user)
    job = complete_item_review(job)
    store.update_job(job)
    return job


@router.post("/cases/{case_id}/finalize-review", response_model=MedReconciliationJob)
async def finalize_case_review(
    case_id: str,
    body: CaseFinalizeRequest,
    store: Annotated[DocumentStore, Depends(get_document_store)],
    user: Annotated[dict | None, Depends(require_user)],
    activity: Annotated[ActivityService, Depends(get_activity_service)],
) -> MedReconciliationJob:
    job = _get_case(store, case_id, user)
    job = finalize_case(
        job,
        user,
        attestation_note=body.attestation_note,
        weak_evidence_acknowledged=body.weak_evidence_acknowledged,
        no_discrepancies_attestation=body.no_discrepancies_attestation,
    )
    store.update_job(job)
    uid = str(user["uid"]) if user and user.get("uid") else None
    activity.log_meddocs_review(user_id=uid, job_id=case_id, note=body.attestation_note)
    return job


@router.get("/cases/{case_id}/review-summary")
async def case_review_summary(
    case_id: str,
    store: Annotated[DocumentStore, Depends(get_document_store)],
    user: Annotated[dict | None, Depends(require_user)],
) -> HTMLResponse:
    job = _get_case(store, case_id, user)
    html = render_review_summary_html(job)
    return HTMLResponse(content=html)


@router.post("/reconciliation", response_model=MedReconciliationJob)
async def create_reconciliation(
    pipeline: Annotated[MeddocsIntakePipeline, Depends(get_meddocs_pipeline)],
    user: Annotated[dict | None, Depends(require_user)],
    activity: Annotated[ActivityService, Depends(get_activity_service)],
    files: list[UploadFile] = File(...),
) -> MedReconciliationJob:
    parts: list[UploadedPart] = []
    for f in files:
        if not f.filename:
            raise FileUploadError("Filename is required.")
        data = await f.read()
        ctype = _normalize_content_type(f.content_type, f.filename)
        parts.append(UploadedPart(f.filename, ctype, data))

    uid = str(user["uid"]) if user and user.get("uid") else None
    try:
        job = pipeline.run_reconciliation(parts, owner_uid=uid)
        job.case_label = job.case_label or "Discharge reconciliation"
        job.transition_type = "discharge"
    except AppException:
        raise
    except Exception as exc:
        logger.exception("MedDocs reconciliation failed")
        raise AppException("MEDDOCS_ERROR", "Reconciliation failed.", status_code=500) from exc
    activity.log_meddocs_reconciliation(
        user_id=uid,
        job_id=job.job_id,
        status=job.status.value,
        discrepancy_count=len(job.discrepancies),
    )
    return job


@router.get("/reconciliation/{job_id}", response_model=MedReconciliationJob)
async def get_reconciliation(
    job_id: str,
    store: Annotated[DocumentStore, Depends(get_document_store)],
    user: Annotated[dict | None, Depends(require_user)],
) -> MedReconciliationJob:
    return _get_case(store, job_id, user)


@router.get("/review-queue", response_model=list[MedReconciliationJob])
async def review_queue(
    store: Annotated[DocumentStore, Depends(get_document_store)],
    user: Annotated[dict | None, Depends(require_user)],
) -> list[MedReconciliationJob]:
    uid = str(user["uid"]) if user and user.get("uid") else None
    return store.list_review_queue(owner_uid=uid)


@router.post("/reconciliation/{job_id}/review", response_model=ReconciliationReviewResponse)
async def submit_review(
    job_id: str,
    body: ReconciliationReviewRequest,
    store: Annotated[DocumentStore, Depends(get_document_store)],
    user: Annotated[dict | None, Depends(require_user)],
    activity: Annotated[ActivityService, Depends(get_activity_service)],
) -> ReconciliationReviewResponse:
    raise AppException(
        "DEPRECATED",
        "Bulk review is deprecated. Use per-item PATCH and finalize-review.",
        status_code=410,
    )


@router.post("/reconciliation/{job_id}/review-legacy", response_model=ReconciliationReviewResponse)
async def submit_review_legacy(
    job_id: str,
    body: ReconciliationReviewRequest,
    store: Annotated[DocumentStore, Depends(get_document_store)],
    user: Annotated[dict | None, Depends(require_user)],
    activity: Annotated[ActivityService, Depends(get_activity_service)],
) -> ReconciliationReviewResponse:
    """Hidden compat for migration tests only — creates legacy bulk state."""
    job = _get_case(store, job_id, user)
    if job.status != JobStatus.NEEDS_REVIEW:
        raise AppException("INVALID_STATE", "Job is not awaiting review.", status_code=409)
    uid = str(user["uid"]) if user and user.get("uid") else None
    review = HumanReview(
        reviewed_at=datetime.now(UTC).isoformat(),
        reviewer_uid=uid,
        corrections_count=body.corrections_count,
        note=body.note,
    )
    job.human_review = review
    job.legacy_bulk_review = review
    job.review_granularity = "legacy_bulk"
    job.case_status = CaseStatus.LEGACY_BULK_ACKNOWLEDGED
    job.status = JobStatus.NEEDS_REVIEW
    from app.services.documents.case_migration import migrate_job_on_read

    job = migrate_job_on_read(job)
    store.update_job(job)
    activity.log_meddocs_review(user_id=uid, job_id=job_id, note=body.note)
    return ReconciliationReviewResponse(job_id=job_id, status=job.status, human_review=review)
