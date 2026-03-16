from __future__ import annotations

import asyncio

from app.common.background_jobs import BackgroundJobService
from app.common.services import CacheService, SearchService
from app.core.resources import redis_client, search_client
from app.db.engine import engine
from app.db.unitofwork import SQLAlchemyUnitOfWork


async def main() -> None:
    cache = CacheService(redis_client)
    search = SearchService(search_client)
    service = BackgroundJobService(
        uow_factory=SQLAlchemyUnitOfWork,
        search=search,
        cache=cache,
    )
    counts = await service.reindex_search_documents()
    print(f"Reindex completed: {counts}")
    await redis_client.aclose()
    await search_client.close()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
