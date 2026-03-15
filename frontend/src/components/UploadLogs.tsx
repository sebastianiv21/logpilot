import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect, useRef } from 'react';
import { formatDistanceToNow, parseISO } from 'date-fns';
import { toast } from 'sonner';
import { Upload } from 'lucide-react';
import { ApiError, getUploadSummary, uploadLogs } from '../services/api';
import { useCurrentSession } from '../contexts/SessionContext';
import type { UploadResult } from '../lib/schemas';
import { UploadSummaryCharts } from './UploadSummaryCharts';

const MAX_ERROR_LENGTH = 120;

/** Shorten long or noisy upload error messages for toast and inline display. */
function shortenUploadError(error: string | null): string {
  if (!error || !error.trim()) return 'Upload failed.';
  const s = error.trim();
  // Loki timestamp/retention errors: one short line
  if (/Loki push failed|entry too far behind|oldest acceptable timestamp/i.test(s)) {
    return 'Log timestamps too old for Loki retention window.';
  }
  if (s.length <= MAX_ERROR_LENGTH) return s;
  return s.slice(0, MAX_ERROR_LENGTH).trim() + '…';
}

/** User-friendly message for known backend error statuses (FR-004, FR-011). */
function uploadErrorMessage(err: unknown): string {
  if (err instanceof ApiError) {
    switch (err.status) {
      case 404:
        return 'Session not found.';
      case 413:
        return 'Archive is too large (e.g. max 100 MB).';
      case 400:
        return shortenUploadError(err.userMessage);
      default:
        return shortenUploadError(err.userMessage);
    }
  }
  if (err instanceof Error) return shortenUploadError(err.message);
  return 'Upload failed.';
}

export function UploadLogs() {
  const {
    currentSessionId,
    markSessionHasLogs,
    lastUploadResultBySessionId,
    setLastUploadResult,
  } = useCurrentSession();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  const {
    data: uploadSummaryFromApi,
    isLoading: isUploadSummaryLoading,
    isError: isUploadSummaryError,
    error: uploadSummaryError,
    refetch: refetchUploadSummary,
    isRefetching: isUploadSummaryRefetching,
  } = useQuery({
    queryKey: ['uploadSummary', currentSessionId ?? ''],
    queryFn: () => getUploadSummary(currentSessionId!),
    enabled: !!currentSessionId,
  });

  const mutation = useMutation({
    mutationFn: async ({ sessionId, file }: { sessionId: string; file: File }) =>
      uploadLogs(sessionId, file),
    onSuccess: (data: UploadResult, variables) => {
      if (data.status === 'failed') {
        toast.error(shortenUploadError(data.error));
        return;
      }
      setLastUploadResult(variables.sessionId, data);
      markSessionHasLogs(variables.sessionId);
      queryClient.setQueryData(['uploadSummary', variables.sessionId], data);
      toast.success(
        data.status === 'partial'
          ? 'Upload complete. Some files or lines were skipped.'
          : 'Logs uploaded.'
      );
    },
    onError: (err) => {
      toast.error(uploadErrorMessage(err));
    },
  });

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const file = fileInputRef.current?.files?.[0];
    if (!currentSessionId) {
      toast.error('Select a session first.');
      return;
    }
    if (!file) {
      toast.error('Choose a .zip file.');
      return;
    }
    if (!file.name.toLowerCase().endsWith('.zip')) {
      toast.error('File must be a .zip archive.');
      return;
    }
    mutation.mutate({ sessionId: currentSessionId, file });
  };

  if (!currentSessionId) {
    return (
      <div className="rounded-lg bg-base-200 p-4 text-base-content/80">
        Select a session to upload logs.
      </div>
    );
  }

  useEffect(() => {
    if (uploadSummaryFromApi && currentSessionId) {
      markSessionHasLogs(currentSessionId);
    }
  }, [uploadSummaryFromApi, currentSessionId, markSessionHasLogs]);

  const resultForCurrentSession =
    uploadSummaryFromApi ??
    lastUploadResultBySessionId[currentSessionId ?? ''] ??
    (mutation.data?.session_id === currentSessionId ? mutation.data : null);

  const handleRetryUploadSummary = () => {
    refetchUploadSummary().then((result) => {
      if (result.data) {
        toast.success('Loaded');
      }
    });
  };

  const isUploadingForCurrentSession =
    mutation.isPending && mutation.variables?.sessionId === currentSessionId;

  const isLoadingSummary = isUploadSummaryLoading || isUploadSummaryRefetching;

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold flex items-center gap-2">
        <Upload size={18} aria-hidden />
        Upload logs
      </h2>
      <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-3">
        <label className="form-control w-full max-w-xs">
          <span className="label-text">Log archive (.zip)</span>
          <input
            ref={fileInputRef}
            type="file"
            accept=".zip"
            className="file-input file-input-bordered w-full max-w-xs"
            aria-label="Choose .zip log archive"
            disabled={mutation.isPending}
          />
        </label>
        <button
          type="submit"
          className="btn btn-primary flex items-center gap-2"
          disabled={mutation.isPending}
          aria-busy={mutation.isPending}
          aria-label="Upload log archive"
        >
          {mutation.isPending ? (
            <span className="loading loading-spinner loading-sm" aria-hidden />
          ) : (
            <Upload size={18} aria-hidden />
          )}
          {mutation.isPending ? 'Uploading…' : 'Upload'}
        </button>
      </form>

      {isLoadingSummary && !resultForCurrentSession && (
        <div className="flex items-center gap-2 text-base-content/80" role="status" aria-live="polite">
          <span className="loading loading-spinner loading-sm" aria-hidden />
          Loading…
        </div>
      )}

      {isUploadSummaryError && !resultForCurrentSession && (
        <div className="rounded-lg p-4 bg-base-200 text-base-content" role="alert">
          <p className="font-medium text-error">
            {uploadSummaryError instanceof Error
              ? uploadSummaryError.message
              : 'Could not load session state.'}
          </p>
          <button
            type="button"
            className="btn btn-sm btn-outline mt-2"
            onClick={handleRetryUploadSummary}
            disabled={isUploadSummaryRefetching}
          >
            {isUploadSummaryRefetching ? 'Retrying…' : 'Retry'}
          </button>
        </div>
      )}

      {isUploadingForCurrentSession && (
        <div className="flex items-center gap-2 text-base-content/80" role="status" aria-live="polite">
          <span className="loading loading-spinner loading-sm" aria-hidden />
          Uploading…
        </div>
      )}

      {resultForCurrentSession && !isUploadingForCurrentSession && (
        <div
          className={`rounded-lg p-4 ${resultForCurrentSession.status === 'failed' ? 'bg-error text-error-content' : 'bg-success/10 text-base-content'}`}
          role="status"
          aria-live="polite"
        >
          <p className="font-medium">
            {resultForCurrentSession.status === 'failed'
              ? 'Failed'
              : resultForCurrentSession.status === 'partial'
                ? 'Complete (some files or lines skipped/rejected)'
                : 'Success'}
          </p>
          {(resultForCurrentSession.uploaded_file_name ?? resultForCurrentSession.updated_at) && (
            <p className="text-sm text-base-content/80 mt-1">
              {resultForCurrentSession.uploaded_file_name && (
                <span>File: {resultForCurrentSession.uploaded_file_name}</span>
              )}
              {resultForCurrentSession.uploaded_file_name && resultForCurrentSession.updated_at && ' · '}
              {resultForCurrentSession.updated_at && (
                <span>
                  Uploaded {formatDistanceToNow(parseISO(resultForCurrentSession.updated_at), { addSuffix: true })}
                </span>
              )}
            </p>
          )}
          {resultForCurrentSession.status !== 'failed' ? (
            <>
              <UploadSummaryCharts result={resultForCurrentSession} />
              <p className="mt-2 text-sm text-base-content/70 sr-only">
                Files processed: {resultForCurrentSession.files_processed}, skipped: {resultForCurrentSession.files_skipped}. Lines parsed: {resultForCurrentSession.lines_parsed}, rejected: {resultForCurrentSession.lines_rejected}. Parsed coverage: {resultForCurrentSession.lines_parsed + resultForCurrentSession.lines_rejected > 0 ? `${Math.round((resultForCurrentSession.lines_parsed / (resultForCurrentSession.lines_parsed + resultForCurrentSession.lines_rejected)) * 100)}%` : '—'}.
              </p>
            </>
          ) : (
            <p className="mt-2 text-sm">{shortenUploadError(resultForCurrentSession.error)}</p>
          )}
        </div>
      )}
    </div>
  );
}
