# Knowledge source path: Docker options

## Problem

The backend reads `KNOWLEDGE_CODE_SOURCES` and `KNOWLEDGE_DOC_SOURCES` from the environment. When running **in a container**, a host path (e.g. `/Users/you/project/docs`) does not exist inside the container, so ingest fails with "path does not exist".

---

## Current approach

- **KNOWLEDGE_CODE_SOURCES** in `.env` = host paths to repo/code content.
- **KNOWLEDGE_DOC_SOURCES** in `.env` = host paths to documentation content.
- **KNOWLEDGE_MOUNT_ROOT** in `.env` = common parent directory for those paths.
- **Docker Compose** mounts that parent to `/knowledge`.
- The backend entrypoint rewrites the configured code/doc paths from the host prefix to `/knowledge`.

Same `.env` works for both:

- **Local run:** app reads `KNOWLEDGE_CODE_SOURCES` and `KNOWLEDGE_DOC_SOURCES` as-is.
- **Docker:** compose mounts `KNOWLEDGE_MOUNT_ROOT`, and the entrypoint rewrites those configured paths into container paths under `/knowledge`.

Example:

- `KNOWLEDGE_MOUNT_ROOT=/Users/you/workspace`
- `KNOWLEDGE_CODE_SOURCES=/Users/you/workspace/app`
- `KNOWLEDGE_DOC_SOURCES=/Users/you/workspace/docs`

Inside the container those become:

- `KNOWLEDGE_CODE_SOURCES=/knowledge/app`
- `KNOWLEDGE_DOC_SOURCES=/knowledge/docs`
