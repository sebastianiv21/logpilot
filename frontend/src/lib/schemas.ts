/**
 * Zod schemas for API request/response types per data-model.md and contracts/api.md.
 */

import { z } from 'zod';

// --- Session ---
export const SessionSchema = z.object({
  id: z.string(),
  name: z.string().nullable(),
  external_link: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});
export type Session = z.infer<typeof SessionSchema>;

export const SessionListSchema = z.object({
  sessions: z.array(SessionSchema),
});
export type SessionList = z.infer<typeof SessionListSchema>;

/** Form schema for create session: optional name and external link. */
export const CreateSessionFormSchema = z.object({
  name: z.string().max(500).optional().or(z.literal('')),
  external_link: z.string().max(2000).optional().or(z.literal('')),
});
export type CreateSessionFormValues = z.infer<typeof CreateSessionFormSchema>;

/** Form schema for edit session (PATCH): optional name and external link. */
export const EditSessionFormSchema = z.object({
  name: z.string().max(500).optional().or(z.literal('')),
  external_link: z.string().max(2000).optional().or(z.literal('')),
});
export type EditSessionFormValues = z.infer<typeof EditSessionFormSchema>;

// --- Upload result ---
// Backend may return "success" | "partial" | "failed" (partial when some files/lines skipped or rejected)
export const UploadResultSchema = z.object({
  status: z.enum(['success', 'failed', 'partial']),
  files_processed: z.number(),
  files_skipped: z.number(),
  lines_parsed: z.number(),
  lines_rejected: z.number(),
  session_id: z.string(),
  error: z.string().nullable(),
});
export type UploadResult = z.infer<typeof UploadResultSchema>;

// --- Logs query ---
export const LogRecordSchema = z.object({
  timestamp_ns: z.number(),
  raw_message: z.string(),
}).passthrough();
export type LogRecord = z.infer<typeof LogRecordSchema>;

export const LogsQueryResponseSchema = z.object({
  logs: z.array(LogRecordSchema),
});
export type LogsQueryResponse = z.infer<typeof LogsQueryResponseSchema>;

export const LogsQueryRequestSchema = z.object({
  start: z.string().nullable().optional(),
  end: z.string().nullable().optional(),
  limit: z.number().min(1).max(1000).optional(),
  service: z.string().nullable().optional(),
  environment: z.string().nullable().optional(),
  log_level: z.string().nullable().optional(),
});
export type LogsQueryRequest = z.infer<typeof LogsQueryRequestSchema>;

/** Form schema for log search: optional start/end (ISO or empty), optional filters, limit. */
export const LogSearchFormSchema = z.object({
  start: z.string().optional(),
  end: z.string().optional(),
  limit: z.number().min(1).max(1000),
  service: z.string().max(200).optional().or(z.literal('')),
  environment: z.string().max(200).optional().or(z.literal('')),
  log_level: z.string().max(50).optional().or(z.literal('')),
});
export type LogSearchFormValues = z.infer<typeof LogSearchFormSchema>;

// --- Report ---
export const ReportSchema = z.object({
  id: z.string(),
  session_id: z.string(),
  content: z.string(),
  created_at: z.string(),
});
export type Report = z.infer<typeof ReportSchema>;

export const ReportListItemSchema = z.object({
  id: z.string(),
  session_id: z.string(),
  created_at: z.string(),
});
export type ReportListItem = z.infer<typeof ReportListItemSchema>;

export const ReportListSchema = z.object({
  reports: z.array(ReportListItemSchema),
});
export type ReportList = z.infer<typeof ReportListSchema>;

// --- Knowledge ---
export const KnowledgeIngestStatusSchema = z.object({
  status: z.enum(['running', 'idle']),
  last_result: z
    .object({
      chunks_ingested: z.number().optional(),
      files_processed: z.number().optional(),
    })
    .nullable()
    .optional(),
  error: z.string().nullable().optional(),
});
export type KnowledgeIngestStatus = z.infer<typeof KnowledgeIngestStatusSchema>;

export const KnowledgeSearchChunkSchema = z.object({
  content: z.string(),
  source_path: z.string(),
  metadata: z.record(z.string(), z.unknown()).optional(),
});
export type KnowledgeSearchChunk = z.infer<typeof KnowledgeSearchChunkSchema>;

export const KnowledgeSearchResponseSchema = z.object({
  chunks: z.array(KnowledgeSearchChunkSchema),
});
export type KnowledgeSearchResponse = z.infer<typeof KnowledgeSearchResponseSchema>;

/** Form schema for knowledge search: query (min 1), optional limit (1–100). */
export const KnowledgeSearchFormSchema = z.object({
  query: z.string().min(1, 'Enter a search query'),
  limit: z.number().min(1).max(100).optional(),
});
export type KnowledgeSearchFormValues = z.infer<typeof KnowledgeSearchFormSchema>;
