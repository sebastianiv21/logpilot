import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { Toaster } from 'sonner'
import { AppLayout } from './components/AppLayout'
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
