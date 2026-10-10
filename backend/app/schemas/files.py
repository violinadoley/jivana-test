from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    success: bool = True
    filename: str
    content_type: str
    size_bytes: int
    storage_key: str | None = None
