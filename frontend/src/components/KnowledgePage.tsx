/**
 * KnowledgePage: dedicated route for knowledge base (ingestion + search).
 * Grouped under a single "Knowledge base" heading per spec.
 */

import { KnowledgeIngest } from './KnowledgeIngest'
import { KnowledgeSearch } from './KnowledgeSearch'

export function KnowledgePage() {
  return (
    <div className="space-y-6">
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
