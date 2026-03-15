/**
 * KnowledgeSearch: search input, run query, display chunks (content, source_path, metadata).
 * When knowledge base is empty or ingest not run, show clear message (FR-007).
 * Results are paginated: fixed batch size 10, Load more and Previous (hidden when 0 or 1 page).
 */

import { useEffect, useMemo, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Search } from 'lucide-react'
import { useKnowledgeIngestStatus } from '../hooks/useKnowledgeIngest'
import { useKnowledgeSearch } from '../hooks/useKnowledgeSearch'
import {
  KnowledgeSearchFormSchema,
  type KnowledgeSearchFormValues,
} from '../lib/schemas'
import type { KnowledgeSearchChunk } from '../lib/schemas'

const KB_SEARCH_BATCH_SIZE = 10

function ChunkCard({ chunk }: { chunk: KnowledgeSearchChunk }) {
  return (
    <div className="card bg-base-200 border border-base-300 overflow-hidden">
      <div className="card-body p-3">
        <p className="text-sm whitespace-pre-wrap break-words">{chunk.content}</p>
        <p className="text-xs text-base-content/60 mt-1 font-mono">
          {chunk.source_path}
        </p>
        {chunk.metadata && Object.keys(chunk.metadata).length > 0 && (
          <pre className="text-xs text-base-content/50 mt-1 overflow-x-auto">
            {JSON.stringify(chunk.metadata)}
          </pre>
        )}
      </div>
    </div>
  )
}

export function KnowledgeSearch() {
  const { data: ingestStatus } = useKnowledgeIngestStatus()
  const searchMutation = useKnowledgeSearch()
  const [visibleCount, setVisibleCount] = useState(KB_SEARCH_BATCH_SIZE)

  const form = useForm<KnowledgeSearchFormValues>({
    resolver: zodResolver(KnowledgeSearchFormSchema),
    defaultValues: { query: '' },
  })

  const hasIngestRun =
    ingestStatus?.last_result != null || (ingestStatus?.error != null && ingestStatus?.status === 'idle')
  const chunks = searchMutation.data?.chunks ?? []
  const hasSearched = searchMutation.isSuccess
  const isEmptyResult = hasSearched && chunks.length === 0

  const visibleChunks = useMemo(
    () => chunks.slice(0, visibleCount),
    [chunks, visibleCount]
  )
  const hasMore = visibleCount < chunks.length
  const hasPrevious = visibleCount > KB_SEARCH_BATCH_SIZE
  const isSinglePage = chunks.length <= KB_SEARCH_BATCH_SIZE
  const showPaginationControls = chunks.length > 0 && !isSinglePage

  useEffect(() => {
    if (searchMutation.data?.chunks) {
      setVisibleCount(KB_SEARCH_BATCH_SIZE)
    }
  }, [searchMutation.data])

  const onSubmit = form.handleSubmit((values) => {
    searchMutation.mutate({
      query: values.query.trim(),
      limit: 50,
    })
  })

  const handleLoadMore = () => {
    setVisibleCount((c) => Math.min(c + KB_SEARCH_BATCH_SIZE, chunks.length))
  }
  const handlePrevious = () => {
    setVisibleCount((c) => Math.max(KB_SEARCH_BATCH_SIZE, c - KB_SEARCH_BATCH_SIZE))
  }

  return (
    <section className="space-y-4" aria-labelledby="knowledge-search-heading">
      <h2 id="knowledge-search-heading" className="text-xl font-semibold flex items-center gap-2">
        <Search size={18} aria-hidden />
        Search
      </h2>
      <form onSubmit={onSubmit} className="flex flex-wrap items-end gap-3">
        <div className="form-control flex-1 min-w-[200px]">
          <label htmlFor="knowledge-query" className="label">
            <span className="label-text">Query</span>
          </label>
          <input
            id="knowledge-query"
            type="text"
            className="input input-bordered w-full"
            placeholder="e.g. authentication flow"
            {...form.register('query')}
            aria-invalid={!!form.formState.errors.query}
            aria-label="Search query for knowledge base"
          />
          {form.formState.errors.query && (
            <p className="text-error text-sm mt-1" role="alert">
              {form.formState.errors.query.message}
            </p>
          )}
        </div>
        <button
          type="submit"
          className="btn btn-primary flex items-center gap-2"
          disabled={searchMutation.isPending}
          aria-busy={searchMutation.isPending}
          aria-label="Search knowledge base"
        >
          {searchMutation.isPending ? (
            <span className="loading loading-spinner loading-sm" aria-hidden />
          ) : (
            <Search size={18} aria-hidden />
          )}
          {searchMutation.isPending ? 'Searching…' : 'Search'}
        </button>
      </form>

      {searchMutation.isError && (
        <div className="alert alert-error" role="alert">
          <span>{searchMutation.error?.message ?? 'Couldn\'t search'}</span>
        </div>
      )}

      {/* T033: empty state when no ingest run or no knowledge available */}
      {!hasIngestRun && !hasSearched && (
        <p className="text-base-content/70 text-sm">
          Run ingestion first, then search.
        </p>
      )}
      {!hasIngestRun && hasSearched && isEmptyResult && (
        <p className="text-base-content/70 text-sm">
          No knowledge yet. Run ingestion first.
        </p>
      )}
      {hasIngestRun && hasSearched && isEmptyResult && (
        <p className="text-base-content/70 text-sm">
          No results match your query. Try different keywords.
        </p>
      )}

      {chunks.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-base-content/80">
            {chunks.length} result{chunks.length !== 1 ? 's' : ''}
            {showPaginationControls && (
              <span className="font-normal text-base-content/60 ml-1">
                (showing {visibleChunks.length})
              </span>
            )}
          </h3>
          <ul className="space-y-2 list-none p-0 m-0" aria-label="Search results">
            {visibleChunks.map((chunk, i) => (
              <li key={i}>
                <ChunkCard chunk={chunk} />
              </li>
            ))}
          </ul>
          {showPaginationControls && (
            <div
              className="flex flex-wrap gap-2 pt-2"
              role="group"
              aria-label="Search results pagination"
            >
              {hasPrevious && (
                <button
                  type="button"
                  className="btn btn-ghost btn-sm"
                  onClick={handlePrevious}
                  aria-label="Previous page of results"
                >
                  Previous
                </button>
              )}
              {hasMore && (
                <button
                  type="button"
                  className="btn btn-ghost btn-sm"
                  onClick={handleLoadMore}
                  aria-label="Load more results"
                >
                  Load more
                </button>
              )}
            </div>
          )}
        </div>
      )}
    </section>
  )
}
