/**
 * ReportGenerate: incident question input, trigger button.
 * Disabled when a report is already generating for the current session (FR-008).
 * Shows "in progress" until content is ready.
 */

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { toast } from 'sonner';
import { ReportGenerateFormSchema, type ReportGenerateFormValues } from '../lib/schemas';
import { useCurrentSession } from '../contexts/SessionContext';
import { useReportGeneration } from '../contexts/ReportGenerationContext';
import { useGenerateReport } from '../hooks/useReports';

export function ReportGenerate() {
  const { currentSessionId } = useCurrentSession();
  const { setGenerating, isGenerating, generatingBySession } = useReportGeneration();
  const generateMutation = useGenerateReport(currentSessionId, (reportId) => {
    if (currentSessionId) setGenerating(currentSessionId, reportId);
  });

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ReportGenerateFormValues>({
    resolver: zodResolver(ReportGenerateFormSchema),
    defaultValues: { question: '' },
  });

  const generatingForCurrent = currentSessionId ? isGenerating(currentSessionId) : false;
  const otherSessionsGenerating = Object.keys(generatingBySession).filter(
    (sid) => sid !== currentSessionId
  );

  const onSubmit = handleSubmit((data) => {
    if (!currentSessionId) return;
    generateMutation.mutate(
      { question: data.question.trim() },
      {
        onSuccess: () => {
          reset();
          toast.info('Report generation started', {
            description:
              "Content will appear when ready. You can switch sessions; the report will show in this session's list when done.",
          });
        },
        onError: (err) => {
          const msg = err instanceof Error ? err.message : 'Failed to start report';
          toast.error('Could not start report', { description: msg });
        },
      }
    );
  });

  return (
    <section className="space-y-3" aria-labelledby="report-generate-heading">
      <h2 id="report-generate-heading" className="text-xl font-semibold">
        Generate report
      </h2>
      <p className="text-base-content/80 text-sm">
        Enter an incident question to generate an AI report for the current session. Only one
        report generates at a time per session.
      </p>

      {otherSessionsGenerating.length > 0 && (
        <p className="text-sm text-base-content/70" role="status">
          Report is generating in the background for another session. It will appear in that
          session's report list when ready. You can continue here.
        </p>
      )}

      <form onSubmit={onSubmit} className="space-y-2">
        <div>
          <label htmlFor="report-question" className="label text-xs">
            Incident question
          </label>
          <input
            id="report-question"
            type="text"
            className="input input-bordered input-sm w-full"
            placeholder="e.g. Why did the service fail at 3pm?"
            aria-invalid={!!errors.question}
            aria-describedby={errors.question ? 'report-question-error' : undefined}
            {...register('question')}
          />
          {errors.question && (
            <p id="report-question-error" className="text-error text-xs mt-0.5" role="alert">
              {errors.question.message}
            </p>
          )}
        </div>
        <button
          type="submit"
          className="btn btn-primary flex items-center gap-2"
          disabled={!currentSessionId || generatingForCurrent || generateMutation.isPending}
          aria-busy={generatingForCurrent || generateMutation.isPending}
          aria-describedby="report-generate-status"
          aria-label="Generate report from incident question"
        >
          {(generateMutation.isPending || generatingForCurrent) && (
            <span className="loading loading-spinner loading-sm" aria-hidden />
          )}
          {generateMutation.isPending
            ? 'Starting…'
            : generatingForCurrent
              ? 'Generating…'
              : 'Generate report'}
        </button>
        <p id="report-generate-status" className="text-sm text-base-content/70" aria-live="polite">
          {generatingForCurrent &&
            'Report is being generated. View it in the report list below once content is ready.'}
        </p>
        {generateMutation.isError && (
          <p className="text-error text-sm" role="alert">
            {generateMutation.error?.message}
          </p>
        )}
      </form>
    </section>
  );
}
