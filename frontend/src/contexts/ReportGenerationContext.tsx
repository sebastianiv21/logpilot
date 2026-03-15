/**
 * Tracks which session has a report currently generating (empty content).
 * Used to disable "Generate report" for that session and to poll until content is ready.
 * When user switches session, generation continues in background (FR-012).
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from 'react';
import { getReport } from '../services/api';
import { notifyReportReady } from '../lib/reportReadyNotification';

type ReportGenerationContextValue = {
  /** Session ID -> report ID that is currently generating (content empty). */
  generatingBySession: Record<string, string>;
  setGenerating: (sessionId: string, reportId: string) => void;
  clearGenerating: (sessionId: string) => void;
  isGenerating: (sessionId: string) => boolean;
};

const ReportGenerationContext = createContext<ReportGenerationContextValue | null>(null);

const POLL_INTERVAL_MS = 2000;

export function ReportGenerationProvider({ children }: { children: ReactNode }) {
  const [generatingBySession, setState] = useState<Record<string, string>>({});
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const setGenerating = useCallback((sessionId: string, reportId: string) => {
    setState((prev) => (prev[sessionId] === reportId ? prev : { ...prev, [sessionId]: reportId }));
  }, []);

  const clearGenerating = useCallback((sessionId: string) => {
    setState((prev) => {
      const next = { ...prev };
      delete next[sessionId];
      return next;
    });
  }, []);

  const isGenerating = useCallback(
    (sessionId: string) => Boolean(generatingBySession[sessionId]),
    [generatingBySession]
  );

  useEffect(() => {
    const entries = Object.entries(generatingBySession);
    if (entries.length === 0) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    const poll = async () => {
      const generatingCount = entries.length;
      for (const [sessionId, reportId] of entries) {
        try {
          const report = await getReport(sessionId, reportId);
          if (report.content != null && report.content.trim().length > 0) {
            notifyReportReady(sessionId, generatingCount);
            setState((prev) => {
              const next = { ...prev };
              if (next[sessionId] === reportId) delete next[sessionId];
              return next;
            });
          }
        } catch {
          // keep polling on error (e.g. network)
        }
      }
    };

    intervalRef.current = setInterval(poll, POLL_INTERVAL_MS);
    poll();

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [generatingBySession]);

  const value: ReportGenerationContextValue = {
    generatingBySession,
    setGenerating,
    clearGenerating,
    isGenerating,
  };

  return (
    <ReportGenerationContext.Provider value={value}>
      {children}
    </ReportGenerationContext.Provider>
  );
}

export function useReportGeneration(): ReportGenerationContextValue {
  const ctx = useContext(ReportGenerationContext);
  if (ctx == null) {
    throw new Error('useReportGeneration must be used within ReportGenerationProvider');
  }
  return ctx;
}
