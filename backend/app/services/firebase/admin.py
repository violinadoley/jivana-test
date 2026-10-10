import logging

import firebase_admin
from app.core.config import Settings
from firebase_admin import credentials

logger = logging.getLogger(__name__)
_initialized = False


def init_firebase(settings: Settings) -> None:
    global _initialized
    if _initialized:
        return
    try:
        firebase_admin.get_app()
        _initialized = True
        return
    except ValueError:
        pass

    if not settings.firebase_project_id:
        logger.info("Firebase not configured; skipping Admin SDK init.")
        return

    try:
        if settings.google_application_credentials:
            cred = credentials.Certificate(settings.google_application_credentials)
            firebase_admin.initialize_app(
                cred,
                {
                    "projectId": settings.firebase_project_id,
                    "storageBucket": settings.firebase_storage_bucket,
                },
            )
        else:
            firebase_admin.initialize_app(
                options={
                    "projectId": settings.firebase_project_id,
                    "storageBucket": settings.firebase_storage_bucket,
                }
            )
        _initialized = True
        logger.info("Firebase Admin SDK initialized.")
    except Exception:
        logger.exception("Failed to initialize Firebase Admin SDK")
