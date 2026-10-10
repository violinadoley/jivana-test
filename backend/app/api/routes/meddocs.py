import logging
from datetime import UTC, datetime
from typing import Annotated

from app.core.deps import (
    get_document_store,
    get_meddocs_pipeline,
    require_user,
)
from app.core.exceptions import AppException, FileUploadError
from app.schemas.meddocs import (
    HumanReview,
    JobStatus,
    MedReconciliationJob,
    ReconciliationReviewRequest,
    ReconciliationReviewResponse,
)
from app.services.documents.document_store import DocumentStore
from app.services.documents.intake_pipeline import MeddocsIntakePipeline, UploadedPart
from fastapi import APIRouter, Depends, File, UploadFile

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


@router.post("/reconciliation", response_model=MedReconciliationJob)
async def create_reconciliation(
    pipeline: Annotated[MeddocsIntakePipeline, Depends(get_meddocs_pipeline)],
    user: Annotated[dict | None, Depends(require_user)],
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
    logger.info(
        "MedDocs reconciliation started",
        extra={"file_count": len(parts), "owner_present": bool(uid)},
    )
    try:
        job = pipeline.run_reconciliation(parts, owner_uid=uid)
    except AppException:
        raise
    except Exception as exc:
        logger.exception("MedDocs reconciliation failed")
        raise AppException("MEDDOCS_ERROR", "Reconciliation failed.", status_code=500) from exc
    return job


@router.get("/reconciliation/{job_id}", response_model=MedReconciliationJob)
async def get_reconciliation(
    job_id: str,
    store: Annotated[DocumentStore, Depends(get_document_store)],
    user: Annotated[dict | None, Depends(require_user)],
) -> MedReconciliationJob:
    job = store.get_job(job_id)
    if not job:
        raise AppException("NOT_FOUND", "Job not found.", status_code=404)
    _assert_owner(job, user)
    return job


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
) -> ReconciliationReviewResponse:
    job = store.get_job(job_id)
    if not job:
        raise AppException("NOT_FOUND", "Job not found.", status_code=404)
    _assert_owner(job, user)
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
    job.status = JobStatus.COMPLETED
    store.update_job(job)
    return ReconciliationReviewResponse(job_id=job_id, status=job.status, human_review=review)


def _assert_owner(job: MedReconciliationJob, user: dict | None) -> None:
    from app.core.config import get_settings

    settings = get_settings()
    if not settings.auth_required:
        return
    uid = str(user["uid"]) if user and user.get("uid") else None
    if job.owner_uid and uid and job.owner_uid != uid:
        raise AppException("FORBIDDEN", "Not authorized for this job.", status_code=403)
