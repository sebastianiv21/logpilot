import { Outlet } from 'react-router-dom'
import { useCurrentSession } from '../contexts/SessionContext'

export function AppLayout() {
  const { currentSessionId } = useCurrentSession()

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 bg-base-200 flex flex-col border-r border-base-300">
        <div className="p-4 border-b border-base-300">
          <h2 className="font-semibold text-base">Sessions</h2>
          <p className="text-sm text-base-content/70 mt-1" aria-live="polite">
            {currentSessionId
              ? `Current: ${currentSessionId.slice(0, 8)}…`
              : 'No session selected'}
          </p>
        </div>
        <nav className="flex-1 p-2" aria-label="Session and app navigation">
          {/* Session list will be rendered here by Phase 3 (SessionList) */}
          <div className="text-sm text-base-content/60">
            Session list area
          </div>
        </nav>
      </aside>
      <main className="flex-1 flex flex-col min-w-0">
        <div className="p-4 flex-1">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
