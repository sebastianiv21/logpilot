/**
 * KnowledgeIngest: button to start ingest, display status (running / idle),
 * last result or error message (FR-007).
 */

import { Database } from 'lucide-react'
import { useKnowledgeIngest } from '../hooks/useKnowledgeIngest'

export function KnowledgeIngest() {
  const { statusQuery, startMutation } = useKnowledgeIngest()
  const { data: status, isLoading: statusLoading, error: statusError } = statusQuery
  const { mutate: startIngest, isPending: starting } = startMutation

  const isRunning = status?.status === 'running'
  const isIdle = status?.status === 'idle'
  const lastResult = status?.last_result
  const errorMessage = status?.error

  return (
    <section className="space-y-3" aria-labelledby="knowledge-ingest-heading">
      <h2 id="knowledge-ingest-heading" className="text-xl font-semibold flex items-center gap-2">
        <Database size={18} aria-hidden />
        Add content
      </h2>
      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          className="btn btn-primary flex items-center gap-2"
          onClick={() => startIngest(undefined)}
          disabled={isRunning || starting}
          aria-busy={isRunning || starting}
          aria-describedby="ingest-status"
          aria-label="Start knowledge base ingestion"
        >
          {(starting || isRunning) ? (
            <span className="loading loading-spinner loading-sm" aria-hidden />
          ) : (
            <Database size={18} aria-hidden />
          )}
          {starting ? 'Starting…' : isRunning ? 'Ingesting…' : 'Start ingestion'}
        </button>
        <span
          id="ingest-status"
          className="text-sm text-base-content/70 flex items-center gap-2"
          role="status"
          aria-live="polite"
        >
          {statusLoading && !status ? (
            <>
              <span className="loading loading-spinner loading-sm" aria-hidden />
              Loading status…
            </>
          ) : (
            statusError
              ? 'Couldn\'t load status'
              : isRunning
                ? 'Ingesting… This may take a few minutes.'
                : isIdle && lastResult
                  ? `Last run: ${lastResult.chunks_ingested ?? 0} chunks, ${lastResult.files_processed ?? 0} files`
                  : isIdle && errorMessage
                    ? `Last run failed: ${errorMessage}`
                    : isIdle
                      ? 'Idle. Run ingestion to populate.'
                      : null
          )}
        </span>
      </div>
    </section>
  )
}
