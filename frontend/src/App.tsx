import { useCallback, useMemo, useState } from 'react'
import { BrowserRouter, Route, Routes, useNavigate } from 'react-router-dom'
import { Toaster, toast } from 'sonner'
import { Copy } from 'lucide-react'
import { AppLayout } from './components/AppLayout'
import { ConnectionBanner } from './components/ConnectionBanner'
import { KnowledgePage } from './components/KnowledgePage'
import { MetricsLink } from './components/MetricsLink'
import { ReportGenerate } from './components/ReportGenerate'
import { ReportList } from './components/ReportList'
import { UploadLogs } from './components/UploadLogs'
import { ReportGenerationProvider } from './contexts/ReportGenerationContext'
import { ReportToOpenContext } from './contexts/ReportToOpenContext'
import { useCurrentSession } from './contexts/SessionContext'
import { useSessionsList } from './hooks/useSessions'

function HomePage() {
  const { data } = useSessionsList()
  const { currentSessionId } = useCurrentSession()

  const currentSession = useMemo(() => {
    const sessions = data?.sessions ?? []
    return currentSessionId ? sessions.find((s) => s.id === currentSessionId) ?? null : null
  }, [data?.sessions, currentSessionId])

  const sessionTitle = useMemo(() => {
    if (!currentSession) return null
    return currentSession.name ?? `Session ${currentSession.id.slice(0, 8)}`
  }, [currentSession])

  const copySessionId = useCallback(async () => {
    if (!currentSession?.id) return
    try {
      await navigator.clipboard.writeText(currentSession.id)
      toast.success('Session ID copied')
    } catch {
      toast.error('Copy failed')
    }
  }, [currentSession])

  return (
    <div className="space-y-6">
      {sessionTitle && (
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold truncate" title={sessionTitle}>
            {sessionTitle}
          </h1>
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
                  onClick={copySessionId}
                  aria-label="Copy session ID"
                >
                  <Copy size={14} aria-hidden />
                </button>
              </span>
            </div>
          )}
        </div>
      )}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8">
        <div className="min-w-0">
          <UploadLogs />
        </div>
      <div className="flex flex-col gap-6 min-w-0">
        <section className="space-y-2 border-t border-base-300 pt-6 lg:border-t-0 lg:pt-0" aria-labelledby="logs-metrics-heading">
          <h2 id="logs-metrics-heading" className="text-xl font-semibold">
            Logs &amp; metrics
          </h2>
          <p className="text-base-content/80 text-sm">
            Search logs and open metrics in Grafana.
          </p>
          <MetricsLink />
        </section>
        <section className="space-y-6 border-t border-base-300 pt-6" aria-labelledby="reports-heading">
          <h2 id="reports-heading" className="text-xl font-semibold">
            Reports
          </h2>
          <ReportGenerate />
          <ReportList />
        </section>
      </div>
      </div>
    </div>
  )
}

function ReportToOpenProviderWithNav({
  children,
}: {
  children: React.ReactNode
}) {
  const [reportToOpen, setReportToOpen] = useState<{
    sessionId: string
    reportId: string
  } | null>(null)
  const navigate = useNavigate()
  const { setCurrentSessionId } = useCurrentSession()
  const openReport = useCallback(
    (sessionId: string, reportId: string) => {
      setCurrentSessionId(sessionId)
      setReportToOpen({ sessionId, reportId })
      navigate('/')
    },
    [navigate, setCurrentSessionId]
  )
  const clearReportToOpen = useCallback(() => setReportToOpen(null), [])
  return (
    <ReportToOpenContext.Provider
      value={{ reportToOpen, openReport, clearReportToOpen }}
    >
      {children}
    </ReportToOpenContext.Provider>
  )
}

function App() {
  return (
    <BrowserRouter>
      <ReportToOpenProviderWithNav>
        <ReportGenerationProvider>
          <ConnectionBanner />
          <Toaster
            toastOptions={{
              unstyled: true,
              classNames: {
                toast: 'alert shadow-lg',
                success: 'alert-success',
                error: 'alert-error',
                info: 'alert-info',
              },
            }}
          />
          <Routes>
            <Route element={<AppLayout />}>
              <Route path="/" element={<HomePage />} />
              <Route path="/knowledge" element={<KnowledgePage />} />
            </Route>
          </Routes>
        </ReportGenerationProvider>
      </ReportToOpenProviderWithNav>
    </BrowserRouter>
  )
}

export default App
