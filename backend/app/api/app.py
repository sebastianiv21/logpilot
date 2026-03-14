"""FastAPI app with router mounting and global exception handler."""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.sessions import router as sessions_router

app = FastAPI(title="LogPilot API", version="0.1.0")

app.include_router(sessions_router)


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


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "service": "logpilot-backend"}
