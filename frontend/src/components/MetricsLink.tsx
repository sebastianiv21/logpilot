import { useState } from 'react';
import { useCurrentSession } from '../contexts/SessionContext';
import { getLogsRange } from '../services/api';

const GRAFANA_URL_KEY = 'VITE_GRAFANA_URL';

/** Path for grafana-lokiexplore-app: /a/grafana-lokiexplore-app/explore/session_id/{id}/logs */
const LOKI_EXPLORE_PATH = '/a/grafana-lokiexplore-app/explore/session_id';

function getGrafanaBaseUrl(): string {
  const url = import.meta.env[GRAFANA_URL_KEY];
  if (typeof url !== 'string' || !url.trim()) return '';
  return url.trim().replace(/\/$/, '');
}

/** Format ms since epoch as ISO 8601 for Grafana from/to. */
function msToIso(ms: number): string {
  return new Date(ms).toISOString();
}

/**
 * Builds grafana-lokiexplore-app URL: .../explore/session_id/{sessionId}/logs?from=...&to=...&var-filters=...
 */
function buildLokiExploreUrl(
  baseUrl: string,
  sessionId: string,
  fromMs: number,
  toMs: number
): string {
  const path = `${baseUrl.replace(/\/?$/, '')}${LOKI_EXPLORE_PATH}/${encodeURIComponent(sessionId)}/logs`;
  const params = new URLSearchParams({
    patterns: '[]',
    from: msToIso(fromMs),
    to: msToIso(toMs),
    'var-filters': `session_id|=|${sessionId}`,
    'var-fields': '',
    'var-levels': '',
    'var-metadata': '',
    'var-patterns': '',
    'var-lineFilterV2': '',
    'var-lineFilters': '',
    timezone: 'browser',
    'var-all-fields': '',
    urlColumns: '[]',
    visualizationType: '"logs"',
    displayedFields: '[]',
    sortOrder: '"Descending"',
    wrapLogMessage: 'false',
  });
  return `${path}?${params.toString()}`;
}

/** Fallback when range is unavailable: same path, from/to omitted (Grafana may use default range). */
function buildLokiExploreUrlWithoutRange(baseUrl: string, sessionId: string): string {
  const path = `${baseUrl.replace(/\/?$/, '')}${LOKI_EXPLORE_PATH}/${encodeURIComponent(sessionId)}/logs`;
  const params = new URLSearchParams({
    patterns: '[]',
    'var-filters': `session_id|=|${sessionId}`,
    'var-fields': '',
    'var-levels': '',
    'var-metadata': '',
    'var-patterns': '',
    'var-lineFilterV2': '',
    'var-lineFilters': '',
    timezone: 'browser',
    'var-all-fields': '',
    urlColumns: '[]',
    visualizationType: '"logs"',
    displayedFields: '[]',
    sortOrder: '"Descending"',
    wrapLogMessage: 'false',
  });
  return `${path}?${params.toString()}`;
}

/**
 * Button to open grafana-lokiexplore-app logs view in a new tab with session and
 * time window set to the uploaded logs' extent.
 */
export function MetricsLink() {
  const { currentSessionId, sessionIdsWithLogs } = useCurrentSession();
  const baseUrl = getGrafanaBaseUrl();
  const [opening, setOpening] = useState(false);
  const hasUploadedLogs = currentSessionId != null && sessionIdsWithLogs.has(currentSessionId);

  const handleOpen = async () => {
    if (!baseUrl || !currentSessionId) return;
    setOpening(true);
    try {
      const range = await getLogsRange(currentSessionId);
      const url = buildLokiExploreUrl(baseUrl, currentSessionId, range.from_ms, range.to_ms);
      window.open(url, '_blank', 'noopener,noreferrer');
    } catch {
      const url = buildLokiExploreUrlWithoutRange(baseUrl, currentSessionId);
      window.open(url, '_blank', 'noopener,noreferrer');
    } finally {
      setOpening(false);
    }
  };

  if (!baseUrl) {
    return (
      <div className="rounded-lg bg-base-200 p-4 text-base-content/80">
        <p>
          Set <code className="rounded bg-base-300 px-1 text-sm">VITE_GRAFANA_URL</code> in your env
          (e.g. <code className="rounded bg-base-300 px-1 text-sm">http://localhost:3000</code>).
        </p>
      </div>
    );
  }

  if (!currentSessionId) {
    return (
      <div className="rounded-lg bg-base-200 p-4 text-base-content/80" role="status">
        Select a session to open Grafana logs for.
      </div>
    );
  }

  if (!hasUploadedLogs) {
    return (
      <div className="rounded-lg bg-base-200 p-4 text-base-content/80" role="status">
        Upload logs first, then open Grafana to view logs for this session.
      </div>
    );
  }

  return (
    <div className="flex flex-wrap items-center gap-3">
      <button
        type="button"
        className="btn btn-primary"
        onClick={handleOpen}
        disabled={opening}
        aria-busy={opening}
        aria-label={`Open logs in Grafana for current session (${currentSessionId.slice(0, 8)}…)`}
      >
        {opening ? 'Opening…' : 'Open in Grafana'}
      </button>
      <p className="text-sm text-base-content/70">
        Opens the Grafana Loki Explore app for this session with the time window of your uploaded
        logs.
      </p>
    </div>
  );
}
