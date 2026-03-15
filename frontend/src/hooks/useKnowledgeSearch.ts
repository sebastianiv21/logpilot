/**
 * useKnowledgeSearch: run knowledge search query, return chunks (content, source_path, metadata).
 */

import {
  useMutation,
  type UseMutationResult,
} from '@tanstack/react-query';
import { searchKnowledge, type KnowledgeSearchBody } from '../services/api';
import type { KnowledgeSearchResponse } from '../lib/schemas';

export type KnowledgeSearchVariables = KnowledgeSearchBody;

export function useKnowledgeSearch(): UseMutationResult<
  KnowledgeSearchResponse,
  Error,
  KnowledgeSearchVariables
> {
  return useMutation({
    mutationFn: (body: KnowledgeSearchVariables) => searchKnowledge(body),
  });
}
