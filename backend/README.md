# LogPilot Backend

## Run dev server

From the `backend` directory:

```bash
uv run fastapi dev app/main.py
```

The FastAPI CLI expects a file path (not `app.main:app`). It looks for an `app` variable in that file by default.
