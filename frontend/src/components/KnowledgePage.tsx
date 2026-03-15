/**
 * KnowledgePage: dedicated route for knowledge base (ingestion + search).
 * Grouped under a single "Knowledge base" heading per spec.
 * Back to Home is in content only (not in top nav) per US3.
 */

import { Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { KnowledgeIngest } from './KnowledgeIngest'
import { KnowledgeSearch } from './KnowledgeSearch'

export function KnowledgePage() {
  return (
    <div className="space-y-6">
      <p className="flex items-center gap-2">
        <Link
          to="/"
          className="link link-hover text-sm font-medium inline-flex items-center gap-1"
          aria-label="Back to home"
        >
          <ArrowLeft size={16} aria-hidden />
          Back to home
        </Link>
      </p>
      <section
        className="space-y-6 rounded-lg border border-base-300 bg-base-200/40 p-6"
        aria-labelledby="knowledge-base-heading"
        aria-describedby="knowledge-base-desc"
      >
        <h1 id="knowledge-base-heading" className="text-2xl font-semibold">
          Knowledge base
        </h1>
        <p id="knowledge-base-desc" className="text-base-content/80 text-sm">
          Add docs and code to the knowledge base for reports and search. Then search across ingested content.
        </p>
        <div className="space-y-6 pt-2">
          <KnowledgeIngest />
          <KnowledgeSearch />
        </div>
      </section>
    </div>
  )
}
