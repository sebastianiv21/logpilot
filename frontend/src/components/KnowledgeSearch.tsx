/**
 * KnowledgeSearch: search input, run query, display chunks (content, source_path, metadata).
 * When knowledge base is empty or ingest not run, show clear message (FR-007).
 */

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

  const form = useForm<KnowledgeSearchFormValues>({
    resolver: zodResolver(KnowledgeSearchFormSchema),
    defaultValues: { query: '', limit: 10 },
  })

  const hasIngestRun =
    ingestStatus?.last_result != null || (ingestStatus?.error != null && ingestStatus?.status === 'idle')
  const chunks = searchMutation.data?.chunks ?? []
  const hasSearched = searchMutation.isSuccess
  const isEmptyResult = hasSearched && chunks.length === 0

  const onSubmit = form.handleSubmit((values) => {
    const limit = typeof values.limit === 'number' && Number.isFinite(values.limit)
      ? values.limit
      : 10
    searchMutation.mutate({
      query: values.query.trim(),
      limit,
    })
  })

  return (
    <section className="space-y-4" aria-labelledby="knowledge-search-heading">
      <h2 id="knowledge-search-heading" className="text-xl font-semibold flex items-center gap-2">
        <Search size={18} aria-hidden />
        Search knowledge base
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
        <div className="form-control w-24">
          <label htmlFor="knowledge-limit" className="label">
            <span className="label-text">Limit</span>
          </label>
          <input
            id="knowledge-limit"
            type="number"
            min={1}
            max={100}
            className="input input-bordered w-full"
            {...form.register('limit', { valueAsNumber: true })}
            aria-label="Maximum number of search results"
          />
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
          <span>{searchMutation.error?.message ?? 'Search failed'}</span>
        </div>
      )}

      {/* T033: empty state when no ingest run or no knowledge available */}
      {!hasIngestRun && !hasSearched && (
        <p className="text-base-content/70 text-sm">
          Run ingestion first to populate the knowledge base, then search here.
        </p>
      )}
      {!hasIngestRun && hasSearched && isEmptyResult && (
        <p className="text-base-content/70 text-sm">
          No knowledge available. Run ingestion first to index documentation and code.
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
          </h3>
          <ul className="space-y-2 list-none p-0 m-0">
            {chunks.map((chunk, i) => (
              <li key={i}>
                <ChunkCard chunk={chunk} />
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  )
}
