#!/usr/bin/env bash
set -e

# When running in Docker: rewrite configured knowledge paths so host paths become container paths.
# KNOWLEDGE_MOUNT_ROOT is mounted at /knowledge, and any configured code/doc source path
# under that root is rewritten to the container path.
if [ -n "${KNOWLEDGE_MOUNT_ROOT}" ]; then
  base="${KNOWLEDGE_MOUNT_ROOT%/}"
  if [ -n "${KNOWLEDGE_CODE_SOURCES}" ]; then
    export KNOWLEDGE_CODE_SOURCES="${KNOWLEDGE_CODE_SOURCES//$base/\/knowledge}"
  fi
  if [ -n "${KNOWLEDGE_DOC_SOURCES}" ]; then
    export KNOWLEDGE_DOC_SOURCES="${KNOWLEDGE_DOC_SOURCES//$base/\/knowledge}"
  fi
fi

exec "$@"
