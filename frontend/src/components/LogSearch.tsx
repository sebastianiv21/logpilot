import { useState, useCallback } from 'react';
import { useCurrentSession } from '../contexts/SessionContext';
import { LogSearchForm, type LogSearchRequestParams } from './LogSearchForm';
import { LogResults } from './LogResults';
import type { LogsQueryResponse } from '../lib/schemas';
import { queryLogs } from '../services/api';

const LOAD_MORE_INCREMENT = 250;

function nextLimit(current: number): number {
  const next = current + LOAD_MORE_INCREMENT;
  return Math.min(next, 1000);
}

/** When session has no ingested logs, show empty state and do not run query until user has uploaded logs (T025). */
export function LogSearch() {
  const { currentSessionId, sessionIdsWithLogs } = useCurrentSession();
  const [result, setResult] = useState<LogsQueryResponse | null>(null);
  const [lastParams, setLastParams] = useState<LogSearchRequestParams | null>(null);
  const [loadingMore, setLoadingMore] = useState(false);

  const hasUploadedLogs = currentSessionId != null && sessionIdsWithLogs.has(currentSessionId);

  const handleResult = useCallback((data: LogsQueryResponse, params: LogSearchRequestParams) => {
    setResult(data);
    setLastParams(params);
  }, []);

  const handleLoadMore = useCallback(async () => {
    if (!currentSessionId || !lastParams) return;
    const newLimit = nextLimit(lastParams.limit);
    if (newLimit === lastParams.limit) return;
    setLoadingMore(true);
    try {
      const data = await queryLogs(currentSessionId, {
        ...lastParams,
        limit: newLimit,
      });
      setResult(data);
      setLastParams({ ...lastParams, limit: newLimit });
    } finally {
      setLoadingMore(false);
    }
  }, [currentSessionId, lastParams]);

  if (!currentSessionId) {
    return (
      <div className="rounded-lg bg-base-200 p-4 text-base-content/80">
        Select a session to search logs.
      </div>
    );
  }

  if (!hasUploadedLogs) {
    return (
      <div className="rounded-lg bg-base-200 p-4 text-base-content/80" role="status">
        No data — upload logs first to search in this session.
      </div>
    );
  }

  const logs = result?.logs ?? [];
  const currentLimit = lastParams?.limit ?? 100;
  const hasMore = logs.length === currentLimit && currentLimit < 1000;

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Log search</h2>
      <LogSearchForm onResult={handleResult} />
      <LogResults
        logs={logs}
        emptyResult={result !== null && logs.length === 0}
        hasMore={hasMore}
        currentLimit={currentLimit}
        onLoadMore={handleLoadMore}
        loadingMore={loadingMore}
      />
    </div>
  );
}
