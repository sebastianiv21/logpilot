import './style.css'
import { themeChange } from 'theme-change'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { SessionProvider } from './contexts/SessionContext.tsx'
import { ReportGenerationProvider } from './contexts/ReportGenerationContext.tsx'
import App from './App.tsx'

themeChange(false)

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30 * 1000,
      retry: 1,
    },
  },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <SessionProvider>
        <ReportGenerationProvider>
          <App />
        </ReportGenerationProvider>
      </SessionProvider>
    </QueryClientProvider>
  </StrictMode>,
)
