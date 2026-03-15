import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation } from '@tanstack/react-query';
import { Search } from 'lucide-react';
import { queryLogs } from '../services/api';
import { useCurrentSession } from '../contexts/SessionContext';
import {
  LogSearchFormSchema,
  type LogSearchFormValues,
  type LogsQueryResponse,
} from '../lib/schemas';

const LIMIT_OPTIONS = [50, 100, 250, 500, 1000] as const;

export type LogSearchRequestParams = {
  start: string | null;
  end: string | null;
  limit: number;
  service: string | null;
  environment: string | null;
  log_level: string | null;
};

type LogSearchFormProps = {
  onResult: (data: LogsQueryResponse, params: LogSearchRequestParams) => void;
  disabled?: boolean;
};

/** Default time range: omit start/end so backend uses full extent of session logs (T024). */
function toQueryParams(values: LogSearchFormValues): {
  start: string | null;
  end: string | null;
  limit: number;
  service: string | null;
  environment: string | null;
  log_level: string | null;
} {
  return {
    start: values.start?.trim() ? values.start.trim() : null,
    end: values.end?.trim() ? values.end.trim() : null,
    limit: values.limit ?? 100,
    service: values.service?.trim() ? values.service.trim() : null,
    environment: values.environment?.trim() ? values.environment.trim() : null,
    log_level: values.log_level?.trim() ? values.log_level.trim() : null,
  };
}

export function LogSearchForm({ onResult, disabled }: LogSearchFormProps) {
  const { currentSessionId } = useCurrentSession();

  const form = useForm<LogSearchFormValues>({
    resolver: zodResolver(LogSearchFormSchema),
    defaultValues: {
      start: '',
      end: '',
      limit: 100 as LogSearchFormValues['limit'],
      service: '',
      environment: '',
      log_level: '',
    },
  });

  const mutation = useMutation({
    mutationFn: async (params: ReturnType<typeof toQueryParams>) => {
      if (!currentSessionId) throw new Error('No session selected');
      const data = await queryLogs(currentSessionId, params);
      return { data, params };
    },
    onSuccess: ({ data, params }) => {
      onResult(data, params);
    },
  });

  const onSubmit = form.handleSubmit((values) => {
    mutation.mutate(toQueryParams(values));
  });

  if (!currentSessionId) return null;

  return (
    <form onSubmit={onSubmit} className="flex flex-wrap items-end gap-3">
      <label className="form-control max-w-xs">
        <span className="label-text">Start (ISO or leave empty for session start)</span>
        <input
          type="text"
          placeholder="e.g. 2025-01-01T00:00:00Z"
          className="input input-bordered input-sm w-full"
          aria-label="Start time"
          {...form.register('start')}
        />
        {form.formState.errors.start && (
          <span className="label-text-alt text-error">{form.formState.errors.start.message}</span>
        )}
      </label>
      <label className="form-control max-w-xs">
        <span className="label-text">End (ISO or leave empty for session end)</span>
        <input
          type="text"
          placeholder="e.g. 2025-01-02T00:00:00Z"
          className="input input-bordered input-sm w-full"
          aria-label="End time"
          {...form.register('end')}
        />
        {form.formState.errors.end && (
          <span className="label-text-alt text-error">{form.formState.errors.end.message}</span>
        )}
      </label>
      <label className="form-control w-24">
        <span className="label-text">Limit</span>
        <select
          className="select select-bordered select-sm w-full"
          aria-label="Max results"
          {...form.register('limit', { valueAsNumber: true })}
        >
          {LIMIT_OPTIONS.map((n) => (
            <option key={n} value={n}>
              {n}
            </option>
          ))}
        </select>
      </label>
      <label className="form-control max-w-[8rem]">
        <span className="label-text">Service</span>
        <input
          type="text"
          placeholder="optional"
          className="input input-bordered input-sm w-full"
          aria-label="Filter by service"
          {...form.register('service')}
        />
      </label>
      <label className="form-control max-w-[8rem]">
        <span className="label-text">Environment</span>
        <input
          type="text"
          placeholder="optional"
          className="input input-bordered input-sm w-full"
          aria-label="Filter by environment"
          {...form.register('environment')}
        />
      </label>
      <label className="form-control max-w-[8rem]">
        <span className="label-text">Log level</span>
        <input
          type="text"
          placeholder="optional"
          className="input input-bordered input-sm w-full"
          aria-label="Filter by log level"
          {...form.register('log_level')}
        />
      </label>
      <button
        type="submit"
        className="btn btn-primary btn-sm flex items-center gap-2"
        disabled={disabled || mutation.isPending}
        aria-busy={mutation.isPending}
        aria-label="Search logs"
      >
        {mutation.isPending ? (
          <span className="loading loading-spinner loading-sm" aria-hidden />
        ) : (
          <Search size={18} aria-hidden />
        )}
        {mutation.isPending ? 'Searching…' : 'Search'}
      </button>
    </form>
  );
}
