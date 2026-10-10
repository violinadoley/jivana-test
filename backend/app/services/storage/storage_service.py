import logging
import uuid
from dataclasses import dataclass

from app.core.config import Settings
from app.core.exceptions import FileUploadError

logger = logging.getLogger(__name__)

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "text/plain",
}


@dataclass
class UploadResult:
    storage_key: str | None
    filename: str
    content_type: str
    size_bytes: int


class StorageService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def storage_configured(self) -> bool:
        env = self._settings.environment.lower()
        runtime_adc = env in ("production", "cloud")
        return bool(
            self._settings.firebase_project_id
            and self._settings.firebase_storage_bucket
            and (self._settings.google_application_credentials or runtime_adc)
        )

    def upload(self, data: bytes, filename: str, content_type: str) -> UploadResult:
        size = len(data)
        storage_key: str | None = None

        if self.storage_configured:
            try:
                from google.cloud import storage  # type: ignore[attr-defined]

                client = storage.Client(project=self._settings.firebase_project_id)
                bucket = client.bucket(self._settings.firebase_storage_bucket)
                storage_key = f"uploads/{uuid.uuid4().hex}/{filename}"
                blob = bucket.blob(storage_key)
                blob.upload_from_string(data, content_type=content_type)
                logger.info("Uploaded file to storage", extra={"storage_key": storage_key})
            except Exception as exc:
                logger.exception("Storage upload failed")
                raise FileUploadError("Unable to store file.") from exc
        else:
            logger.debug("Storage not configured; metadata-only upload.")

        return UploadResult(
            storage_key=storage_key,
            filename=filename,
            content_type=content_type,
            size_bytes=size,
        )
