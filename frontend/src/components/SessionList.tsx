import { format, parseISO } from 'date-fns';
import type { Session } from '../lib/schemas';
import { useSessionsList } from '../hooks/useSessions';
import { useCurrentSession } from '../contexts/SessionContext';

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
          className="btn btn-xs btn-ghost"
          onClick={onSelect}
          aria-pressed={isCurrent}
          aria-label={isCurrent ? 'Current session' : 'Set as current session'}
        >
          {isCurrent ? 'Current' : 'Select'}
        </button>
        <button
          type="button"
          className="btn btn-xs btn-ghost"
          onClick={onEdit}
          aria-label="Edit session"
        >
          Edit
        </button>
      </div>
    </div>
  );
}

export function SessionList({
  onEditSession,
}: {
  onEditSession: (session: Session) => void;
}) {
  const { data, isLoading, isError, error } = useSessionsList();
  const { currentSessionId, setCurrentSessionId } = useCurrentSession();

  if (isLoading) {
    return (
      <div className="text-sm text-base-content/60 p-2" aria-live="polite">
        Loading sessions…
      </div>
    );
  }

  if (isError) {
    return (
      <div className="text-sm text-error p-2" role="alert">
        {error?.message ?? 'Failed to load sessions'}
      </div>
    );
  }

  const sessions = data?.sessions ?? [];

  if (sessions.length === 0) {
    return (
      <div className="text-sm text-base-content/60 p-2" aria-live="polite">
        No sessions yet. Create one to get started.
      </div>
    );
  }

  return (
    <ul className="space-y-2 p-0 list-none" aria-label="Session list">
      {sessions.map((session) => (
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
  );
}
