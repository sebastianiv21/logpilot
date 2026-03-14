# Knowledge source path: Docker options

## Problem

The backend reads `KNOWLEDGE_SOURCES` (paths to docs) from the environment. When running **in a container**, a host path (e.g. `/Users/you/project/docs`) does not exist inside the container, so ingest fails with "path does not exist".

---

## Option A: Two env vars (previous approach)

- **KNOWLEDGE_SOURCES_HOST_PATH** in `.env` → used only for the Docker volume mount.
- **KNOWLEDGE_SOURCES** set in `docker-compose` to `/knowledge/docs` → used inside the container.

**Pros:** Clear separation; supports multiple host paths later (multiple mounts).  
**Cons:** Two variables for “where are my docs”; easy to set only one and get confused.

---

## Option B: Single KNOWLEDGE_SOURCES (recommended)

- **KNOWLEDGE_SOURCES** in `.env` = your **host** path (e.g. `/Users/you/appsmith-docs/website/docs`).
- **Docker Compose** uses that same value for the volume: `mount host path → /knowledge/docs`.
- **Docker Compose** overrides the **container** env to `KNOWLEDGE_SOURCES=/knowledge/docs`.

Same `.env` works for both:

- **Local run:** app reads `KNOWLEDGE_SOURCES` and uses the path as-is.
- **Docker:** compose uses `KNOWLEDGE_SOURCES` for the mount and forces the container to use `/knowledge/docs`.

**Pros:** One variable; same file for local and Docker; less to remember.  
**Cons:** For Docker, only a **single** path is supported for the mount (comma-separated values would break the volume spec). For multiple sources in Docker you’d mount a parent directory or use a second var (e.g. keep `KNOWLEDGE_SOURCES_HOST_PATH` for the mount).

---

## Option C: No default mount; document only

- No knowledge volume in `docker-compose`.
- Docs tell users: “Add a volume and set `KNOWLEDGE_SOURCES=/knowledge/docs`.”

**Pros:** No magic; explicit.  
**Cons:** More manual steps; easy to forget or misconfigure.

---

## Multiple sources (docs + repo)

When `KNOWLEDGE_SOURCES` is comma-separated, set **KNOWLEDGE_SOURCES_MOUNT** to the common parent on the host. The backend image’s entrypoint rewrites `KNOWLEDGE_SOURCES` so those host paths become paths under `/knowledge` in the container. You never set container paths by hand.
