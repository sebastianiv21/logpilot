import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';

const STORAGE_KEY = 'logpilot_current_session_id';

type SessionContextValue = {
  currentSessionId: string | null;
  setCurrentSessionId: (id: string | null) => void;
  /** Session IDs that have had at least one successful upload (in this tab). Used to show "upload first" until logs exist. */
  sessionIdsWithLogs: Set<string>;
  markSessionHasLogs: (sessionId: string) => void;
};

const SessionContext = createContext<SessionContextValue | null>(null);

function readStored(): string | null {
  try {
    const v = localStorage.getItem(STORAGE_KEY);
    return v && v.length > 0 ? v : null;
  } catch {
    return null;
  }
}

function writeStored(id: string | null): void {
  try {
    if (id == null) localStorage.removeItem(STORAGE_KEY);
    else localStorage.setItem(STORAGE_KEY, id);
  } catch {
    // ignore
  }
}

export function SessionProvider({ children }: { children: ReactNode }) {
  const [currentSessionId, setState] = useState<string | null>(readStored);
  const [sessionIdsWithLogs, setSessionIdsWithLogs] = useState<Set<string>>(() => new Set());

  useEffect(() => {
    writeStored(currentSessionId);
  }, [currentSessionId]);

  const setCurrentSessionId = useCallback((id: string | null) => {
    setState(id);
  }, []);

  const markSessionHasLogs = useCallback((sessionId: string) => {
    setSessionIdsWithLogs((prev) => new Set(prev).add(sessionId));
  }, []);

  const value = useMemo<SessionContextValue>(
    () => ({
      currentSessionId,
      setCurrentSessionId,
      sessionIdsWithLogs,
      markSessionHasLogs,
    }),
    [currentSessionId, setCurrentSessionId, sessionIdsWithLogs, markSessionHasLogs]
  );

  return (
    <SessionContext.Provider value={value}>
      {children}
    </SessionContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components -- hook exported from same file as provider
export function useCurrentSession(): SessionContextValue {
  const ctx = useContext(SessionContext);
  if (ctx == null) {
    throw new Error('useCurrentSession must be used within SessionProvider');
  }
  return ctx;
}
