import { useState, useMemo } from 'react';
import { format, parseISO } from 'date-fns';
import { Check, Pencil } from 'lucide-react';
import type { Session } from '../lib/schemas';
import { useSessionsList } from '../hooks/useSessions';
import { useCurrentSession } from '../contexts/SessionContext';

const SESSIONS_BATCH_SIZE = 10;

function SessionListItem({
  session,
  isCurrent,
  onSelect,
  onEdit,
}: {
  session: Session;
  isCurrent: boolean;
  onSelect: () => void;
  onEdit: () => void;
}) {
  const createdAt = (() => {
    try {
      return format(parseISO(session.created_at), 'MMM d, yyyy HH:mm');
    } catch {
      return session.created_at;
    }
  })();

  return (
    <div
      className={`rounded-lg border p-2 text-sm ${
        isCurrent
          ? 'border-primary bg-primary/10'
          : 'border-base-300 bg-base-100 hover:bg-base-200'
      }`}
      data-current={isCurrent}
    >
      <div className="font-medium truncate" title={session.name ?? session.id}>
        {session.name || `Session ${session.id.slice(0, 8)}`}
      </div>
      <div className="text-base-content/60 mt-0.5">{createdAt}</div>
      {session.external_link ? (
        <a
          href={session.external_link}
          target="_blank"
          rel="noopener noreferrer"
          className="link link-hover text-xs mt-1 block truncate"
          title={session.external_link}
        >
          {session.external_link}
        </a>
      ) : null}
      <div className="mt-2 flex gap-1">
        <button
          type="button"
          className="btn btn-xs btn-ghost flex items-center gap-1"
          onClick={onSelect}
          aria-pressed={isCurrent}
          aria-label={isCurrent ? 'Current session' : 'Set as current session'}
        >
          <Check size={18} aria-hidden />
          {isCurrent ? 'Current' : 'Select'}
        </button>
        <button
          type="button"
          className="btn btn-xs btn-ghost flex items-center gap-1"
          onClick={onEdit}
          aria-label="Edit session"
        >
          <Pencil size={18} aria-hidden />
          Edit
        </button>
      </div>
    </div>
  );
}

function filterSessionsByQuery(sessions: Session[], query: string): Session[] {
  const q = query.trim().toLowerCase();
  if (!q) return sessions;
  return sessions.filter(
    (s) =>
      (s.name ?? '').toLowerCase().includes(q) ||
      s.id.toLowerCase().includes(q) ||
      (s.external_link ?? '').toLowerCase().includes(q)
  );
}

export function SessionList({
  onEditSession,
  searchQuery = '',
}: {
  onEditSession: (session: Session) => void;
  searchQuery?: string;
}) {
  const { data, isLoading, isError, error } = useSessionsList();
  const { currentSessionId, setCurrentSessionId } = useCurrentSession();
  const [visibleCount, setVisibleCount] = useState<number>(SESSIONS_BATCH_SIZE);

  const sessions = data?.sessions ?? [];
  const filteredSessions = useMemo(
    () => filterSessionsByQuery(sessions, searchQuery),
    [sessions, searchQuery]
  );
  const visibleSessions = useMemo(
    () => filteredSessions.slice(0, visibleCount),
    [filteredSessions, visibleCount]
  );
  const hasMore = visibleCount < filteredSessions.length;
  const hasPrevious = visibleCount > SESSIONS_BATCH_SIZE;
  const isSinglePage = filteredSessions.length <= SESSIONS_BATCH_SIZE;
  const showPaginationControls = filteredSessions.length > 0 && !isSinglePage;

  const searchActive = searchQuery.trim() !== '';
  const liveRegionText =
    !searchActive
      ? ''
      : filteredSessions.length === 0
        ? 'No sessions match your search.'
        : filteredSessions.length === 1
          ? '1 session'
          : `${filteredSessions.length} sessions`;

  if (isLoading) {
    return (
      <div
        className="flex items-center gap-2 text-sm text-base-content/60 p-2"
        role="status"
        aria-busy="true"
        aria-live="polite"
      >
        <span className="loading loading-spinner loading-sm" aria-hidden />
        Loading sessions…
      </div>
    );
  }

  if (isError) {
    return (
      <div className="text-sm text-error p-2" role="alert">
        {error?.message ?? 'Couldn\'t load sessions'}
      </div>
    );
  }

  if (sessions.length === 0) {
    return (
      <div className="text-sm text-base-content/60 p-2" aria-live="polite">
        No sessions yet. Create one to get started.
      </div>
    );
  }

  if (
    filteredSessions.length === 0 &&
    searchQuery.trim() !== ''
  ) {
    return (
      <div className="space-y-2">
        <div
          className="sr-only"
          aria-live="polite"
          aria-atomic="true"
          role="status"
        >
          {liveRegionText}
        </div>
        <div className="text-sm text-base-content/60 p-2">
          No sessions match your search.
        </div>
      </div>
    );
  }

  const handleLoadMore = () => {
    setVisibleCount((c) =>
      Math.min(c + SESSIONS_BATCH_SIZE, filteredSessions.length)
    );
  };
  const handlePrevious = () => {
    setVisibleCount((c) => Math.max(SESSIONS_BATCH_SIZE, c - SESSIONS_BATCH_SIZE));
  };

  return (
    <div className="space-y-2">
      {liveRegionText ? (
        <div
          className="sr-only"
          aria-live="polite"
          aria-atomic="true"
          role="status"
        >
          {liveRegionText}
        </div>
      ) : null}
      <ul className="space-y-2 p-0 list-none" aria-label="Session list">
        {visibleSessions.map((session) => (
          <li key={session.id}>
            <SessionListItem
              session={session}
              isCurrent={currentSessionId === session.id}
              onSelect={() => setCurrentSessionId(session.id)}
              onEdit={() => onEditSession(session)}
            />
          </li>
        ))}
      </ul>
      {showPaginationControls && (
        <div
          className="flex flex-wrap gap-2 pt-2 justify-center"
          role="group"
          aria-label="Sessions pagination"
        >
          {hasPrevious && (
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={handlePrevious}
              aria-label="Previous page of sessions"
            >
              Previous
            </button>
          )}
          {hasMore && (
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={handleLoadMore}
              aria-label="Load more sessions"
            >
              Load more
            </button>
          )}
        </div>
      )}
    </div>
  );
}
