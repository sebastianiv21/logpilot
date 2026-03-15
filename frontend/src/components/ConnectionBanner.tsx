/**
 * Shows a banner when the backend is unreachable (network or 5xx) with retry guidance (FR-011).
 */

import { useQuery } from '@tanstack/react-query';
import { WifiOff, RefreshCw } from 'lucide-react';
import { getSessions, isConnectionError } from '../services/api';

export function ConnectionBanner() {
  const { isError, error, refetch, isFetching } = useQuery({
    queryKey: ['sessions'],
    queryFn: getSessions,
    retry: false,
    staleTime: 30_000,
    refetchOnWindowFocus: true,
  });

  if (!isError || !error || !isConnectionError(error)) return null;

  const message =
    error instanceof Error ? error.message : 'Backend unavailable. Check your connection.';

  return (
    <div
      className="bg-error text-error-content px-4 py-2 flex flex-wrap items-center justify-center gap-3"
      role="alert"
    >
      <WifiOff size={18} aria-hidden />
      <span>{message}</span>
      <button
        type="button"
        className="btn btn-sm btn-ghost btn-active flex items-center gap-2"
        onClick={() => refetch()}
        disabled={isFetching}
        aria-busy={isFetching}
        aria-label="Retry connection"
      >
        {isFetching ? (
          <span className="loading loading-spinner loading-sm" aria-hidden />
        ) : (
          <RefreshCw size={18} aria-hidden />
        )}
        {isFetching ? 'Checking…' : 'Retry'}
      </button>
      <span className="text-sm opacity-90">Check your network and backend, then retry.</span>
    </div>
  );
}
