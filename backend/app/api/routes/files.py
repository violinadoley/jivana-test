import logging
from typing import Annotated

from app.core.config import Settings, get_settings
from app.core.deps import get_activity_service, get_storage_service, require_user
from app.core.exceptions import FileUploadError
from app.schemas.files import FileUploadResponse
from app.services.firebase.activity_service import ActivityService
from app.services.storage.storage_service import ALLOWED_CONTENT_TYPES, StorageService
from fastapi import APIRouter, Depends, File, UploadFile

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/files", tags=["files"])


def _normalize_content_type(content_type: str | None, filename: str) -> str:
    if content_type and content_type.split(";")[0].strip() in ALLOWED_CONTENT_TYPES:
        return content_type.split(";")[0].strip()
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return "application/pdf"
    if lower.endswith(".png"):
        return "image/png"
    if lower.endswith((".jpg", ".jpeg")):
        return "image/jpeg"
    if lower.endswith(".txt"):
        return "text/plain"
    return content_type or "application/octet-stream"


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    settings: Annotated[Settings, Depends(get_settings)],
    storage: Annotated[StorageService, Depends(get_storage_service)],
    user: Annotated[dict | None, Depends(require_user)],
    activity: Annotated[ActivityService, Depends(get_activity_service)],
    file: UploadFile = File(...),
) -> FileUploadResponse:
    if not file.filename:
        raise FileUploadError("Filename is required.")

    content_type = _normalize_content_type(file.content_type, file.filename)
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise FileUploadError("Unsupported file type. Allowed: PDF, PNG, JPEG, TXT.")

    data = await file.read()
    if len(data) > settings.max_upload_size_bytes:
        raise FileUploadError(f"File exceeds maximum size of {settings.max_upload_size_mb} MB.")

    if len(data) == 0:
        raise FileUploadError("File is empty.")

    result = storage.upload(data, file.filename, content_type)
    logger.info(
        "File validated",
        extra={"file_name": result.filename, "size_bytes": result.size_bytes},
    )
    uid = str(user["uid"]) if user and user.get("uid") else None
    activity.log_file_upload(
        user_id=uid,
        filename=result.filename,
        size_bytes=result.size_bytes,
        storage_key=result.storage_key,
    )

    return FileUploadResponse(
        success=True,
        filename=result.filename,
        content_type=result.content_type,
        size_bytes=result.size_bytes,
        storage_key=result.storage_key,
    )
