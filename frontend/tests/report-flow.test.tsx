import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ReportList } from '../src/components/ReportList'
import { ReportView } from '../src/components/ReportView'

const mocks = vi.hoisted(() => ({
  toastSuccess: vi.fn(),
  toastError: vi.fn(),
  exportReportMock: vi.fn(),
  downloadBlobMock: vi.fn(),
  useReportMock: vi.fn(),
  useReportsListMock: vi.fn(),
  clearGeneratingMock: vi.fn(),
}))

vi.mock('sonner', () => ({
  toast: {
    success: mocks.toastSuccess,
    error: mocks.toastError,
  },
}))

vi.mock('../src/services/api', () => ({
  ApiError: class ApiError extends Error {
    get userMessage() {
      return this.message
    }
  },
  exportReport: mocks.exportReportMock,
  downloadBlob: mocks.downloadBlobMock,
}))

vi.mock('../src/hooks/useReports', () => ({
  useReport: mocks.useReportMock,
  useReportsList: mocks.useReportsListMock,
}))

vi.mock('../src/contexts/ReportGenerationContext', () => ({
  useReportGeneration: () => ({
    clearGenerating: mocks.clearGeneratingMock,
  }),
}))

vi.mock('../src/contexts/SessionContext', () => ({
  useCurrentSession: () => ({
    currentSessionId: 'session-1',
  }),
}))

vi.mock('../src/contexts/ReportToOpenContext', () => ({
  useReportToOpen: () => ({
    reportToOpen: null,
    clearReportToOpen: vi.fn(),
  }),
}))

vi.mock('../src/hooks/useFocusTrap', () => ({
  useFocusTrap: vi.fn(),
}))

describe('report flow', () => {
  beforeEach(() => {
    mocks.toastSuccess.mockReset()
    mocks.toastError.mockReset()
    mocks.exportReportMock.mockReset()
    mocks.downloadBlobMock.mockReset()
    mocks.useReportMock.mockReset()
    mocks.useReportsListMock.mockReset()
    mocks.clearGeneratingMock.mockReset()

    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
    })
  })

  it('renders report history with question previews and legacy fallback', () => {
    mocks.useReportsListMock.mockReturnValue({
      data: {
        reports: [
          {
            id: 'r1',
            session_id: 'session-1',
            created_at: '2026-03-29T12:34:56Z',
            question_preview: 'Why did checkout requests start timing out after the deploy?',
            has_question: true,
          },
          {
            id: 'r2',
            session_id: 'session-1',
            created_at: '2026-03-28T12:34:56Z',
            question_preview: null,
            has_question: false,
          },
        ],
      },
      isLoading: false,
      error: null,
    })

    render(<ReportList />)

    expect(screen.getByText(/Why did checkout requests start timing out/i)).toBeInTheDocument()
    expect(screen.getByText('No incident question recorded')).toBeInTheDocument()
    expect(screen.queryByText(/Coding agent fix prompt/i)).not.toBeInTheDocument()
  })

  it('shows the full incident question and copies Markdown from the report view', async () => {
    const content = `## Incident Summary\nSummary\n\n## Coding agent fix prompt\nUse evidence.\n`
    mocks.useReportMock.mockReturnValue({
      data: {
        id: 'r1',
        session_id: 'session-1',
        created_at: '2026-03-29T12:34:56Z',
        question: 'Why did checkout requests start timing out after the deploy?',
        content,
      },
      isLoading: false,
      error: null,
    })

    render(<ReportView sessionId="session-1" reportId="r1" />)

    expect(screen.getByText('Incident question')).toBeInTheDocument()
    expect(screen.getByText(/Why did checkout requests start timing out/i)).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /copy report as markdown/i }))

    await waitFor(() => {
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(content)
    })
    expect(mocks.toastSuccess).toHaveBeenCalledWith('Report copied')
  })

  it('shows a clear error when report copy fails', async () => {
    mocks.useReportMock.mockReturnValue({
      data: {
        id: 'r1',
        session_id: 'session-1',
        created_at: '2026-03-29T12:34:56Z',
        question: 'Why did checkout requests start timing out after the deploy?',
        content: '## Incident Summary\nSummary',
      },
      isLoading: false,
      error: null,
    })
    vi.mocked(navigator.clipboard.writeText).mockRejectedValueOnce(new Error('denied'))

    render(<ReportView sessionId="session-1" reportId="r1" />)

    fireEvent.click(screen.getByRole('button', { name: /copy report as markdown/i }))

    await waitFor(() => {
      expect(mocks.toastError).toHaveBeenCalledWith('Copy failed', {
        description: 'Clipboard access is unavailable.',
      })
    })
  })

  it('shows a clear error when PDF export fails', async () => {
    mocks.useReportMock.mockReturnValue({
      data: {
        id: 'r1',
        session_id: 'session-1',
        created_at: '2026-03-29T12:34:56Z',
        question: 'Why did checkout requests start timing out after the deploy?',
        content: '## Incident Summary\nSummary',
      },
      isLoading: false,
      error: null,
    })
    mocks.exportReportMock.mockRejectedValueOnce(
      new Error('PDF export failed. Please try again or use Markdown export.')
    )

    render(<ReportView sessionId="session-1" reportId="r1" />)

    fireEvent.click(screen.getByRole('button', { name: /export report as pdf/i }))

    await waitFor(() => {
      expect(mocks.toastError).toHaveBeenCalledWith('Export failed', {
        description: 'PDF export failed. Please try again or use Markdown export.',
      })
    })
  })
})
