#!/usr/bin/env bash
set -e

# When running in Docker: rewrite KNOWLEDGE_SOURCES so host paths become container paths.
# - If KNOWLEDGE_SOURCES_MOUNT is set: we mounted that parent at /knowledge; replace it in KNOWLEDGE_SOURCES.
# - Else: we mounted a single path at /knowledge; use /knowledge.
if [ -n "${KNOWLEDGE_SOURCES_MOUNT}" ]; then
  base="${KNOWLEDGE_SOURCES_MOUNT%/}"
  export KNOWLEDGE_SOURCES="${KNOWLEDGE_SOURCES//$base/\/knowledge}"
else
  export KNOWLEDGE_SOURCES="/knowledge"
fi

exec "$@"
