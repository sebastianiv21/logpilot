#!/usr/bin/env bash
# Optional API validation for quickstart.md (Phase 5 T017).
# Run with backend base URL (default http://localhost:8000).
# Exits 0 if GET /sessions and GET /sessions/{id}/upload-summary behave per contract.

set -e
BASE_URL="${1:-http://localhost:8000}"
BASE_URL="${BASE_URL%/}"

echo "Validating upload-summary API at $BASE_URL ..."

# GET /sessions must return 200
SESSIONS=$(curl -s -w "\n%{http_code}" "$BASE_URL/sessions")
HTTP_CODE=$(echo "$SESSIONS" | tail -n1)
BODY=$(echo "$SESSIONS" | sed '$d')
if [ "$HTTP_CODE" != "200" ]; then
  echo "FAIL: GET /sessions returned $HTTP_CODE"
  exit 1
fi

# Extract first session id (simple grep; session ids are UUIDs)
SESSION_ID=$(echo "$BODY" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
if [ -z "$SESSION_ID" ]; then
  echo "No sessions found; creating one via POST /sessions ..."
  CREATE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/sessions" -H "Content-Type: application/json" -d "{}")
  CREATE_CODE=$(echo "$CREATE" | tail -n1)
  CREATE_BODY=$(echo "$CREATE" | sed '$d')
  if [ "$CREATE_CODE" != "201" ]; then
    echo "FAIL: POST /sessions returned $CREATE_CODE"
    exit 1
  fi
  SESSION_ID=$(echo "$CREATE_BODY" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
fi

# GET /sessions/{id}/upload-summary: 200 (if has summary) or 404 (no summary / session not found) are both valid
SUMMARY_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/sessions/$SESSION_ID/upload-summary")
if [ "$SUMMARY_CODE" != "200" ] && [ "$SUMMARY_CODE" != "404" ]; then
  echo "FAIL: GET /sessions/{id}/upload-summary returned $SUMMARY_CODE (expected 200 or 404)"
  exit 1
fi

echo "OK: GET /sessions 200, GET /sessions/{id}/upload-summary $SUMMARY_CODE (per contract)."
exit 0
