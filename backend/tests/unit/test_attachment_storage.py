from __future__ import annotations

from io import BytesIO

import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers

from app.common.attachments import WorkAttachmentStorage
from app.core.exceptions import ServiceError


@pytest.mark.asyncio
async def test_save_attachment_stores_allowed_file(tmp_path):
    storage = WorkAttachmentStorage(base_dir=tmp_path)
    file = UploadFile(
        file=BytesIO(b"demo-pdf-content"),
        filename="narjad.pdf",
        headers=Headers({"content-type": "application/pdf"}),
    )

    result = await storage.save(work_id="work-1", file=file)

    saved_path = tmp_path / str(result["storage_key"])

    assert result["file_name"] == "narjad.pdf"
    assert result["content_type"] == "application/pdf"
    assert result["file_size"] == len(b"demo-pdf-content")
    assert saved_path.exists()


@pytest.mark.asyncio
async def test_save_attachment_rejects_large_file(tmp_path):
    storage = WorkAttachmentStorage(base_dir=tmp_path)
    file = UploadFile(
        file=BytesIO(b"x" * (2 * 1024 * 1024 + 1)),
        filename="scan.pdf",
        headers=Headers({"content-type": "application/pdf"}),
    )

    with pytest.raises(ServiceError) as exc_info:
        await storage.save(work_id="work-1", file=file)

    assert exc_info.value.code == "attachment_too_large"
