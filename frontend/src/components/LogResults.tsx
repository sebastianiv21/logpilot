import { format } from 'date-fns';
import type { LogRecord } from '../lib/schemas';

/** Known label keys we display as columns; others from passthrough shown in metadata. */
const LABEL_KEYS = ['service', 'log_level', 'environment'];

function getDisplayLabels(record: LogRecord): Record<string, string> {
  const out: Record<string, string> = {};
  for (const key of Object.keys(record)) {
    if (key === 'timestamp_ns' || key === 'raw_message') continue;
    const v = (record as Record<string, unknown>)[key];
    if (typeof v === 'string' || typeof v === 'number') out[key] = String(v);
  }
  return out;
}

function formatTimestampNs(ns: number): string {
  try {
    const ms = Math.floor(ns / 1_000_000);
    const d = new Date(ms);
    return format(d, 'yyyy-MM-dd HH:mm:ss.SSS');
  } catch {
    return String(ns);
  }
}

type LogResultsProps = {
  logs: LogRecord[];
  /** When true, show "no logs match" (T024). */
  emptyResult?: boolean;
  /** When true, show "Load more" that calls onLoadMore with increased limit. */
  hasMore?: boolean;
  currentLimit?: number;
  onLoadMore?: () => void;
  loadingMore?: boolean;
};

export function LogResults({
  logs,
  emptyResult,
  hasMore,
  currentLimit,
  onLoadMore,
  loadingMore,
}: LogResultsProps) {
  if (emptyResult && logs.length === 0) {
    return (
      <p className="rounded-lg bg-base-200 p-4 text-base-content/80" role="status">
        No logs match the current filters.
      </p>
    );
  }

  if (logs.length === 0) {
    return null;
  }

  return (
    <div className="space-y-2">
      <div className="overflow-x-auto">
        <table className="table table-sm table-zebra" role="table" aria-label="Log search results">
          <thead>
            <tr>
              <th scope="col">Time</th>
              <th scope="col">Message</th>
              {LABEL_KEYS.map((k) => (
                <th key={k} scope="col">
                  {k}
                </th>
              ))}
              <th scope="col">Other labels</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((record, i) => {
              const labels = getDisplayLabels(record);
              const known: Record<string, string> = {};
              const other: Record<string, string> = {};
              for (const [k, v] of Object.entries(labels)) {
                if (LABEL_KEYS.includes(k)) known[k] = v;
                else other[k] = v;
              }
              return (
                <tr key={i}>
                  <td className="whitespace-nowrap font-mono text-sm">
                    {formatTimestampNs(record.timestamp_ns)}
                  </td>
                  <td className="max-w-md break-words font-mono text-sm">
                    {record.raw_message}
                  </td>
                  {LABEL_KEYS.map((k) => (
                    <td key={k} className="whitespace-nowrap text-sm">
                      {known[k] ?? '—'}
                    </td>
                  ))}
                  <td className="text-sm text-base-content/70">
                    {Object.keys(other).length > 0
                      ? Object.entries(other)
                          .map(([k, v]) => `${k}=${v}`)
                          .join(', ')
                      : '—'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {hasMore && onLoadMore && currentLimit != null && (
        <div className="flex justify-center pt-2">
          <button
            type="button"
            className="btn btn-sm btn-ghost"
            onClick={onLoadMore}
            disabled={loadingMore}
            aria-busy={loadingMore}
          >
            {loadingMore ? 'Loading…' : `Load more (up to ${Math.min(currentLimit + 250, 1000)} results)`}
          </button>
        </div>
      )}
    </div>
  );
}
