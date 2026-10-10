import logging
from typing import Any

from app.core.config import Settings
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


class FirestoreService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._db: Any = None

    def _client(self) -> Any:
        if not self._settings.firebase_configured:
            raise AppException(
                "FIREBASE_NOT_CONFIGURED",
                "Firestore is not configured. Set FIREBASE_PROJECT_ID.",
                status_code=503,
            )
        if self._db is None:
            from firebase_admin import firestore

            self._db = firestore.client()
        return self._db

    def create_document(
        self, collection: str, data: dict[str, Any], document_id: str | None = None
    ) -> str:
        db = self._client()
        if document_id:
            ref = db.collection(collection).document(document_id)
            ref.set(data)
            return document_id
        ref = db.collection(collection).add(data)
        return str(ref[1].id)

    def get_document(self, collection: str, document_id: str) -> dict[str, Any] | None:
        db = self._client()
        snap = db.collection(collection).document(document_id).get()
        if not snap.exists:
            return None
        data = snap.to_dict()
        return data if data is None else dict(data)

    def update_document(self, collection: str, document_id: str, data: dict[str, Any]) -> None:
        db = self._client()
        db.collection(collection).document(document_id).update(data)

    def delete_document(self, collection: str, document_id: str) -> None:
        db = self._client()
        db.collection(collection).document(document_id).delete()

    def list_documents(self, collection: str, limit: int = 50) -> list[dict[str, Any]]:
        db = self._client()
        docs = db.collection(collection).limit(limit).stream()
        return [{"id": d.id, **d.to_dict()} for d in docs]

    def list_documents_ordered(
        self,
        collection: str,
        *,
        order_field: str,
        descending: bool = True,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        from firebase_admin import firestore

        db = self._client()
        direction = firestore.Query.DESCENDING if descending else firestore.Query.ASCENDING
        docs = (
            db.collection(collection)
            .order_by(order_field, direction=direction)
            .limit(limit)
            .stream()
        )
        return [{"id": d.id, **(d.to_dict() or {})} for d in docs]
