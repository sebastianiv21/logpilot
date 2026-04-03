/**
 * KnowledgeIngest: source-specific status cards and re-ingest controls.
 */

import { Database, RefreshCw, RotateCcw } from 'lucide-react'
import { useKnowledgeIngest } from '../hooks/useKnowledgeIngest'
import type { KnowledgeSourceStatus } from '../lib/schemas'

function formatDate(value: string | null | undefined): string {
  if (!value) return 'Never'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

function SourceCard({
  source,
  isStarting,
  onStart,
}: {
  source: KnowledgeSourceStatus;
  isStarting: boolean;
  onStart: (mode: 'incremental' | 'force') => void;
}) {
  const isRunning = source.status === 'running'

  return (
    <article className="rounded-xl border border-base-300 bg-base-100 p-4 space-y-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="font-semibold">{source.display_name}</h3>
          <p className="text-sm text-base-content/70">
            Status: <span className="capitalize">{source.status}</span>
          </p>
        </div>
        {(isRunning || isStarting) && <span className="loading loading-spinner loading-sm" aria-hidden />}
      </div>
      <div className="text-sm space-y-1">
        <p>
          Configured paths:{' '}
          {source.configured_paths.length > 0 ? source.configured_paths.join(', ') : 'Not configured'}
        </p>
        <p>Last completed: {formatDate(source.last_completed_at)}</p>
        <p>Last mode: {source.last_ingest_mode ?? 'N/A'}</p>
        <p>Last chunks: {source.last_chunks_ingested}</p>
        <p>Files processed: {source.last_files_processed}</p>
        <p>Files skipped unchanged: {source.last_files_skipped_unchanged}</p>
        <p>Files deleted: {source.last_files_deleted}</p>
      </div>
      {source.last_error && (
        <div className="alert alert-error py-2" role="alert">
          <span className="text-sm">{source.last_error}</span>
        </div>
      )}
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          className="btn btn-primary btn-sm flex items-center gap-2"
          onClick={() => onStart('incremental')}
          disabled={isRunning || isStarting || source.configured_paths.length === 0}
        >
          <RefreshCw size={16} aria-hidden />
          Re-ingest
        </button>
        <button
          type="button"
          className="btn btn-outline btn-sm flex items-center gap-2"
          onClick={() => onStart('force')}
          disabled={isRunning || isStarting || source.configured_paths.length === 0}
        >
          <RotateCcw size={16} aria-hidden />
          Force re-ingest
        </button>
      </div>
    </article>
  )
}

export function KnowledgeIngest() {
  const { statusQuery, startMutation } = useKnowledgeIngest()
  const { data, isLoading: statusLoading, error: statusError } = statusQuery
  const { mutate: startIngest, isPending: starting, variables } = startMutation

  return (
    <section className="space-y-3" aria-labelledby="knowledge-ingest-heading">
      <h2 id="knowledge-ingest-heading" className="text-xl font-semibold flex items-center gap-2">
        <Database size={18} aria-hidden />
        Add content
      </h2>
      <p className="text-sm text-base-content/70" role="status" aria-live="polite">
        {statusLoading && !data
          ? 'Loading knowledge source status…'
          : statusError
            ? "Couldn't load knowledge source status."
            : 'Code and documentation are tracked separately so you can re-ingest only what changed.'}
      </p>
      <div className="grid gap-4 md:grid-cols-2">
        {(data?.sources ?? []).map((source) => (
          <SourceCard
            key={source.source_key}
            source={source}
            isStarting={starting && variables?.source === source.source_key}
            onStart={(mode) => startIngest({ source: source.source_key, mode })}
          />
        ))}
      </div>
    </section>
  )
}
