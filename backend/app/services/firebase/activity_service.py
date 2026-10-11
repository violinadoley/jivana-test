import logging
from datetime import UTC, datetime
from typing import Any

from app.core.config import Settings
from app.services.firebase.firestore_service import FirestoreService

logger = logging.getLogger(__name__)

ACTIVITY_COLLECTION = "activity"


class ActivityService:
    def __init__(self, settings: Settings, firestore: FirestoreService) -> None:
        self._settings = settings
        self._firestore = firestore

    @property
    def enabled(self) -> bool:
        return self._settings.firebase_configured

    def _log(self, payload: dict[str, Any]) -> None:
        if not self.enabled:
            return
        try:
            from firebase_admin import firestore

            data = {**payload, "created_at": firestore.SERVER_TIMESTAMP}
            self._firestore.create_document(ACTIVITY_COLLECTION, data)
        except Exception:
            logger.exception("Failed to write activity to Firestore")

    def log_ai_generate(
        self,
        *,
        user_id: str | None,
        message: str,
        response_preview: str,
    ) -> None:
        del response_preview  # Do not persist model output in Firestore.
        length = len(message.strip())
        if length <= 50:
            bucket = "1-50"
        elif length <= 200:
            bucket = "51-200"
        else:
            bucket = "201+"
        self._log(
            {
                "type": "ai_generate",
                "title": "AI generation",
                "summary": f"message_length_bucket={bucket}",
                "user_id": user_id,
            }
        )

    def log_file_upload(
        self,
        *,
        user_id: str | None,
        filename: str,
        size_bytes: int,
        storage_key: str | None,
    ) -> None:
        stored = "stored in Cloud Storage" if storage_key else "validated (storage pending)"
        self._log(
            {
                "type": "file_upload",
                "title": f"Upload: {filename}",
                "summary": f"{size_bytes} bytes — {stored}",
                "user_id": user_id,
                "storage_key": storage_key,
            }
        )

    def log_meddocs_reconciliation(
        self,
        *,
        user_id: str | None,
        job_id: str,
        status: str,
        discrepancy_count: int,
    ) -> None:
        self._log(
            {
                "type": "meddocs_reconciliation",
                "title": "Medication reconciliation",
                "summary": f"status={status}; discrepancies={discrepancy_count}; job={job_id[:10]}",
                "user_id": user_id,
                "job_id": job_id,
            }
        )

    def log_copilot_turn(self, *, user_id: str | None, session_id: str) -> None:
        self._log(
            {
                "type": "copilot_chat",
                "title": "Copilot conversation",
                "summary": f"session={session_id[:10]}",
                "user_id": user_id,
            }
        )

    def log_meeting_intelligence(self, *, user_id: str | None, title: str) -> None:
        self._log(
            {
                "type": "meeting_intelligence",
                "title": f"Meeting: {title[:60]}",
                "summary": "transcript analyzed",
                "user_id": user_id,
            }
        )

    def log_research(self, *, user_id: str | None, question: str) -> None:
        preview = question.strip()
        if len(preview) > 80:
            preview = f"{preview[:77]}..."
        self._log(
            {
                "type": "research",
                "title": "Research synthesis",
                "summary": preview,
                "user_id": user_id,
            }
        )

    def log_workflow_agent(self, *, user_id: str | None, goal: str) -> None:
        preview = goal.strip()
        if len(preview) > 80:
            preview = f"{preview[:77]}..."
        self._log(
            {
                "type": "workflow_agent",
                "title": "Agent workflow",
                "summary": preview,
                "user_id": user_id,
            }
        )

    def log_enterprise_search(self, *, user_id: str | None, query: str) -> None:
        self._log(
            {
                "type": "enterprise_search",
                "title": "Enterprise search",
                "summary": query[:120],
                "user_id": user_id,
            }
        )

    def log_meddocs_review(
        self,
        *,
        user_id: str | None,
        job_id: str,
        note: str | None,
    ) -> None:
        preview = (note or "Acknowledged").strip()
        if len(preview) > 80:
            preview = f"{preview[:77]}..."
        self._log(
            {
                "type": "meddocs_review",
                "title": "Reconciliation reviewed",
                "summary": preview,
                "user_id": user_id,
                "job_id": job_id,
            }
        )

    def list_recent(self, *, user_id: str | None, limit: int = 20) -> list[dict[str, Any]]:
        if not self.enabled:
            return []
        try:
            raw = self._firestore.list_documents_ordered(
                ACTIVITY_COLLECTION,
                order_field="created_at",
                descending=True,
                limit=min(limit * 8, 120),
            )
            rows: list[dict[str, Any]] = []
            for data in raw:
                row_uid = data.get("user_id")
                if user_id is not None and row_uid != user_id:
                    continue
                if self._settings.auth_required and not user_id:
                    continue
                rows.append(data)
                if len(rows) >= limit:
                    break
            return rows
        except Exception:
            logger.exception("Failed to list activity from Firestore")
            return []

    @staticmethod
    def parse_timestamp(value: Any) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.astimezone(UTC) if value.tzinfo else value.replace(tzinfo=UTC)
        if hasattr(value, "timestamp"):
            return datetime.fromtimestamp(value.timestamp(), tz=UTC)
        return None
