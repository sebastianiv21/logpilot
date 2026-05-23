FROM python:3.14-slim

WORKDIR /app

# ripgrep powers the agent's grep_repo tool (on-demand code search).
RUN apt-get update \
    && apt-get install -y --no-install-recommends ripgrep \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY app ./app
COPY entrypoint.sh /app/entrypoint.sh
RUN uv sync --frozen --no-dev && chmod +x /app/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uv", "run", "fastapi", "run", "app/main.py", "--port", "8000"]
