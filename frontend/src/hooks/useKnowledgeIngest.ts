/**
 * useKnowledgeIngest: trigger ingest mutation, poll per-source status, and toast on completion.
 */

import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseMutationResult,
  type UseQueryResult,
} from '@tanstack/react-query';
import { useEffect, useRef } from 'react';
import { toast } from 'sonner';
import {
  getKnowledgeSourcesStatus,
  startKnowledgeIngest,
  type KnowledgeIngestBody,
} from '../services/api';
import type { KnowledgeSourcesStatus } from '../lib/schemas';

const knowledgeSourcesStatusKey = ['knowledge', 'sources', 'status'] as const;

export function useKnowledgeSourcesStatus(): UseQueryResult<KnowledgeSourcesStatus> {
  return useQuery({
    queryKey: knowledgeSourcesStatusKey,
    queryFn: getKnowledgeSourcesStatus,
    refetchInterval: (query) => {
      const isRunning = query.state.data?.sources.some((source) => source.status === 'running');
      return isRunning ? 2000 : false;
    },
  });
}

export function useKnowledgeIngestStart(): UseMutationResult<
  { message: string },
  Error,
  KnowledgeIngestBody
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: KnowledgeIngestBody) => startKnowledgeIngest(body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: knowledgeSourcesStatusKey });
    },
  });
}

export function useKnowledgeIngest(): {
  statusQuery: UseQueryResult<KnowledgeSourcesStatus>;
  startMutation: UseMutationResult<{ message: string }, Error, KnowledgeIngestBody>;
} {
  const statusQuery = useKnowledgeSourcesStatus();
  const startMutation = useKnowledgeIngestStart();
  const prevStatusesRef = useRef<Record<string, string>>({});

  useEffect(() => {
    const sources = statusQuery.data?.sources ?? [];
    const prevStatuses = prevStatusesRef.current;

    for (const source of sources) {
      if (source.status !== 'running' && prevStatuses[source.source_key] === 'running') {
        if (source.status === 'failed' && source.last_error) {
          toast.error(`${source.display_name} ingest failed`, {
            description: source.last_error,
          });
        } else if (source.status === 'ready') {
          toast.success(`${source.display_name} ingest complete`, {
            description: `${source.last_chunks_ingested} chunks, ${source.last_files_processed} files`,
          });
        }
      }

      prevStatuses[source.source_key] = source.status;
    }
  }, [statusQuery.data]);

  return { statusQuery, startMutation };
}
