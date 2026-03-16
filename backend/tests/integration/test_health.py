from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint_reports_ok(monkeypatch):
    monkeypatch.setattr("app.main.check_database_health", AsyncMock(return_value=True))
    monkeypatch.setattr("app.main.CacheService.ping", AsyncMock(return_value=True))
    monkeypatch.setattr("app.main.SearchService.ping", AsyncMock(return_value=True))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["checks"] == {"database": True, "redis": True, "elasticsearch": True}
