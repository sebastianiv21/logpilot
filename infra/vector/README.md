# Vector parser sidecar

Vector runs alongside the backend and re-parses every log file the backend drops into the shared volume. Today it operates in **dual-write** mode: the Python pipeline still parses and pushes to Loki with `parser="python"`, and Vector pushes the same files with `parser="vector"`. Queries default to the Python labelset (`LOKI_QUERY_PARSER=python`); during cutover the default flips to `vector` and the Python pipeline is removed.

## What the default config does

[`vector.toml`](./vector.toml) addresses three TODOs from the architecture plan:

- **TODO 4 — timestamp fallback.** VRL tries several ISO formats on each line. On miss, it carries the previous line's timestamp forward (so stack-trace continuations inherit the parent's time), then falls back to ingest time (`now()`). Vector's `file` source doesn't surface the file's mtime as a VRL field, so a true mtime fallback is deferred to a custom transform if you ever need it.
- **TODO 5 — service from parent folder.** The path layout is `/var/log/logpilot/<session_id>/<service>/<filename>`, including `stdout` and `stderr`. A single regex extracts both labels — no host-side directory convention required.
- **TODO 7 — configurable parsing.** The config is a single mounted file. Override by bind-mounting your own at `/etc/vector/vector.toml`:

  ```yaml
  # docker-compose.override.yaml
  services:
    vector:
      volumes:
        - ./my-vector.toml:/etc/vector/vector.toml:ro
  ```

  Or override individual fields via the [`VECTOR_CONFIG_*` env vars](https://vector.dev/docs/reference/configuration/).

## How the backend feeds it

`backend/app/services/upload.py` drops every extracted log file into the shared volume at the path Vector expects. The shape is `KNOWLEDGE/upload-derived/<session_id>/<service>/<filename>`. Vector picks them up via inotify; no API call coordinates the handoff.

The Python parser still runs on the same files and pushes to Loki with `parser="python"` — the existing API contract (`UploadResult.lines_parsed`, etc.) is unchanged. Vector's output appears in Loki as a separate, parallel labelset for evaluation.

## Cutover (future PR)

Once Vector parity is verified end-to-end, the steps are:

1. `LOKI_QUERY_PARSER=vector` (so the agent and API read Vector's output)
2. Delete `app/services/log_parser.py`, drop the parse-and-push branch in `upload.py`, drop `derive_labels_from_file_path`. Upload becomes "extract + drop"; `UploadResult` reports file counts only.

Both steps need to land together — they're a behavior change for `query_logs` clients.

## Operating notes

- Vector's `data_dir` (`/var/lib/vector`) holds checkpoints so it doesn't re-ingest files on restart. Persisted via the `vector-data` named volume.
- `out_of_order_action = "accept"` lets Loki accept the parsed timestamps even when they're earlier than ingestion time — necessary for historical zips.
- The `parser=vector` label is set on every push, including via `remove_label_fields = true` so we don't accidentally push other VRL-internal fields as labels.
