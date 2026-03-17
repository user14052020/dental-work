from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.exceptions import NotFoundError, ServiceError


ALLOWED_ATTACHMENT_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
}

ALLOWED_ATTACHMENT_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


class WorkAttachmentStorage:
    def __init__(self, base_dir: Path | None = None):
        self._base_dir = base_dir or settings.attachments_storage_path
        self._base_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, *, work_id: str, file: UploadFile) -> dict[str, str | int]:
        file_name = (file.filename or "").strip()
        extension = Path(file_name).suffix.lower()

        if not file_name or extension not in ALLOWED_ATTACHMENT_EXTENSIONS:
            raise ServiceError(
                message="Разрешены только изображения, PDF, Word и Excel файлы.",
                code="attachment_invalid_type",
            )

        if file.content_type and file.content_type not in ALLOWED_ATTACHMENT_CONTENT_TYPES:
            raise ServiceError(
                message="Неподдерживаемый тип файла.",
                code="attachment_invalid_content_type",
            )

        content = await file.read()
        if not content:
            raise ServiceError(message="Файл пустой.", code="attachment_empty")

        if len(content) > settings.attachments_max_size_bytes:
            raise ServiceError(
                message=f"Максимальный размер файла {settings.attachments_max_size_bytes // (1024 * 1024)} МБ.",
                code="attachment_too_large",
            )

        storage_key = f"{work_id}/{uuid4().hex}{extension}"
        destination = self._base_dir / storage_key
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)

        return {
            "storage_key": storage_key,
            "file_name": file_name,
            "content_type": file.content_type or "application/octet-stream",
            "file_size": len(content),
        }

    def delete(self, storage_key: str) -> None:
        path = self._base_dir / storage_key
        if path.exists():
            path.unlink()

        current = path.parent
        while current != self._base_dir and current.exists():
            try:
                current.rmdir()
            except OSError:
                break
            current = current.parent

    def build_download_url(self, work_id: str, attachment_id: str, storage_key: str | None = None) -> str:
        if settings.attachments_public_base_url:
            suffix = storage_key or f"{work_id}/{attachment_id}"
            return f"{settings.attachments_public_base_url.rstrip('/')}/{suffix.lstrip('/')}"
        return f"/api/proxy/works/{work_id}/attachments/{attachment_id}/download"

    def build_file_response(self, *, storage_key: str, download_name: str, media_type: str) -> FileResponse:
        path = self._base_dir / storage_key
        if not path.exists():
            raise NotFoundError("work_attachment_file", storage_key)
        return FileResponse(path=path, filename=download_name, media_type=media_type)
