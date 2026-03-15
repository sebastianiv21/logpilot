/**
 * KnowledgeIngest: button to start ingest, display status (running / idle),
 * last result or error message (FR-007).
 */

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
      <h2 id="knowledge-ingest-heading" className="text-xl font-semibold">
        Knowledge base
      </h2>
      <p className="text-base-content/80 text-sm">
        Ingest documentation and code into the knowledge base for report generation and search.
      </p>
      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          className="btn btn-primary"
          onClick={() => startIngest(undefined)}
          disabled={isRunning || starting}
          aria-busy={isRunning || starting}
          aria-describedby="ingest-status"
          aria-label="Start knowledge base ingestion"
        >
          {starting ? 'Starting…' : isRunning ? 'Ingesting…' : 'Start ingestion'}
        </button>
        <span
          id="ingest-status"
          className="text-sm text-base-content/70"
          aria-live="polite"
        >
          {statusLoading && !status
            ? 'Loading status…'
            : statusError
              ? 'Failed to load status'
              : isRunning
                ? 'Ingest in progress (this may take several minutes)'
                : isIdle && lastResult
                  ? `Last run: ${lastResult.chunks_ingested ?? 0} chunks, ${lastResult.files_processed ?? 0} files`
                  : isIdle && errorMessage
                    ? `Last run failed: ${errorMessage}`
                    : isIdle
                      ? 'Idle — run ingestion to populate the knowledge base'
                      : null}
        </span>
      </div>
    </section>
  )
}
