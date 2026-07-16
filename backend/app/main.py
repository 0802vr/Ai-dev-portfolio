import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api import router
from app.core.config import get_settings
from app.core.exceptions import ApplicationError
from app.core.logging import configure_logging
from app.db import engine
from app.models import Base

settings = get_settings()
configure_logging(settings.log_file)
logger = logging.getLogger("api.access")

@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan,
              docs_url="/docs", openapi_url="/openapi.json")
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins,
    allow_credentials=False, allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key", "X-Request-ID"])
app.include_router(router, prefix=settings.api_prefix, tags=["portfolio"])

@app.middleware("http")
async def access_log(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))[:100]
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Unhandled request error", extra={"request_id": request_id})
        raise
    response.headers["X-Request-ID"] = request_id
    logger.info("request", extra={"request_id": request_id, "method": request.method,
        "path": request.url.path, "status_code": response.status_code,
        "duration_ms": round((time.perf_counter() - started) * 1000, 2)})
    return response

@app.exception_handler(ApplicationError)
async def application_error(_: Request, exc: ApplicationError):
    return JSONResponse(status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}})

@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"error": {"code": "validation_error",
        "message": "Проверьте введённые данные", "details": exc.errors()}})

@app.exception_handler(SQLAlchemyError)
async def database_error(_: Request, exc: SQLAlchemyError):
    logger.exception("Database error", exc_info=exc)
    return JSONResponse(status_code=503, content={"error": {
        "code": "database_unavailable", "message": "Сервис временно недоступен"}})

@app.exception_handler(Exception)
async def unknown_error(_: Request, exc: Exception):
    logger.exception("Unexpected error", exc_info=exc)
    return JSONResponse(status_code=500, content={"error": {
        "code": "internal_error", "message": "Внутренняя ошибка сервиса"}})

