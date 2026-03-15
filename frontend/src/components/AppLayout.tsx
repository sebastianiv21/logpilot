import { useState, useRef } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { FolderOpen, Pencil } from 'lucide-react'
import { useCurrentSession } from '../contexts/SessionContext'
import type { Session } from '../lib/schemas'
import { useFocusTrap } from '../hooks/useFocusTrap'
import { SessionList } from './SessionList'
import { CreateSessionForm } from './CreateSessionForm'
import { EditSessionForm } from './EditSessionForm'
import { HeaderKbLink } from './HeaderKbLink'
import { ThemeSwitcher } from './ThemeSwitcher'

export function AppLayout() {
  const { currentSessionId } = useCurrentSession()
  const location = useLocation()
  const [editingSession, setEditingSession] = useState<Session | null>(null)
  const editModalRef = useRef<HTMLDivElement>(null)
  useFocusTrap(!!editingSession, editModalRef)
  const isKnowledgePage = location.pathname === '/knowledge'

  return (
    <div className="flex flex-col min-h-screen">
      <a
        href="#main-content"
        className="sr-only focus:fixed focus:top-4 focus:left-4 focus:z-[100] focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-content focus:rounded-lg focus:outline-none focus:w-auto focus:h-auto focus:m-0 focus:overflow-visible focus:[clip:auto]"
      >
        Skip to main content
      </a>
      <nav
        className="w-full flex items-center justify-between gap-2 px-4 py-2 border-b border-base-300 bg-base-200/50 shrink-0"
        aria-label="Main navigation"
      >
        <div className="flex items-center gap-2 min-w-0">
          <span className="font-semibold text-lg truncate" aria-hidden="true">LogPilot</span>
          {!isKnowledgePage && <span className="flex-1" aria-hidden="true" />}
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <HeaderKbLink />
          <ThemeSwitcher />
        </div>
      </nav>
      <div className="flex flex-1 min-h-0">
        {!isKnowledgePage && (
          <aside className="w-64 bg-base-200 flex flex-col border-r border-base-300 shrink-0">
            <div className="p-4 border-b border-base-300">
              <h2 className="font-semibold text-base flex items-center gap-2">
                <FolderOpen size={18} aria-hidden />
                Sessions
              </h2>
              <p className="text-sm text-base-content/70 mt-1" aria-live="polite">
                {currentSessionId
                  ? `Current: ${currentSessionId.slice(0, 8)}…`
                  : 'No session selected'}
              </p>
            </div>
            <nav className="flex-1 overflow-auto flex flex-col p-2" aria-label="Session and app navigation">
              <div className="mb-3">
                <CreateSessionForm />
              </div>
              <SessionList onEditSession={setEditingSession} />
            </nav>
          </aside>
        )}
        <main id="main-content" className="flex-1 flex flex-col min-w-0 overflow-auto" tabIndex={-1}>
          <div className="p-4 flex-1">
            <Outlet />
          </div>
        </main>
      </div>

      {editingSession && (
        <dialog open className="modal modal-open" id="edit-session-modal" aria-modal="true" aria-labelledby="edit-session-title">
          <div className="modal-box" ref={editModalRef} role="document">
            <h3 id="edit-session-title" className="font-semibold text-lg flex items-center gap-2">
              <Pencil size={18} aria-hidden />
              Edit session
            </h3>
            <EditSessionForm
              session={editingSession}
              onSuccess={() => setEditingSession(null)}
              onCancel={() => setEditingSession(null)}
            />
          </div>
          <form method="dialog" className="modal-backdrop" onSubmit={() => setEditingSession(null)}>
            <button type="submit" aria-label="Close edit session dialog">close</button>
          </form>
        </dialog>
      )}
    </div>
  )
}
