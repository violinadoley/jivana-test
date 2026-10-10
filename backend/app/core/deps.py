from typing import Annotated, Any

from app.ai.base import AIService
from app.ai.services.gemini_service import GeminiService
from app.core.config import Settings, get_settings
from app.core.exceptions import AuthenticationError
from app.services.documents.document_ai_service import DocumentAIService
from app.services.documents.document_store import DocumentStore
from app.services.documents.intake_pipeline import MeddocsIntakePipeline
from app.services.documents.vertex_gemini_service import VertexGeminiMeddocsService
from app.services.firebase.activity_service import ActivityService
from app.services.firebase.firestore_service import FirestoreService
from app.services.storage.storage_service import StorageService
from fastapi import Depends, Header

_gemini_override: AIService | None = None


def set_gemini_service_override(service: AIService | None) -> None:
    global _gemini_override
    _gemini_override = service


def get_gemini_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AIService:
    if _gemini_override is not None:
        return _gemini_override
    return GeminiService(settings)


def get_firestore_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> FirestoreService:
    return FirestoreService(settings)


def get_storage_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> StorageService:
    return StorageService(settings)


def get_activity_service(
    settings: Annotated[Settings, Depends(get_settings)],
    firestore: Annotated[FirestoreService, Depends(get_firestore_service)],
) -> ActivityService:
    return ActivityService(settings, firestore)


async def get_current_user_optional(
    settings: Annotated[Settings, Depends(get_settings)],
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any] | None:
    if not authorization or not authorization.startswith("Bearer "):
        if settings.auth_required:
            raise AuthenticationError()
        return None
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        if settings.auth_required:
            raise AuthenticationError()
        return None
    if not settings.firebase_configured:
        if settings.auth_required:
            raise AuthenticationError("Authentication is not configured on the server.")
        return None
    try:
        from firebase_admin import auth

        decoded: dict[str, Any] = auth.verify_id_token(token)
        return decoded
    except Exception as exc:
        if settings.auth_required:
            raise AuthenticationError("Invalid or expired token.") from exc
        return None


async def require_user(
    user: Annotated[dict[str, Any] | None, Depends(get_current_user_optional)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, Any] | None:
    if settings.auth_required and user is None:
        raise AuthenticationError()
    return user


def get_document_ai_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> DocumentAIService:
    return DocumentAIService(settings)


def get_vertex_meddocs_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> VertexGeminiMeddocsService:
    return VertexGeminiMeddocsService(settings)


def get_document_store(
    settings: Annotated[Settings, Depends(get_settings)],
    firestore: Annotated[FirestoreService, Depends(get_firestore_service)],
) -> DocumentStore:
    fs = firestore if settings.firebase_configured else None
    return DocumentStore(settings, firestore=fs)


def get_meddocs_pipeline(
    settings: Annotated[Settings, Depends(get_settings)],
    storage: Annotated[StorageService, Depends(get_storage_service)],
    store: Annotated[DocumentStore, Depends(get_document_store)],
    document_ai: Annotated[DocumentAIService, Depends(get_document_ai_service)],
    vertex: Annotated[VertexGeminiMeddocsService, Depends(get_vertex_meddocs_service)],
) -> MeddocsIntakePipeline:
    return MeddocsIntakePipeline(settings, storage, store, document_ai, vertex)
