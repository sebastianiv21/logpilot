import { useState, useRef } from 'react'
import { Link, Outlet, useLocation } from 'react-router-dom'
import { FolderOpen, Pencil, ScrollText, Search } from 'lucide-react'
import type { Session } from '../lib/schemas'
import { useFocusTrap } from '../hooks/useFocusTrap'
import { useDebouncedValue } from '../hooks/useDebouncedValue'
import { SessionList } from './SessionList'
import { CreateSessionForm } from './CreateSessionForm'
import { EditSessionForm } from './EditSessionForm'
import { HeaderKbLink } from './HeaderKbLink'
import { ThemeSwitcher } from './ThemeSwitcher'

const SEARCH_DEBOUNCE_MS = 200

export function AppLayout() {
  const location = useLocation()
  const [editingSession, setEditingSession] = useState<Session | null>(null)
  const [sessionSearchRaw, setSessionSearchRaw] = useState('')
  const sessionSearchDebounced = useDebouncedValue(
    sessionSearchRaw.trim(),
    SEARCH_DEBOUNCE_MS
  )
  const editModalRef = useRef<HTMLDivElement>(null)
  useFocusTrap(!!editingSession, editModalRef)
  const isKnowledgePage = location.pathname === '/knowledge'

  return (
    <div className="flex flex-col h-screen overflow-hidden">
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
          <Link
            to="/"
            className="font-semibold text-lg truncate flex items-center gap-2 hover:opacity-90 min-w-0"
            aria-label="LogPilot home"
          >
            <ScrollText size={20} aria-hidden />
            <span className="truncate">LogPilot</span>
          </Link>
          {!isKnowledgePage && <span className="flex-1" aria-hidden="true" />}
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <HeaderKbLink />
          <ThemeSwitcher />
        </div>
      </nav>
      <div className="flex flex-1 min-h-0">
        {!isKnowledgePage && (
          <aside
            className="w-64 bg-base-200 flex flex-col border-r border-base-300 shrink-0 min-h-0"
            aria-label="Session and app navigation"
          >
            <div className="p-4 border-b border-base-300 shrink-0">
              <h2 className="font-semibold text-base flex items-center gap-2">
                <FolderOpen size={18} aria-hidden />
                Sessions
              </h2>
            </div>
            <div className="shrink-0 p-2">
              <CreateSessionForm />
            </div>
            <div className="shrink-0 p-2">
              <div className="group flex items-center gap-2 rounded-lg border border-base-300 bg-base-100 focus-within:outline focus-within:outline-2 focus-within:outline-offset-2 focus-within:outline-primary min-h-8">
                <Search
                  size={16}
                  className="shrink-0 ml-2.5 text-base-content/50"
                  aria-hidden
                />
                <input
                  type="search"
                  value={sessionSearchRaw}
                  onChange={(e) => setSessionSearchRaw(e.target.value)}
                  placeholder="Search sessions…"
                  className="border-0 bg-transparent focus:outline-none focus:ring-0 flex-1 min-w-0 py-1.5 pr-2 text-sm"
                  aria-label="Search sessions by name, ID, or link"
                />
              </div>
            </div>
            <div className="flex-1 min-h-0 overflow-y-auto p-2">
              <SessionList
                onEditSession={setEditingSession}
                searchQuery={sessionSearchDebounced}
              />
            </div>
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
