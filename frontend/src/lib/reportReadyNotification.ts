/**
 * Report-ready notification: toast + subtle sound.
 * Message always includes session identity (name or id); long names truncated with full value in title.
 * Per specs/011-report-ready-alert-session/contracts/report-ready-notification.md
 */

import { toast } from 'sonner';
import { getSession } from '../services/api';
import { playReportReadySound } from './sound';

const MAX_LABEL_LENGTH = 40;

function getSessionLabel(sessionId: string): Promise<string> {
  return getSession(sessionId)
    .then((s) => (s.name && s.name.trim() ? s.name.trim() : s.id.slice(0, 8)))
    .catch(() => sessionId.slice(0, 8));
}

/**
 * Truncate label for display; full value available via title (FR-004).
 */
function truncateLabel(label: string): { display: string; title: string } {
  if (label.length <= MAX_LABEL_LENGTH) return { display: label, title: label };
  return {
    display: `${label.slice(0, MAX_LABEL_LENGTH - 1)}\u2026`,
    title: label,
  };
}

/**
 * Show report-ready toast and play sound. Call when a report transitions from generating to ready.
 * Message always includes session identity (session name or truncated id). Optional onViewReport
 * is used in Phase 4 to add a "View report" action.
 */
export async function notifyReportReady(
  sessionId: string,
  reportId: string,
  _generatingCount: number,
  onViewReport?: (sessionId: string, reportId: string) => void
): Promise<void> {
  const rawLabel = await getSessionLabel(sessionId);
  const { display: labelDisplay, title: labelTitle } = truncateLabel(rawLabel);
  const message = `Report ready (${labelDisplay})`;
  const description = labelDisplay !== labelTitle ? labelTitle : undefined;
  toast.success(message, {
    ...(description && { description }),
    ...(onViewReport && {
      action: {
        label: 'View report',
        onClick: () => onViewReport(sessionId, reportId),
      },
    }),
  });
  playReportReadySound();
}
