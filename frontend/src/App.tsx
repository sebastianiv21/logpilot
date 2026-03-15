import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { Toaster } from 'sonner'
import { AppLayout } from './components/AppLayout'
import { KnowledgeIngest } from './components/KnowledgeIngest'
import { KnowledgeSearch } from './components/KnowledgeSearch'
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
            ? 'Upload logs or use the session list to switch.'
            : 'Select a session or create one to get started.'}
        </p>
      </div>
      {currentSessionId && <UploadLogs />}
      {currentSessionId && (
        <section className="space-y-2" aria-labelledby="logs-metrics-heading">
          <h2 id="logs-metrics-heading" className="text-xl font-semibold">
            Logs &amp; metrics
          </h2>
          <p className="text-base-content/80 text-sm">
            View and search logs and metrics in Grafana for this session.
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
      <section className="space-y-6 mt-8 border-t border-base-300 pt-6">
        <KnowledgeIngest />
        <KnowledgeSearch />
      </section>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
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
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
