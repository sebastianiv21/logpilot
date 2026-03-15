import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { Toaster } from 'sonner'
import { AppLayout } from './components/AppLayout'
import { ConnectionBanner } from './components/ConnectionBanner'
import { KnowledgePage } from './components/KnowledgePage'
import { MetricsLink } from './components/MetricsLink'
import { ReportGenerate } from './components/ReportGenerate'
import { ReportList } from './components/ReportList'
import { UploadLogs } from './components/UploadLogs'
import { useCurrentSession } from './contexts/SessionContext'

function HomePage() {
  const { currentSessionId } = useCurrentSession()
  if (!currentSessionId) {
    return (
      <div className="space-y-6">
        <p className="text-base-content/80">
          Select or create a session to get started.
        </p>
      </div>
    )
  }
  return (
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
  )
}

function App() {
  return (
    <BrowserRouter>
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
    </BrowserRouter>
  )
}

export default App
