#!/usr/bin/env bash
set -e

# Container-side knowledge paths are fixed by docker-compose
# (KNOWLEDGE_CODE_SOURCES=/knowledge/code, KNOWLEDGE_DOC_SOURCES=/knowledge/docs)
# and the corresponding host paths are bind-mounted there. Nothing to rewrite.

exec "$@"
