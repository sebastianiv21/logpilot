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
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">LogPilot</h1>
        <p className="mt-2 text-base-content/80">
          {currentSessionId
            ? 'Upload logs or switch session in the sidebar.'
            : 'Select or create a session to get started.'}
        </p>
      </div>
      {currentSessionId && <UploadLogs />}
      {currentSessionId && (
        <section className="space-y-2 mt-8 border-t border-base-300 pt-6" aria-labelledby="logs-metrics-heading">
          <h2 id="logs-metrics-heading" className="text-xl font-semibold">
            Logs &amp; metrics
          </h2>
          <p className="text-base-content/80 text-sm">
            Search logs and open metrics in Grafana.
          </p>
          <MetricsLink />
        </section>
      )}
      {currentSessionId && (
        <section className="space-y-6 mt-8 border-t border-base-300 pt-6" aria-labelledby="reports-heading">
          <h2 id="reports-heading" className="text-xl font-semibold">
            Reports
          </h2>
          <ReportGenerate />
          <ReportList />
        </section>
      )}
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
