# Knowledge sources in Docker

The backend's two knowledge inputs — source code (for `grep_repo` / `read_file`) and documentation (for the docs ingest pipeline) — are mounted independently into the container at fixed paths. No host-path rewriting, no shared-parent assumption.

## How it works

`docker-compose.yaml` pins the container-side paths and bind-mounts each one from a host path you configure in `.env`:

```yaml
backend:
  environment:
    KNOWLEDGE_CODE_SOURCES: /knowledge/code
    KNOWLEDGE_DOC_SOURCES: /knowledge/docs
  volumes:
    - ${KNOWLEDGE_CODE_HOST_PATH:-./knowledge/code}:/knowledge/code:ro
    - ${KNOWLEDGE_DOC_HOST_PATH:-./knowledge/docs}:/knowledge/docs:ro
```

Inside the container the backend always reads from `/knowledge/code` and `/knowledge/docs`. The host paths can live on different drives, in different repos, with no common parent.

## Configure

In your `.env`:

```bash
KNOWLEDGE_CODE_HOST_PATH=/Users/you/projects/my-app
KNOWLEDGE_DOC_HOST_PATH=/Users/you/projects/appsmith-docs/website/docs
```

Either may be left unset — compose falls back to the in-repo `./knowledge/code` / `./knowledge/docs` directories (empty by default), which is harmless: the corresponding feature just returns no results until you point it at something real.

## Running the backend on the host (no Docker)

When you skip Docker and run `uv run fastapi dev` directly, the `*_HOST_PATH` vars are ignored. Set the actual `*_SOURCES` vars to host paths instead:

```bash
KNOWLEDGE_CODE_SOURCES=/Users/you/projects/my-app
KNOWLEDGE_DOC_SOURCES=/Users/you/projects/appsmith-docs/website/docs
```

Both accept comma-separated lists.

## Migration from `KNOWLEDGE_MOUNT_ROOT`

The previous design used a single `KNOWLEDGE_MOUNT_ROOT` env var plus an entrypoint rewrite step. That's gone — `entrypoint.sh` no longer touches knowledge paths, and `KNOWLEDGE_MOUNT_ROOT` is unread.

Rename in your `.env`:

```diff
-KNOWLEDGE_MOUNT_ROOT=/Users/you/workspace
-KNOWLEDGE_CODE_SOURCES=/Users/you/workspace/app
-KNOWLEDGE_DOC_SOURCES=/Users/you/workspace/docs
+KNOWLEDGE_CODE_HOST_PATH=/Users/you/workspace/app
+KNOWLEDGE_DOC_HOST_PATH=/Users/you/workspace/docs
```

If you only used one of the two before, drop the other entirely.
