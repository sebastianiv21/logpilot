import { Copy, ExternalLink } from 'lucide-react'
import type { Session } from '../lib/schemas'

export interface SessionTitleRowProps {
  sessionTitle: string | null
  currentSession: Session | null
  onCopySessionId: () => void
}

export function SessionTitleRow({
  sessionTitle,
  currentSession,
  onCopySessionId,
}: SessionTitleRowProps) {
  const externalLinkUrl = currentSession?.external_link?.trim() ?? ''
  const hasExternalLink = externalLinkUrl.length > 0

  if (!sessionTitle) return null

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between gap-2 min-w-0">
        <h1 className="text-2xl font-semibold truncate min-w-0 flex-1" title={sessionTitle}>
          {sessionTitle}
        </h1>
        {currentSession &&
          (hasExternalLink ? (
            <a
              href={externalLinkUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-ghost btn-sm gap-1.5 shrink-0"
              aria-label="Open session's external link"
            >
              <ExternalLink size={16} aria-hidden />
              <span>External link</span>
            </a>
          ) : (
            <span
              className="tooltip tooltip-left btn btn-sm gap-1.5 shrink-0 cursor-not-allowed before:text-sm before:font-medium bg-base-200 border border-base-300 text-base-content/70"
              data-tip="No external link provided"
              aria-label="External link — no link provided"
              tabIndex={0}
            >
              <ExternalLink size={16} aria-hidden />
              <span>External link</span>
            </span>
          ))}
      </div>
      {currentSession && (
        <div className="flex items-center gap-1.5 flex-wrap text-sm text-base-content/70">
          <span className="shrink-0">Session ID:</span>
          <span className="flex items-center gap-1 min-w-0 max-w-full">
            <code className="truncate font-mono text-xs" title={currentSession.id}>
              {currentSession.id}
            </code>
            <button
              type="button"
              className="btn btn-ghost btn-xs btn-square shrink-0"
              onClick={onCopySessionId}
              aria-label="Copy session ID"
            >
              <Copy size={14} aria-hidden />
            </button>
          </span>
        </div>
      )}
    </div>
  )
}
