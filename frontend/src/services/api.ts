/**
 * API client for LogPilot backend.
 * Base URL from VITE_API_BASE; fetch wrapper with JSON and error handling.
 */

import {
  GenerateReportResponseSchema,
  KnowledgeIngestStatusSchema,
  KnowledgeSearchResponseSchema,
  LogsQueryResponseSchema,
  ReportListSchema,
  ReportSchema,
  UploadResultSchema,
} from '../lib/schemas';
import type {
  GenerateReportResponse,
  KnowledgeIngestStatus,
  KnowledgeSearchResponse,
  LogsQueryRequest,
  LogsQueryResponse,
  Report,
  ReportList,
  Session,
  SessionList,
  UploadResult,
} from '../lib/schemas';

const getBaseUrl = (): string => {
  const base = import.meta.env.VITE_API_BASE;
  if (typeof base === 'string' && base.length > 0) return base.replace(/\/$/, '');
  return '';
};

export type ApiErrorDetail = string | Array<{ loc: (string | number)[]; msg: string; type?: string }>;

export class ApiError extends Error {
  status: number;
  detail: ApiErrorDetail;
  constructor(status: number, detail: ApiErrorDetail, message?: string) {
    super(message ?? (typeof detail === 'string' ? detail : 'Request failed'));
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }

  /** User-friendly message from backend detail (string or first validation message). */
  get userMessage(): string {
    if (typeof this.detail === 'string') return this.detail;
    if (Array.isArray(this.detail) && this.detail.length > 0) {
      const first = this.detail[0];
      return typeof first === 'object' && first !== null && 'msg' in first
        ? String(first.msg)
        : JSON.stringify(this.detail);
    }
    return `Request failed (${this.status})`;
  }
}

async function parseErrorResponse(res: Response): Promise<ApiError> {
  let detail: ApiErrorDetail = `Request failed: ${res.status} ${res.statusText}`;
  const contentType = res.headers.get('content-type');
  if (contentType?.includes('application/json')) {
    try {
      const data = await res.json();
      if (data != null && typeof data === 'object' && 'detail' in data) {
        detail = data.detail as ApiErrorDetail;
      }
    } catch {
      // keep default detail
    }
  }
  return new ApiError(res.status, detail);
}

/** User-facing message when fetch fails (network error, CORS, etc.). */
export const NETWORK_ERROR_MESSAGE =
  'Unable to reach server. Check your connection and try again.';

/** True if error indicates backend unavailable or network failure (for retry/connection UI). */
export function isConnectionError(err: unknown): boolean {
  if (err instanceof ApiError) {
    return err.status === 0 || err.status === 502 || err.status === 503 || err.status === 504;
  }
  return false;
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const base = getBaseUrl();
  const url = path.startsWith('http') ? path : `${base}${path.startsWith('/') ? path : `/${path}`}`;
  let res: Response;
  try {
    res = await fetch(url, {
      ...options,
      headers: {
        Accept: 'application/json',
        ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
        ...options.headers,
      },
    });
  } catch {
    throw new ApiError(0, NETWORK_ERROR_MESSAGE, NETWORK_ERROR_MESSAGE);
  }
  if (!res.ok) {
    throw await parseErrorResponse(res);
  }
  const contentType = res.headers.get('content-type');
  if (contentType?.includes('application/json')) {
    return res.json() as Promise<T>;
  }
  return undefined as T;
}

export function apiUrl(path: string): string {
  const base = getBaseUrl();
  return path.startsWith('http') ? path : `${base}${path.startsWith('/') ? path : `/${path}`}`;
}

// --- Sessions (contracts/api.md) ---

export async function getSessions(): Promise<SessionList> {
  return apiFetch<SessionList>('/sessions');
}

export async function getSession(id: string): Promise<Session> {
  return apiFetch<Session>(`/sessions/${encodeURIComponent(id)}`);
}

export type CreateSessionBody = { name?: string | null; external_link?: string | null };
export type PatchSessionBody = { name?: string | null; external_link?: string | null };

export async function createSession(body: CreateSessionBody = {}): Promise<Session> {
  return apiFetch<Session>('/sessions', {
    method: 'POST',
    body: JSON.stringify({ name: body.name ?? null, external_link: body.external_link ?? null }),
  });
}

export async function patchSession(id: string, body: PatchSessionBody): Promise<Session> {
  return apiFetch<Session>(`/sessions/${encodeURIComponent(id)}`, {
    method: 'PATCH',
    body: JSON.stringify(body),
  });
}

// --- Upload (contracts/api.md) ---

/** POST /sessions/{session_id}/logs/upload — multipart/form-data, field "file" (.zip). Returns parsed UploadResult. */
export async function uploadLogs(sessionId: string, file: File): Promise<UploadResult> {
  const form = new FormData();
  form.append('file', file);
  const raw = await apiFetch<unknown>(`/sessions/${encodeURIComponent(sessionId)}/logs/upload`, {
    method: 'POST',
    body: form,
  });
  return UploadResultSchema.parse(raw);
}

/** GET /sessions/{session_id}/upload-summary — last upload result for session. Returns null on 404. */
export async function getUploadSummary(sessionId: string): Promise<UploadResult | null> {
  try {
    const raw = await apiFetch<unknown>(
      `/sessions/${encodeURIComponent(sessionId)}/upload-summary`
    );
    return UploadResultSchema.parse(raw);
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) return null;
    throw err;
  }
}

// --- Logs query (contracts/api.md) ---

/** POST /sessions/{session_id}/logs/query — body: start, end, limit, service, environment, log_level. Returns parsed LogsQueryResponse. */
export async function queryLogs(
  sessionId: string,
  body: LogsQueryRequest
): Promise<LogsQueryResponse> {
  const raw = await apiFetch<unknown>(
    `/sessions/${encodeURIComponent(sessionId)}/logs/query`,
    {
      method: 'POST',
      body: JSON.stringify({
        start: body.start ?? null,
        end: body.end ?? null,
        limit: body.limit ?? 100,
        service: body.service ?? null,
        environment: body.environment ?? null,
        log_level: body.log_level ?? null,
      }),
    }
  );
  return LogsQueryResponseSchema.parse(raw);
}

// --- Logs range (for Grafana Explore time window) ---

export type LogsRangeResponse = { from_ms: number; to_ms: number };

/** GET /sessions/{session_id}/logs/range — time extent of session logs (ms). 404 if no logs. */
export async function getLogsRange(sessionId: string): Promise<LogsRangeResponse> {
  return apiFetch<LogsRangeResponse>(
    `/sessions/${encodeURIComponent(sessionId)}/logs/range`
  );
}

// --- Knowledge (contracts/api.md) ---

export type KnowledgeIngestBody = { sources?: string[] };

/** POST /knowledge/ingest — start background ingest. Returns 202; poll GET /knowledge/ingest/status. */
export async function startKnowledgeIngest(
  body: KnowledgeIngestBody = {}
): Promise<{ message: string }> {
  return apiFetch<{ message: string }>('/knowledge/ingest', {
    method: 'POST',
    body: JSON.stringify({ sources: body.sources ?? [] }),
  });
}

/** GET /knowledge/ingest/status — running | idle, last_result, error. */
export async function getKnowledgeIngestStatus(): Promise<KnowledgeIngestStatus> {
  const raw = await apiFetch<unknown>('/knowledge/ingest/status');
  return KnowledgeIngestStatusSchema.parse(raw);
}

export type KnowledgeSearchBody = { query: string; limit?: number };

/** POST /knowledge/search — semantic search; returns chunks with content, source_path, metadata. */
export async function searchKnowledge(
  body: KnowledgeSearchBody
): Promise<KnowledgeSearchResponse> {
  const raw = await apiFetch<unknown>('/knowledge/search', {
    method: 'POST',
    body: JSON.stringify({
      query: body.query,
      limit: body.limit ?? 10,
    }),
  });
  return KnowledgeSearchResponseSchema.parse(raw);
}

// --- Reports (contracts/api.md) ---

/** GET /sessions/{session_id}/reports — list reports (no content). */
export async function getReports(sessionId: string): Promise<ReportList> {
  const raw = await apiFetch<unknown>(
    `/sessions/${encodeURIComponent(sessionId)}/reports`
  );
  return ReportListSchema.parse(raw);
}

/** GET /sessions/{session_id}/reports/{report_id} — single report with content (empty while generating). */
export async function getReport(
  sessionId: string,
  reportId: string
): Promise<Report> {
  const raw = await apiFetch<unknown>(
    `/sessions/${encodeURIComponent(sessionId)}/reports/${encodeURIComponent(reportId)}`
  );
  return ReportSchema.parse(raw);
}

export type GenerateReportBody = { question: string };

/** POST /sessions/{session_id}/reports/generate — start generation; returns 202 with report id. Poll GET report until content present. */
export async function generateReport(
  sessionId: string,
  body: GenerateReportBody
): Promise<{ id: string; session_id: string; created_at: string; content: string | null }> {
  const raw = await apiFetch<unknown>(
    `/sessions/${encodeURIComponent(sessionId)}/reports/generate`,
    {
      method: 'POST',
      body: JSON.stringify({ question: body.question }),
    }
  );
  return GenerateReportResponseSchema.parse(raw) as GenerateReportResponse;
}

/** GET /sessions/{session_id}/reports/{report_id}/export?format=markdown|pdf — blob download. */
export async function exportReport(
  sessionId: string,
  reportId: string,
  format: 'markdown' | 'pdf'
): Promise<Blob> {
  const url = apiUrl(
    `/sessions/${encodeURIComponent(sessionId)}/reports/${encodeURIComponent(reportId)}/export?format=${format}`
  );
  const res = await fetch(url, { credentials: 'same-origin' });
  if (!res.ok) {
    const contentType = res.headers.get('content-type');
    if (contentType?.includes('application/json')) {
      const data = await res.json().catch(() => ({}));
      const detail = data?.detail ?? res.statusText;
      throw new ApiError(res.status, typeof detail === 'string' ? detail : JSON.stringify(detail));
    }
    throw new ApiError(res.status, `${res.status} ${res.statusText}`);
  }
  return res.blob();
}

/** Trigger browser download of a blob (e.g. from exportReport). */
export function downloadBlob(blob: Blob, filename: string): void {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}
