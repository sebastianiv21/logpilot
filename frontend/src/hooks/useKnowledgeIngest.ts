/**
 * useKnowledgeIngest: trigger ingest mutation, poll GET /knowledge/ingest/status until idle,
 * show success/error via Sonner (FR-007).
 */

import {
  useQuery,
  useMutation,
  useQueryClient,
  type UseQueryResult,
  type UseMutationResult,
} from '@tanstack/react-query';
import { useEffect, useRef } from 'react';
import { toast } from 'sonner';
import {
  getKnowledgeIngestStatus,
  startKnowledgeIngest,
  type KnowledgeIngestBody,
} from '../services/api';
import type { KnowledgeIngestStatus } from '../lib/schemas';

const knowledgeIngestStatusKey = ['knowledge', 'ingest', 'status'] as const;

export function useKnowledgeIngestStatus(): UseQueryResult<KnowledgeIngestStatus> {
  return useQuery({
    queryKey: knowledgeIngestStatusKey,
    queryFn: getKnowledgeIngestStatus,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === 'running' ? 2000 : false;
    },
  });
}

export function useKnowledgeIngestStart(): UseMutationResult<
  { message: string },
  Error,
  KnowledgeIngestBody | undefined
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body?: KnowledgeIngestBody) => startKnowledgeIngest(body ?? {}),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: knowledgeIngestStatusKey });
    },
  });
}

/** Hook that combines status (with polling) and start mutation, and toasts on completion (FR-007). */
export function useKnowledgeIngest(): {
  statusQuery: UseQueryResult<KnowledgeIngestStatus>;
  startMutation: UseMutationResult<
    { message: string },
    Error,
    KnowledgeIngestBody | undefined
  >;
} {
  const statusQuery = useKnowledgeIngestStatus();
  const startMutation = useKnowledgeIngestStart();
  const prevStatusRef = useRef<'running' | 'idle' | undefined>(undefined);

  useEffect(() => {
    const status = statusQuery.data?.status;
    if (status === 'idle' && prevStatusRef.current === 'running') {
      const err = statusQuery.data?.error;
      if (err) {
        toast.error('Ingest failed', { description: err });
      } else {
        const last = statusQuery.data?.last_result;
        if (last) {
          toast.success('Ingest complete', {
            description: `${last.chunks_ingested ?? 0} chunks, ${last.files_processed ?? 0} files`,
          });
        }
      }
    }
    prevStatusRef.current = status;
  }, [statusQuery.data?.status, statusQuery.data?.error, statusQuery.data?.last_result]);

  return { statusQuery, startMutation };
}
