# LogPilot Backend

## Run dev server

From the `backend` directory:

```bash
uv run fastapi dev app/main.py
```

The FastAPI CLI expects a file path (not `app.main:app`). It looks for an `app` variable in that file by default.

## PDF export

Report export to PDF uses [xhtml2pdf](https://github.com/xhtml2pdf/xhtml2pdf) (pure Python). No system dependencies are required; the package is installed with the project.
