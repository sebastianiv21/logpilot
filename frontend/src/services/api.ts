/**
 * API client for LogPilot backend.
 * Base URL from VITE_API_BASE; fetch wrapper with JSON and error handling.
 */

import type { Session, SessionList } from '../lib/schemas';

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

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const base = getBaseUrl();
  const url = path.startsWith('http') ? path : `${base}${path.startsWith('/') ? path : `/${path}`}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      Accept: 'application/json',
      ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
      ...options.headers,
    },
  });
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
