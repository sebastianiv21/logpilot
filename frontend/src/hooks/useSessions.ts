/**
 * TanStack Query hooks for sessions API.
 * useQuery for list/get, useMutation for create/update; cache invalidation on mutations.
 */

import {
  useQuery,
  useMutation,
  useQueryClient,
  type UseQueryResult,
  type UseMutationResult,
} from '@tanstack/react-query';
import {
  getSessions,
  getSession,
  createSession,
  patchSession,
  type CreateSessionBody,
  type PatchSessionBody,
} from '../services/api';
import type { Session } from '../lib/schemas';

const sessionsKey = ['sessions'] as const;
const sessionKey = (id: string) => ['sessions', id] as const;

export function useSessionsList(): UseQueryResult<{ sessions: Session[] }> {
  return useQuery({
    queryKey: sessionsKey,
    queryFn: getSessions,
  });
}

export function useSession(id: string | null): UseQueryResult<Session> {
  return useQuery({
    queryKey: sessionKey(id ?? ''),
    queryFn: () => getSession(id!),
    enabled: !!id,
  });
}

export function useCreateSession(): UseMutationResult<
  Session,
  Error,
  CreateSessionBody | undefined
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body?: CreateSessionBody) => createSession(body ?? {}),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: sessionsKey });
    },
  });
}

export function usePatchSession(): UseMutationResult<
  Session,
  Error,
  { id: string; body: PatchSessionBody }
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: PatchSessionBody }) =>
      patchSession(id, body),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: sessionsKey });
      queryClient.invalidateQueries({ queryKey: sessionKey(data.id) });
    },
  });
}
