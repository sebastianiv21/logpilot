import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { SessionList } from '../src/components/SessionList'

const mocks = vi.hoisted(() => ({
  useSessionsListMock: vi.fn(),
  mutateMock: vi.fn(),
  setCurrentSessionIdMock: vi.fn(),
}))

vi.mock('../src/hooks/useSessions', () => ({
  useSessionsList: mocks.useSessionsListMock,
  usePatchSession: () => ({
    mutate: mocks.mutateMock,
    isPending: false,
  }),
}))

vi.mock('../src/contexts/SessionContext', () => ({
  useCurrentSession: () => ({
    currentSessionId: 'deleted-session',
    setCurrentSessionId: mocks.setCurrentSessionIdMock,
  }),
}))

describe('SessionList', () => {
  beforeEach(() => {
    mocks.useSessionsListMock.mockReset()
    mocks.mutateMock.mockReset()
    mocks.setCurrentSessionIdMock.mockReset()
  })

  it('renders the pin action and pinned indicator', async () => {
    mocks.useSessionsListMock.mockReturnValue({
      data: {
        sessions: [
          {
            id: 'session-1',
            name: 'Pinned session',
            external_link: null,
            is_pinned: true,
            created_at: '2026-04-03T10:00:00Z',
            updated_at: '2026-04-03T10:00:00Z',
          },
        ],
      },
      isLoading: false,
      isError: false,
      error: null,
    })

    render(<SessionList onEditSession={vi.fn()} />)

    expect(screen.getByLabelText(/pinned session/i)).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /unpin session/i }))

    expect(mocks.mutateMock).toHaveBeenCalledWith({
      id: 'session-1',
      body: { is_pinned: false },
    })
  })

  it('clears the current session when it no longer exists', async () => {
    mocks.useSessionsListMock.mockReturnValue({
      data: { sessions: [] },
      isLoading: false,
      isError: false,
      error: null,
    })

    render(<SessionList onEditSession={vi.fn()} />)

    await waitFor(() => {
      expect(mocks.setCurrentSessionIdMock).toHaveBeenCalledWith(null)
    })
  })
})
