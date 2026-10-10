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

    def list_recent(self, *, user_id: str | None, limit: int = 20) -> list[dict[str, Any]]:
        if not self.enabled or not user_id:
            return []
        try:
            raw = self._firestore.list_documents_ordered(
                ACTIVITY_COLLECTION,
                order_field="created_at",
                descending=True,
                limit=min(limit * 5, 100),
            )
            rows: list[dict[str, Any]] = []
            for data in raw:
                if data.get("user_id") != user_id:
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
