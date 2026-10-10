from typing import Any


class AppException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication required.") -> None:
        super().__init__("AUTHENTICATION_ERROR", message, status_code=401)


class ValidationError(AppException):
    def __init__(self, message: str) -> None:
        super().__init__("VALIDATION_ERROR", message, status_code=422)


class AIGenerationError(AppException):
    def __init__(self, message: str = "Unable to generate a response.") -> None:
        super().__init__("AI_GENERATION_ERROR", message, status_code=502)


class FileUploadError(AppException):
    def __init__(self, message: str) -> None:
        super().__init__("FILE_UPLOAD_ERROR", message, status_code=400)


class DocumentAIConfigurationError(AppException):
    def __init__(self, message: str) -> None:
        super().__init__("DOCUMENT_AI_MISCONFIGURED", message, status_code=503)


class MeddocsProcessingError(AppException):
    def __init__(self, message: str, code: str = "MEDDOCS_PROCESSING_ERROR") -> None:
        super().__init__(code, message, status_code=422)
