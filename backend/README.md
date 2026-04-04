# LogPilot Backend

## Run dev server

From the `backend` directory:

```bash
uv run fastapi dev app/main.py
```

The FastAPI CLI expects a file path (not `app.main:app`). It looks for an `app` variable in that file by default.

## PDF export

Report export to PDF uses ReportLab and streams the generated file back to the client from a spooled temporary file, which avoids creating an extra in-memory `bytes` copy in the API layer.

The backend also logs one structured `pdf_export` event per request with content-free diagnostics such as report size, code-fence counts, parsed block counts, render duration, and before/after process max RSS. Oversized or pathological inputs are rejected with a deterministic API error so the Markdown export remains available as a safe fallback.
