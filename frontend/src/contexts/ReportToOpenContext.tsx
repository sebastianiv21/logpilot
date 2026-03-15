/**
 * Report-to-open intent: when the user clicks "View report" in the report-ready toast,
 * we set current session and this intent so ReportList can open the report modal.
 * Per specs/011-report-ready-alert-session/data-model.md
 *
 * The provider that wires openReport to setCurrentSessionId + navigate must live
 * inside BrowserRouter and SessionProvider (see App.tsx ReportToOpenProviderWithNav).
 */

import {
  createContext,
  useCallback,
  useContext,
  useState,
  type ReactNode,
} from 'react';

export type ReportToOpen = { sessionId: string; reportId: string };

export type ReportToOpenContextValue = {
  reportToOpen: ReportToOpen | null;
  openReport: (sessionId: string, reportId: string) => void;
  clearReportToOpen: () => void;
};

export const ReportToOpenContext = createContext<ReportToOpenContextValue | null>(null);

export function useReportToOpen(): ReportToOpenContextValue {
  const ctx = useContext(ReportToOpenContext);
  if (ctx == null) {
    throw new Error('useReportToOpen must be used within ReportToOpenProvider');
  }
  return ctx;
}

/** Provider that only holds state; use ReportToOpenProviderWithNav in App for full openReport (session + navigate). */
export function ReportToOpenProvider({ children }: { children: ReactNode }) {
  const [reportToOpen, setReportToOpen] = useState<ReportToOpen | null>(null);
  const openReport = useCallback((sessionId: string, reportId: string) => {
    setReportToOpen({ sessionId, reportId });
  }, []);
  const clearReportToOpen = useCallback(() => setReportToOpen(null), []);
  return (
    <ReportToOpenContext.Provider
      value={{ reportToOpen, openReport, clearReportToOpen }}
    >
      {children}
    </ReportToOpenContext.Provider>
  );
}
