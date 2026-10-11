import logging
from typing import Any

from app.core.config import Settings
from app.schemas.meddocs import CaseListFilter, CaseStatus, MedReconciliationJob
from app.services.documents.case_migration import migrate_job_on_read
from app.services.firebase.firestore_service import FirestoreService

logger = logging.getLogger(__name__)

COLLECTION = "meddocs_reconciliation_jobs"


class DocumentStore:
    def __init__(self, settings: Settings, firestore: FirestoreService | None = None) -> None:
        self._settings = settings
        self._firestore = firestore
        self._memory: dict[str, dict[str, Any]] = {}

    def save_job(self, job: MedReconciliationJob) -> None:
        payload = job.model_dump(mode="json")
        if self._settings.firebase_configured and self._firestore:
            self._firestore.create_document(COLLECTION, payload, document_id=job.job_id)
        else:
            self._memory[job.job_id] = payload

    def get_job(
        self,
        job_id: str,
        *,
        persist_migration: bool = True,
    ) -> MedReconciliationJob | None:
        data = self._load(job_id)
        if not data:
            return None
        if "job_id" not in data:
            data["job_id"] = job_id
        job = MedReconciliationJob.model_validate(data)
        migrated = migrate_job_on_read(job)
        if persist_migration and migrated.model_dump(mode="json") != data:
            self.update_job(migrated)
        return migrated

    def update_job(self, job: MedReconciliationJob) -> None:
        payload = job.model_dump(mode="json")
        if self._settings.firebase_configured and self._firestore:
            self._firestore.update_document(COLLECTION, job.job_id, payload)
        else:
            self._memory[job.job_id] = payload

    def list_cases(
        self,
        owner_uid: str | None,
        status_filter: CaseListFilter = CaseListFilter.ALL,
        limit: int = 50,
    ) -> list[MedReconciliationJob]:
        if self._settings.firebase_configured and self._firestore:
            docs = self._firestore.list_documents(COLLECTION, limit=200)
        else:
            docs = [{"id": k, **v} for k, v in self._memory.items()]

        jobs: list[MedReconciliationJob] = []
        for doc in docs:
            doc_owner = doc.get("owner_uid")
            if owner_uid and doc_owner not in (owner_uid, None):
                continue
            jid = str(doc.get("job_id") or doc.get("id"))
            job = self.get_job(jid, persist_migration=False)
            if not job:
                continue
            if not _matches_filter(job, status_filter):
                continue
            jobs.append(job)

        jobs.sort(key=lambda j: j.metrics.started_at or j.finalized_at or "", reverse=True)
        return jobs[:limit]

    def list_review_queue(
        self, owner_uid: str | None, limit: int = 20
    ) -> list[MedReconciliationJob]:
        return self.list_cases(owner_uid, CaseListFilter.AWAITING_REVIEW, limit=limit)

    def _load(self, job_id: str) -> dict[str, Any] | None:
        if self._settings.firebase_configured and self._firestore:
            data = self._firestore.get_document(COLLECTION, job_id)
            return data
        return self._memory.get(job_id)


def _matches_filter(job: MedReconciliationJob, status_filter: CaseListFilter) -> bool:
    if status_filter == CaseListFilter.ALL:
        return True
    cs = job.case_status
    if status_filter == CaseListFilter.DRAFT:
        return cs == CaseStatus.DRAFT
    if status_filter == CaseListFilter.AWAITING_REVIEW:
        return cs in (CaseStatus.AWAITING_REVIEW, CaseStatus.PROCESSING)
    if status_filter == CaseListFilter.LEGACY_BULK_ACKNOWLEDGED:
        return cs == CaseStatus.LEGACY_BULK_ACKNOWLEDGED
    if status_filter == CaseListFilter.REVIEW_DOCUMENTED:
        return cs == CaseStatus.REVIEW_DOCUMENTED
    if status_filter == CaseListFilter.FAILED:
        return cs == CaseStatus.FAILED
    return True
