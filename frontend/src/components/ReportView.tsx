/**
 * ReportView: display report content (markdown rendered), export Markdown / PDF.
 * Export only when report has content; show "generating…" or disable export when not ready (FR-010).
 */

import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { toast } from 'sonner';
import { useReport } from '../hooks/useReports';
import { useReportGeneration } from '../contexts/ReportGenerationContext';
import { exportReport, downloadBlob } from '../services/api';

type Props = {
  sessionId: string;
  reportId: string;
  onClose?: () => void;
};

export function ReportView({ sessionId, reportId, onClose }: Props) {
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
      const msg = err instanceof Error ? err.message : 'Export failed';
      toast.error('Export failed', { description: msg });
    } finally {
      setExporting(null);
    }
  };

  return (
    <div className="flex flex-col flex-1 min-h-0 mt-2">
      {isLoading && !report && (
        <p className="text-base-content/70 text-sm">Loading report…</p>
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
              className="btn btn-sm btn-outline"
              onClick={() => handleExport('markdown')}
              disabled={!hasContent || exporting !== null}
              aria-busy={exporting === 'markdown'}
              aria-describedby={!hasContent ? 'export-disabled-reason' : undefined}
            >
              {exporting === 'markdown' ? 'Exporting…' : 'Export Markdown'}
            </button>
            <button
              type="button"
              className="btn btn-sm btn-outline"
              onClick={() => handleExport('pdf')}
              disabled={!hasContent || exporting !== null}
              aria-busy={exporting === 'pdf'}
            >
              {exporting === 'pdf' ? 'Exporting…' : 'Export PDF'}
            </button>
          </div>
          {!hasContent && (
            <p id="export-disabled-reason" className="text-sm text-base-content/70 mb-2">
              Report is still generating. Export is available when content is ready.
            </p>
          )}
          <div className="flex-1 overflow-auto rounded border border-base-300 bg-base-200 p-4">
            {hasContent ? (
              <div className="report-content text-sm space-y-2 [&_h1]:text-lg [&_h2]:text-base [&_h3]:text-sm [&_ul]:list-disc [&_ol]:list-decimal [&_pre]:bg-base-300 [&_pre]:p-2 [&_pre]:rounded [&_code]:bg-base-300 [&_code]:px-1 [&_code]:rounded">
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
