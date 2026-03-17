from __future__ import annotations

from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.exception_handlers import register_exception_handlers
from app.api.router import api_router
from app.common.background_jobs import BackgroundJobRunner, BackgroundJobService
from app.common.services import CacheService, SearchService
from app.core.config import settings
from app.core.resources import redis_client, search_client
from app.db.engine import check_database_health, engine
from app.db.unitofwork import SQLAlchemyUnitOfWork


@asynccontextmanager
async def lifespan(_: FastAPI):
    cache_service = CacheService(redis_client)
    search_service = SearchService(search_client)
    background_job_runner = BackgroundJobRunner(
        service=BackgroundJobService(
            uow_factory=SQLAlchemyUnitOfWork,
            search=search_service,
            cache=cache_service,
        ),
        cache=cache_service,
    )
    try:
        await search_service.ensure_indices()
    except Exception:
        # Elastic can become available after app startup in local Docker environments.
        pass
    background_job_runner.start()
    yield
    await background_job_runner.stop()
    await redis_client.aclose()
    await search_client.close()
    await engine.dispose()


app = FastAPI(title=settings.app_name, debug=settings.app_debug, lifespan=lifespan)
app.include_router(api_router, prefix=settings.api_v1_prefix)
settings.attachments_storage_path.mkdir(parents=True, exist_ok=True)
app.mount("/media/attachments", StaticFiles(directory=settings.attachments_storage_path), name="work-attachments")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.parsed_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request.state.request_id = str(uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response


register_exception_handlers(app)


@app.get("/health")
async def healthcheck() -> JSONResponse:
    try:
        db_ready = await check_database_health()
    except Exception:
        db_ready = False

    try:
        redis_ready = await CacheService(redis_client).ping()
    except Exception:
        redis_ready = False

    try:
        elastic_ready = await SearchService(search_client).ping()
    except Exception:
        elastic_ready = False

    return JSONResponse(
        content={
            "status": "ok" if all([db_ready, redis_ready, elastic_ready]) else "degraded",
            "checks": {
                "database": db_ready,
                "redis": redis_ready,
                "elasticsearch": elastic_ready,
            },
        }
    )
