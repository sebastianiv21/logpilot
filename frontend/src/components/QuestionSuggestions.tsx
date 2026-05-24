/**
 * QuestionSuggestions: three pill buttons surfaced above the question input
 * after a log upload completes. Clicking one calls `onSelect(question)` so
 * the parent (ReportGenerate) can populate the form field. The backend
 * returns an empty list (not an error) when the LLM is unconfigured or the
 * agent run fails — we silently hide the section in that case.
 */

import { useQuery } from '@tanstack/react-query';
import { Sparkles } from 'lucide-react';
import { getSuggestedQuestions } from '../services/api';

type Props = {
  sessionId: string;
  /** Called with the chosen question text. */
  onSelect: (question: string) => void;
  /** Suggestions only make sense after logs land; pass false to skip the fetch. */
  enabled?: boolean;
};

export function QuestionSuggestions({ sessionId, onSelect, enabled = true }: Props) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['suggestedQuestions', sessionId],
    queryFn: () => getSuggestedQuestions(sessionId),
    enabled: enabled && !!sessionId,
    // The backend caches in-process; the data is effectively immutable for a
    // session's lifetime, so don't refetch on focus/reconnect.
    staleTime: Infinity,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  });

  if (!enabled || !sessionId) return null;

  if (isLoading) {
    return (
      <div
        className="flex items-center gap-2 text-xs text-base-content/60"
        role="status"
        aria-live="polite"
      >
        <span className="loading loading-spinner loading-xs" aria-hidden />
        Generating suggestions…
      </div>
    );
  }

  const questions = data?.questions ?? [];
  if (isError || questions.length === 0) return null;

  return (
    <div className="space-y-1.5" aria-labelledby="suggested-questions-heading">
      <p
        id="suggested-questions-heading"
        className="text-xs text-base-content/60 flex items-center gap-1.5"
      >
        <Sparkles size={12} aria-hidden />
        Suggested questions
      </p>
      <div className="flex flex-wrap gap-1.5" role="group" aria-label="Suggested question pills">
        {questions.map((q) => (
          <button
            key={q}
            type="button"
            className="badge badge-outline badge-sm cursor-pointer hover:bg-base-200 px-3 py-2 h-auto whitespace-normal text-left"
            onClick={() => onSelect(q)}
            aria-label={`Use suggested question: ${q}`}
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
