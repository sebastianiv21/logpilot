# Vector parser sidecar

Vector is LogPilot's log ingest pipeline. The backend extracts each uploaded
archive and drops the log files into a shared volume; Vector tails the volume,
parses each line, and pushes to Loki. The backend never inspects log content
itself.

## What the default config does

[`vector.toml`](./vector.toml) handles three concerns:

- **Timestamp extraction.** VRL handles three shapes:
  - JSON-line records — MongoDB's `t.$date`, Caddy's `ts` (epoch float)
  - Text-prefix records — ISO 8601 with `T` (most services), Postgres `YYYY-MM-DD HH:MM:SS.fff UTC`, supervisor/keycloak `YYYY-MM-DD HH:MM:SS,SSS`, Redis `<pid>:<role> DD Mon YYYY HH:MM:SS.SSS`
  - Anything else (SLF4J banners, prose, stack frames) — ingest time (`now()`)
  - True "carry the previous line's timestamp forward to stack-trace continuations" needs Vector's `multiline` config on the file source — different start pattern per service. Deferred to a follow-up.
- **Service from parent folder.** The path layout is `/var/log/logpilot/<session_id>/<service>/<filename>`, where filename can be `<container_id>-stdout.log`, `<container_id>-stderr.log`, or any `*.log`. A single regex extracts session_id + service + filename; a second regex pulls `container_id` and `stream` (stdout/stderr) out of docker-style filenames.
- **Configurable parsing.** The config is a single mounted file. Override by bind-mounting your own at `/etc/vector/vector.toml`:

  ```yaml
  # docker-compose.override.yaml
  services:
    vector:
      volumes:
        - ./my-vector.toml:/etc/vector/vector.toml:ro
  ```

  Or override individual fields via the [`VECTOR_CONFIG_*` env vars](https://vector.dev/docs/reference/configuration/).

## How the backend feeds it

`backend/app/services/upload.py` drops every extracted log file into the shared
volume at the path Vector expects. The shape is
`<VECTOR_LOG_DROP_DIR>/<session_id>/<service>/<filename>`. Vector picks them
up via inotify; no API call coordinates the handoff.

## Operating notes

- Vector's `data_dir` (`/var/lib/vector`) holds checkpoints so it doesn't re-ingest files on restart. Persisted via the `vector-data` named volume.
- `out_of_order_action = "accept"` lets Loki accept the parsed timestamps even when they're earlier than ingestion time — necessary for historical zips.
- `remove_label_fields = true` ensures no VRL-internal fields leak into Loki as labels.
