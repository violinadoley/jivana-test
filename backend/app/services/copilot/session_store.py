import logging
import uuid
from typing import Any

from app.core.config import Settings
from app.services.firebase.firestore_service import FirestoreService

logger = logging.getLogger(__name__)

COLLECTION = "copilot_sessions"


class CopilotSessionStore:
    def __init__(self, settings: Settings, firestore: FirestoreService | None) -> None:
        self._settings = settings
        self._firestore = firestore
        self._memory: dict[str, dict[str, Any]] = {}

    def create(self, *, user_id: str | None, title: str) -> dict[str, Any]:
        session_id = uuid.uuid4().hex
        payload: dict[str, Any] = {
            "session_id": session_id,
            "user_id": user_id,
            "title": title[:120],
            "messages": [],
        }
        if self._settings.firebase_configured and self._firestore:
            self._firestore.create_document(COLLECTION, payload, document_id=session_id)
        else:
            self._memory[session_id] = payload
        return payload

    def get(self, session_id: str) -> dict[str, Any] | None:
        if self._settings.firebase_configured and self._firestore:
            data = self._firestore.get_document(COLLECTION, session_id)
            return data
        return self._memory.get(session_id)

    def append_message(self, session_id: str, *, role: str, content: str) -> dict[str, Any] | None:
        data = self.get(session_id)
        if not data:
            return None
        messages = list(data.get("messages") or [])
        messages.append({"role": role, "content": content})
        data["messages"] = messages[-40:]
        if self._settings.firebase_configured and self._firestore:
            self._firestore.update_document(COLLECTION, session_id, {"messages": data["messages"]})
        else:
            self._memory[session_id] = data
        return data
