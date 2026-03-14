"""Minimal FastAPI app for Phase 1; will be extended in Phase 2 with routers and error handling."""
from fastapi import FastAPI

app = FastAPI(title="LogPilot API", version="0.1.0")


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "service": "logpilot-backend"}
