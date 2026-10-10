import logging
from typing import Any

from app.core.config import Settings
from app.schemas.meddocs import JobStatus, MedReconciliationJob
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

    def get_job(self, job_id: str) -> MedReconciliationJob | None:
        data = self._load(job_id)
        if not data:
            return None
        if "job_id" not in data:
            data["job_id"] = job_id
        return MedReconciliationJob.model_validate(data)

    def update_job(self, job: MedReconciliationJob) -> None:
        payload = job.model_dump(mode="json")
        if self._settings.firebase_configured and self._firestore:
            self._firestore.update_document(COLLECTION, job.job_id, payload)
        else:
            self._memory[job.job_id] = payload

    def list_review_queue(
        self, owner_uid: str | None, limit: int = 20
    ) -> list[MedReconciliationJob]:
        if self._settings.firebase_configured and self._firestore:
            docs = self._firestore.list_documents(COLLECTION, limit=100)
        else:
            docs = [{"id": k, **v} for k, v in self._memory.items()]

        jobs: list[MedReconciliationJob] = []
        for doc in docs:
            if doc.get("status") != JobStatus.NEEDS_REVIEW.value:
                continue
            if owner_uid and doc.get("owner_uid") not in (owner_uid, None):
                continue
            jid = str(doc.get("job_id") or doc.get("id"))
            job = self.get_job(jid)
            if job:
                jobs.append(job)
            if len(jobs) >= limit:
                break
        return jobs

    def _load(self, job_id: str) -> dict[str, Any] | None:
        if self._settings.firebase_configured and self._firestore:
            data = self._firestore.get_document(COLLECTION, job_id)
            return data
        return self._memory.get(job_id)
