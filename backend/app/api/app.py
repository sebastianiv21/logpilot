"""FastAPI app with router mounting and global exception handler."""

import logging
import time

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.types import ASGIApp, Receive, Scope, Send

from app.api.knowledge import router as knowledge_router
from app.api.logs import router as logs_router
from app.api.reports import router as reports_router
from app.api.sessions import router as sessions_router
from app.api.upload import router as upload_router
from app.lib.prometheus_client import get_metrics

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """Pure ASGI middleware — does NOT wrap the body stream, safe for file uploads."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        method = scope.get("method", "?")
        path = scope.get("path", "?")
        t0 = time.perf_counter()
        logger.info("Request: %s %s", method, path)
        try:
            await self.app(scope, receive, send)
        except Exception:
            logger.exception("Request failed: %s %s", method, path)
            raise
        else:
            ms = (time.perf_counter() - t0) * 1000
            logger.info("Response: %s %s (%.0fms)", method, path, ms)


app = FastAPI(title="LogPilot API", version="0.1.0")

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RootResponse(BaseModel):
    """GET / response."""

    status: str
    service: str


app.include_router(sessions_router)
app.include_router(upload_router)
app.include_router(logs_router)
app.include_router(reports_router)
app.include_router(knowledge_router)


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(content=get_metrics(), media_type="text/plain; version=0.0.4; charset=utf-8")


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Structured detail for 400/404/413/422 from HTTPException."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Structured detail for 422 validation errors."""
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return 500 JSON so the client never sees a broken connection (NetworkError)."""
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )


@app.get("/", response_model=RootResponse)
def root() -> RootResponse:
    return RootResponse(status="ok", service="logpilot-backend")
