/**
 * ReportList: report history for the current session with created_at (date-fns).
 * Click to open report view. Consumes reportToOpen from context to open a report when
 * user clicks "View report" in the report-ready toast.
 */

import { useState, useRef, useEffect } from 'react';
import { format } from 'date-fns';
import { FileText } from 'lucide-react';
import { toast } from 'sonner';
import { useCurrentSession } from '../contexts/SessionContext';
import { useReportToOpen } from '../contexts/ReportToOpenContext';
import { useReportsList } from '../hooks/useReports';
import { useFocusTrap } from '../hooks/useFocusTrap';
import { ReportView } from './ReportView';
import type { ReportListItem } from '../lib/schemas';

const UNAVAILABLE_MESSAGE = 'Session or report no longer available.';

export function ReportList() {
  const { currentSessionId } = useCurrentSession();
  const { reportToOpen, clearReportToOpen } = useReportToOpen();
  const { data, isLoading, error } = useReportsList(currentSessionId);
  const [selectedReport, setSelectedReport] = useState<ReportListItem | null>(null);
  const reportModalRef = useRef<HTMLDivElement>(null);
  useFocusTrap(!!selectedReport, reportModalRef);

  useEffect(() => {
    if (
      !reportToOpen ||
      reportToOpen.sessionId !== currentSessionId ||
      isLoading
    ) {
      return;
    }
    if (error) {
      toast.error(UNAVAILABLE_MESSAGE);
      clearReportToOpen();
      return;
    }
    const reports = data?.reports ?? [];
    const report = reports.find((r) => r.id === reportToOpen.reportId);
    if (report) {
      setSelectedReport(report);
      clearReportToOpen();
    } else {
      toast.error(UNAVAILABLE_MESSAGE);
      clearReportToOpen();
    }
  }, [
    reportToOpen,
    currentSessionId,
    isLoading,
    error,
    data?.reports,
    clearReportToOpen,
  ]);

  if (!currentSessionId) {
    return (
      <p className="text-base-content/70 text-sm">Select a session to view its reports.</p>
    );
  }

  if (isLoading) {
    return (
      <p
        className="flex items-center gap-2 text-base-content/70 text-sm"
        role="status"
        aria-busy="true"
      >
        <span className="loading loading-spinner loading-sm" aria-hidden />
        Loading reports…
      </p>
    );
  }
  if (error) {
    return (
      <p className="text-error text-sm" role="alert">
        Couldn't load reports.
      </p>
    );
  }

  const reports = data?.reports ?? [];

  return (
    <section className="space-y-2" aria-labelledby="report-list-heading">
      <h2 id="report-list-heading" className="text-xl font-semibold flex items-center gap-2">
        <FileText size={18} aria-hidden />
        Report history
      </h2>
      {reports.length === 0 ? (
        <p className="text-base-content/70 text-sm">No reports yet. Generate one above.</p>
      ) : (
        <ul className="space-y-1" aria-label="Reports">
          {reports.map((report) => (
            <li key={report.id}>
              <button
                type="button"
                className="btn btn-ghost btn-sm justify-start w-full text-left flex items-center gap-2"
                onClick={() => setSelectedReport(report)}
                aria-label={`View report from ${format(new Date(report.created_at), 'PPp')}`}
              >
                <FileText size={18} aria-hidden />
                <span className="truncate">
                  {format(new Date(report.created_at), 'PPp')}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}

      {selectedReport && (
        <dialog open className="modal modal-open" id="report-view-modal" aria-modal="true" aria-labelledby="report-view-title">
          <div className="modal-box max-w-4xl max-h-[80vh] flex flex-col" ref={reportModalRef} role="document">
            <h3 id="report-view-title" className="font-semibold text-lg">Report</h3>
            <ReportView
              sessionId={currentSessionId}
              reportId={selectedReport.id}
              onClose={() => setSelectedReport(null)}
            />
          </div>
          <form method="dialog" className="modal-backdrop" onSubmit={() => setSelectedReport(null)}>
            <button type="submit" aria-label="Close report view">close</button>
          </form>
        </dialog>
      )}
    </section>
  );
}
