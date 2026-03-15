import { useMutation } from '@tanstack/react-query';
import { useRef } from 'react';
import { toast } from 'sonner';
import { ApiError } from '../services/api';
import { uploadLogs } from '../services/api';
import { useCurrentSession } from '../contexts/SessionContext';
import type { UploadResult } from '../lib/schemas';

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
  const { currentSessionId, markSessionHasLogs } = useCurrentSession();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const mutation = useMutation({
    mutationFn: async ({ sessionId, file }: { sessionId: string; file: File }) =>
      uploadLogs(sessionId, file),
    onSuccess: (data: UploadResult, variables) => {
      if (data.status === 'failed') {
        toast.error(shortenUploadError(data.error));
        return;
      }
      // Mark session as having logs so log search can run (T025)
      markSessionHasLogs(variables.sessionId);
      // success or partial (backend uses "partial" when some files/lines skipped or rejected)
      toast.success(
        data.status === 'partial'
          ? 'Upload complete (some files or lines were skipped or rejected).'
          : 'Logs uploaded successfully.'
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

  const result = mutation.data;

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Upload logs</h2>
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
          {mutation.isPending && <span className="loading loading-spinner loading-sm" aria-hidden />}
          {mutation.isPending ? 'Uploading…' : 'Upload'}
        </button>
      </form>

      {mutation.isPending && (
        <div className="flex items-center gap-2 text-base-content/80" role="status" aria-live="polite">
          <span className="loading loading-spinner loading-sm" aria-hidden />
          Uploading…
        </div>
      )}

      {result && !mutation.isPending && (
        <div
          className={`rounded-lg p-4 ${result.status === 'failed' ? 'bg-error/10 text-error-content' : 'bg-success/10 text-success-content'}`}
          role="status"
          aria-live="polite"
        >
          <p className="font-medium">
            {result.status === 'failed'
              ? 'Failed'
              : result.status === 'partial'
                ? 'Complete (some files or lines skipped/rejected)'
                : 'Success'}
          </p>
          {result.status !== 'failed' ? (
            <ul className="mt-2 list-inside list-disc text-sm">
              <li>Files processed: {result.files_processed}</li>
              <li>Files skipped: {result.files_skipped}</li>
              <li>Lines parsed: {result.lines_parsed}</li>
              <li>Lines rejected: {result.lines_rejected}</li>
              <li>
                Parsed coverage:{' '}
                {result.lines_parsed + result.lines_rejected > 0
                  ? `${Math.round((result.lines_parsed / (result.lines_parsed + result.lines_rejected)) * 100)}%`
                  : '—'}
              </li>
            </ul>
          ) : (
            <p className="mt-2 text-sm">{shortenUploadError(result.error)}</p>
          )}
        </div>
      )}
    </div>
  );
}
