/**
 * TanStack Query hooks for reports API.
 * List reports, get report by id (with optional polling until content), generate mutation.
 */

import {
  useQuery,
  useMutation,
  useQueryClient,
  type UseQueryResult,
  type UseMutationResult,
} from '@tanstack/react-query';
import {
  getReports,
  getReport,
  generateReport,
  type GenerateReportBody,
} from '../services/api';
import type { Report, ReportList } from '../lib/schemas';

const reportsListKey = (sessionId: string) => ['sessions', sessionId, 'reports'] as const;
const reportKey = (sessionId: string, reportId: string) =>
  ['sessions', sessionId, 'reports', reportId] as const;

export function useReportsList(sessionId: string | null): UseQueryResult<ReportList> {
  return useQuery({
    queryKey: reportsListKey(sessionId ?? ''),
    queryFn: () => getReports(sessionId!),
    enabled: !!sessionId,
  });
}

export function useReport(
  sessionId: string | null,
  reportId: string | null,
  options?: { refetchIntervalWhenEmpty?: number }
): UseQueryResult<Report> {
  return useQuery({
    queryKey: reportKey(sessionId ?? '', reportId ?? ''),
    queryFn: () => getReport(sessionId!, reportId!),
    enabled: !!sessionId && !!reportId,
    refetchInterval: (query) => {
      if (options?.refetchIntervalWhenEmpty != null) {
        const content = query.state.data?.content;
        if (content == null || content.trim() === '') return options.refetchIntervalWhenEmpty;
      }
      return false;
    },
  });
}

export function useGenerateReport(
  sessionId: string | null,
  onReportCreated?: (reportId: string) => void
): UseMutationResult<
  { id: string; session_id: string; created_at: string; content: string | null },
  Error,
  GenerateReportBody
> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (body: GenerateReportBody) => generateReport(sessionId!, body),
    onSuccess: (data) => {
      const sid = data.session_id;
      queryClient.invalidateQueries({ queryKey: reportsListKey(sid) });
      queryClient.setQueryData(reportKey(sid, data.id), {
        id: data.id,
        session_id: data.session_id,
        created_at: data.created_at,
        content: data.content ?? '',
      });
      onReportCreated?.(data.id);
    },
  });
}
