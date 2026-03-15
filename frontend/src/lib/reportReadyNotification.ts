/**
 * Report-ready notification: toast + subtle sound.
 * Context-aware message when multiple sessions have reports generating (session name or id).
 * Per specs/004-ui-polish-feedback/contracts/report-ready-notification.md
 */

import { toast } from 'sonner';
import { getSession } from '../services/api';
import { playReportReadySound } from './sound';

function getSessionLabel(sessionId: string): Promise<string> {
  return getSession(sessionId)
    .then((s) => (s.name && s.name.trim() ? s.name.trim() : s.id.slice(0, 8)))
    .catch(() => sessionId.slice(0, 8));
}

/**
 * Show report-ready toast and play sound. Call when a report transitions from generating to ready.
 * If generatingCount > 1, message includes session context (resolved via getSession).
 */
export async function notifyReportReady(
  sessionId: string,
  generatingCount: number
): Promise<void> {
  const message =
    generatingCount > 1
      ? `Report ready (${await getSessionLabel(sessionId)})`
      : 'Report ready';
  toast.success(message);
  playReportReadySound();
}
