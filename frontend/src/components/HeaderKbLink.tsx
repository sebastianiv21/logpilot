/**
 * HeaderKbLink: navbar control — database icon + status indicator (red / yellow / green).
 * Single click navigates to /knowledge. Tooltip "Knowledge base"; aria-label includes status.
 */

import { Link } from 'react-router-dom'
import { Database } from 'lucide-react'
import { useKnowledgeSourcesStatus } from '../hooks/useKnowledgeIngest'
import type { KnowledgeSourceStatus } from '../lib/schemas'

type IndicatorState = 'red' | 'yellow' | 'green'

function getIndicatorState(sources: KnowledgeSourceStatus[] | undefined): IndicatorState {
  if (sources?.some((source) => source.status === 'running')) return 'yellow'
  if (sources?.some((source) => source.status === 'ready')) return 'green'
  return 'red'
}

function getStatusAriaSuffix(state: IndicatorState): string {
  switch (state) {
    case 'red':
      return 'no data'
    case 'yellow':
      return 'ingesting'
    case 'green':
      return 'ready'
    default:
      return 'no data'
  }
}

export function HeaderKbLink() {
  const { data } = useKnowledgeSourcesStatus()
  const state = getIndicatorState(data?.sources)
  const ariaSuffix = getStatusAriaSuffix(state)

  const dotClasses = [
    'absolute -right-0.5 -bottom-0.5 w-3 h-3 rounded-full border-2 border-base-100',
    state === 'red' && 'bg-error',
    state === 'yellow' && 'bg-warning animate-pulse',
    state === 'green' && 'bg-success',
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <Link
      to="/knowledge"
      className="relative flex items-center justify-center p-2 rounded-lg hover:bg-base-300 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-base-100"
      title="Knowledge base"
      aria-label={`Knowledge base, ${ariaSuffix}`}
    >
      <span className="relative inline-flex">
        <Database size={20} aria-hidden />
        <span
          className={dotClasses}
          aria-hidden
          role="status"
        />
      </span>
    </Link>
  )
}
