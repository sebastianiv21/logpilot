/**
 * ReportView: display report content (markdown rendered), export Markdown / PDF.
 * Export only when report has content; show "generating…" or disable export when not ready (FR-010).
 */

import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { toast } from 'sonner';
import { FileDown } from 'lucide-react';
import { useReport } from '../hooks/useReports';
import { useReportGeneration } from '../contexts/ReportGenerationContext';
import { ApiError, exportReport, downloadBlob } from '../services/api';

type Props = {
  sessionId: string;
  reportId: string;
  onClose?: () => void;
};

export function ReportView({ sessionId, reportId, onClose: _onClose }: Props) {
  const { data: report, isLoading, error } = useReport(sessionId, reportId, {
    refetchIntervalWhenEmpty: 2000,
  });
  const { clearGenerating } = useReportGeneration();
  const [exporting, setExporting] = useState<'markdown' | 'pdf' | null>(null);

  const hasContent = report?.content != null && report.content.trim().length > 0;

  useEffect(() => {
    if (hasContent) clearGenerating(sessionId);
  }, [hasContent, sessionId, clearGenerating]);

  const handleExport = async (format: 'markdown' | 'pdf') => {
    if (!hasContent) return;
    setExporting(format);
    try {
      const blob = await exportReport(sessionId, reportId, format);
      const ext = format === 'pdf' ? 'pdf' : 'md';
      downloadBlob(blob, `report-${reportId}.${ext}`);
      toast.success(`Exported as ${format}`);
    } catch (err) {
      const description =
        err instanceof ApiError
          ? err.userMessage
          : err instanceof Error && err.message
            ? (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')
                ? 'Export failed. Try again.'
                : err.message)
            : 'Export failed. Try again.';
      toast.error('Export failed', { description });
    } finally {
      setExporting(null);
    }
  };

  return (
    <div className="flex flex-col flex-1 min-h-0 mt-2">
      {isLoading && !report && (
        <p
          className="flex items-center gap-2 text-base-content/70 text-sm"
          role="status"
          aria-busy="true"
        >
          <span className="loading loading-spinner loading-sm" aria-hidden />
          Loading report…
        </p>
      )}
      {error && (
        <p className="text-error text-sm" role="alert">
          Failed to load report: {error.message}
        </p>
      )}
      {report && (
        <>
          <div className="flex flex-wrap gap-2 mb-3">
            <button
              type="button"
              className="btn btn-sm btn-outline flex items-center gap-2"
              onClick={() => handleExport('markdown')}
              disabled={!hasContent || exporting !== null}
              aria-busy={exporting === 'markdown'}
              aria-describedby={!hasContent ? 'export-disabled-reason' : undefined}
              aria-label="Export report as Markdown"
            >
              <FileDown size={18} aria-hidden />
              {exporting === 'markdown' ? 'Exporting…' : 'Export Markdown'}
            </button>
            <button
              type="button"
              className="btn btn-sm btn-outline flex items-center gap-2"
              onClick={() => handleExport('pdf')}
              disabled={!hasContent || exporting !== null}
              aria-busy={exporting === 'pdf'}
              aria-describedby={!hasContent ? 'export-disabled-reason' : undefined}
              aria-label="Export report as PDF"
            >
              <FileDown size={18} aria-hidden />
              {exporting === 'pdf' ? 'Exporting…' : 'Export PDF'}
            </button>
          </div>
          {!hasContent && (
            <p id="export-disabled-reason" className="text-sm text-base-content/70 mb-2">
              Report is still generating. Export is available when content is ready.
            </p>
          )}
          <div className="flex-1 overflow-auto rounded border border-base-300 bg-base-200 p-4 min-w-0">
            {hasContent ? (
              <div
                className="report-content text-sm break-words space-y-3 max-w-full
                  [&_h1]:text-xl [&_h1]:font-semibold [&_h1]:mt-4 [&_h1]:mb-2 [&_h1]:first:mt-0
                  [&_h2]:text-lg [&_h2]:font-semibold [&_h2]:mt-3 [&_h2]:mb-1.5
                  [&_h3]:text-base [&_h3]:font-medium [&_h3]:mt-2 [&_h3]:mb-1
                  [&_ul]:list-disc [&_ul]:pl-6 [&_ul]:space-y-1
                  [&_ol]:list-decimal [&_ol]:pl-6 [&_ol]:space-y-1
                  [&_p]:leading-relaxed
                  [&_code]:font-mono [&_code]:text-[13px] [&_code]:rounded
                  [&_code]:bg-base-300/80 [&_code]:px-1.5 [&_code]:py-0.5
                  [&_code]:border [&_code]:border-base-300
                  [&_pre]:my-3 [&_pre]:p-4 [&_pre]:rounded-lg [&_pre]:border [&_pre]:border-base-300
                  [&_pre]:bg-base-300/80 [&_pre]:overflow-x-auto [&_pre]:font-mono [&_pre]:text-[13px]
                  [&_pre]:leading-relaxed [&_pre]:min-h-0
                  [&_pre_code]:bg-transparent [&_pre_code]:p-0 [&_pre_code]:border-0 [&_pre_code]:rounded-none
                  [&_pre_code]:break-all"
                style={{ overflowWrap: 'break-word' } as React.CSSProperties}
              >
                <ReactMarkdown>{report.content}</ReactMarkdown>
              </div>
            ) : (
              <p className="text-base-content/70">Generating… Content will appear here when ready.</p>
            )}
          </div>
        </>
      )}
    </div>
  );
}
