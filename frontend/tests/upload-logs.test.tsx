import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { UploadLogs } from '../src/components/UploadLogs'

const mocks = vi.hoisted(() => ({
  toastSuccess: vi.fn(),
  toastError: vi.fn(),
  getUploadSummaryMock: vi.fn(),
  uploadLogsMock: vi.fn(),
}))

let currentSessionId = 'session-1'

vi.mock('sonner', () => ({
  toast: {
    success: mocks.toastSuccess,
    error: mocks.toastError,
  },
}))

vi.mock('../src/services/api', async () => {
  const actual = await vi.importActual<typeof import('../src/services/api')>('../src/services/api')
  return {
    ...actual,
    getUploadSummary: mocks.getUploadSummaryMock,
    uploadLogs: mocks.uploadLogsMock,
  }
})

vi.mock('../src/contexts/SessionContext', () => ({
  useCurrentSession: () => ({
    currentSessionId,
    markSessionHasLogs: vi.fn(),
    lastUploadResultBySessionId: {},
    setLastUploadResult: vi.fn(),
  }),
}))

function renderUploadLogs() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <UploadLogs />
    </QueryClientProvider>
  )
}

describe('UploadLogs', () => {
  beforeEach(() => {
    currentSessionId = 'session-1'
    mocks.toastSuccess.mockReset()
    mocks.toastError.mockReset()
    mocks.getUploadSummaryMock.mockReset()
    mocks.uploadLogsMock.mockReset()
    mocks.getUploadSummaryMock.mockResolvedValue(null)
  })

  it('clears the selected file after a successful upload', async () => {
    mocks.uploadLogsMock.mockResolvedValue({
      session_id: 'session-1',
      status: 'success',
      uploaded_file_name: 'logs.zip',
      files_processed: 1,
      files_skipped: 0,
      error: null,
      updated_at: '2026-04-03T10:00:00Z',
    })

    renderUploadLogs()

    const fileInput = screen.getByLabelText(/choose \.zip log archive/i) as HTMLInputElement
    const file = new File(['test'], 'logs.zip', { type: 'application/zip' })

    fireEvent.change(fileInput, { target: { files: [file] } })
    expect(fileInput.files?.[0]).toBe(file)

    fireEvent.click(screen.getByRole('button', { name: /upload log archive/i }))

    await waitFor(() => {
      expect(mocks.uploadLogsMock).toHaveBeenCalledWith('session-1', file)
    })

    await waitFor(() => {
      expect(fileInput.value).toBe('')
    })
  })

  it('clears the selected file when the active session changes', async () => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    })
    const { rerender } = render(
      <QueryClientProvider client={queryClient}>
        <UploadLogs />
      </QueryClientProvider>
    )

    const fileInput = screen.getByLabelText(/choose \.zip log archive/i) as HTMLInputElement
    const file = new File(['test'], 'logs.zip', { type: 'application/zip' })

    fireEvent.change(fileInput, { target: { files: [file] } })
    expect(fileInput.files?.[0]).toBe(file)

    currentSessionId = 'session-2'

    rerender(
      <QueryClientProvider client={queryClient}>
        <UploadLogs />
      </QueryClientProvider>
    )

    await waitFor(() => {
      expect(
        (screen.getByLabelText(/choose \.zip log archive/i) as HTMLInputElement).value
      ).toBe('')
    })
  })

  it('blocks uploads when the session already has logs', async () => {
    mocks.getUploadSummaryMock.mockResolvedValue({
      session_id: 'session-1',
      status: 'success',
      uploaded_file_name: 'existing.zip',
      files_processed: 1,
      files_skipped: 0,
      error: null,
      updated_at: '2026-04-03T10:00:00Z',
    })

    renderUploadLogs()

    await waitFor(() => {
      expect(screen.getByText(/this session already has logs/i)).toBeInTheDocument()
    })

    expect(screen.getByLabelText(/choose \.zip log archive/i)).toBeDisabled()
    expect(screen.getByRole('button', { name: /upload log archive/i })).toBeDisabled()
    expect(mocks.uploadLogsMock).not.toHaveBeenCalled()
  })
})
