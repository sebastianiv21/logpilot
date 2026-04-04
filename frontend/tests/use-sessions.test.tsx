import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { renderHook, waitFor } from '@testing-library/react'
import type { ReactNode } from 'react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useCreateSession } from '../src/hooks/useSessions'
import type { Session } from '../src/lib/schemas'

const mocks = vi.hoisted(() => ({
  createSessionMock: vi.fn(),
  getSessionsMock: vi.fn(),
  getSessionMock: vi.fn(),
  patchSessionMock: vi.fn(),
}))

vi.mock('../src/services/api', () => ({
  createSession: mocks.createSessionMock,
  getSessions: mocks.getSessionsMock,
  getSession: mocks.getSessionMock,
  patchSession: mocks.patchSessionMock,
}))

describe('useCreateSession', () => {
  beforeEach(() => {
    mocks.createSessionMock.mockReset()
    mocks.getSessionsMock.mockReset()
    mocks.getSessionMock.mockReset()
    mocks.patchSessionMock.mockReset()
  })

  it('adds the created session to the sessions cache immediately', async () => {
    const createdSession: Session = {
      id: 'session-new',
      name: 'Fresh session',
      external_link: null,
      is_pinned: false,
      created_at: '2026-04-04T12:00:00Z',
      updated_at: '2026-04-04T12:00:00Z',
    }
    mocks.createSessionMock.mockResolvedValue(createdSession)

    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    })
    queryClient.setQueryData(['sessions'], {
      sessions: [
        {
          id: 'session-old',
          name: 'Older session',
          external_link: null,
          is_pinned: false,
          created_at: '2026-04-03T12:00:00Z',
          updated_at: '2026-04-03T12:00:00Z',
        },
      ],
    })

    const wrapper = ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    )

    const { result } = renderHook(() => useCreateSession(), { wrapper })

    result.current.mutate({ name: 'Fresh session' })

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(queryClient.getQueryData(['sessions'])).toEqual({
      sessions: [
        createdSession,
        {
          id: 'session-old',
          name: 'Older session',
          external_link: null,
          is_pinned: false,
          created_at: '2026-04-03T12:00:00Z',
          updated_at: '2026-04-03T12:00:00Z',
        },
      ],
    })
    expect(queryClient.getQueryData(['sessions', 'session-new'])).toEqual(createdSession)
  })
})
