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

  useEffect(() => {
    writeStored(currentSessionId);
  }, [currentSessionId]);

  const setCurrentSessionId = useCallback((id: string | null) => {
    setState(id);
  }, []);

  const value = useMemo<SessionContextValue>(
    () => ({ currentSessionId, setCurrentSessionId }),
    [currentSessionId, setCurrentSessionId]
  );

  return (
    <SessionContext.Provider value={value}>
      {children}
    </SessionContext.Provider>
  );
}

export function useCurrentSession(): SessionContextValue {
  const ctx = useContext(SessionContext);
  if (ctx == null) {
    throw new Error('useCurrentSession must be used within SessionProvider');
  }
  return ctx;
}
