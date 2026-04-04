/**
 * Zod schemas for API request/response types per data-model.md and contracts/api.md.
 */

import { z } from 'zod';

// --- Session ---
export const SessionSchema = z.object({
  id: z.string(),
  name: z.string().nullable(),
  external_link: z.string().nullable(),
  is_pinned: z.boolean(),
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
  is_pinned: z.boolean().optional(),
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
  uploaded_file_name: z.string().nullable().optional(),
  updated_at: z.string().nullable().optional(),
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
  question: z.string().nullable().optional(),
  created_at: z.string(),
});
export type Report = z.infer<typeof ReportSchema>;

export const ReportListItemSchema = z.object({
  id: z.string(),
  session_id: z.string(),
  created_at: z.string(),
  question_preview: z.string().nullable().optional(),
  has_question: z.boolean(),
});
export type ReportListItem = z.infer<typeof ReportListItemSchema>;

export const ReportListSchema = z.object({
  reports: z.array(ReportListItemSchema),
});
export type ReportList = z.infer<typeof ReportListSchema>;

/** POST generate response: content is null until generation completes. */
export const GenerateReportResponseSchema = z.object({
  id: z.string(),
  session_id: z.string(),
  created_at: z.string(),
  content: z.string().nullable(),
});
export type GenerateReportResponse = z.infer<typeof GenerateReportResponseSchema>;

/** Form schema for report generation: question (min length 1). */
export const ReportGenerateFormSchema = z.object({
  question: z.string().min(1, 'Enter an incident question'),
});
export type ReportGenerateFormValues = z.infer<typeof ReportGenerateFormSchema>;

// --- Knowledge ---
export const KnowledgeSourceStatusSchema = z.object({
  source_key: z.enum(['code', 'docs']),
  display_name: z.string(),
  configured_paths: z.array(z.string()),
  status: z.enum(['idle', 'running', 'ready', 'failed']),
  last_started_at: z.string().nullable().optional(),
  last_completed_at: z.string().nullable().optional(),
  last_error: z.string().nullable().optional(),
  last_chunks_ingested: z.number().default(0),
  last_files_processed: z.number().default(0),
  last_files_skipped_unchanged: z.number().default(0),
  last_files_deleted: z.number().default(0),
  last_embedding_model: z.string().nullable().optional(),
  last_embedding_dimension: z.number().nullable().optional(),
  last_ingest_mode: z.enum(['incremental', 'force']).nullable().optional(),
});
export type KnowledgeSourceStatus = z.infer<typeof KnowledgeSourceStatusSchema>;

export const KnowledgeSourcesStatusSchema = z.object({
  sources: z.array(KnowledgeSourceStatusSchema),
});
export type KnowledgeSourcesStatus = z.infer<typeof KnowledgeSourcesStatusSchema>;

export const KnowledgeSearchChunkSchema = z.object({
  content: z.string(),
  source_path: z.string(),
  source_key: z.enum(['code', 'docs']).optional().default('docs'),
  metadata: z.record(z.string(), z.unknown()).optional(),
});
export type KnowledgeSearchChunk = z.infer<typeof KnowledgeSearchChunkSchema>;

export const KnowledgeSearchResponseSchema = z.object({
  chunks: z.array(KnowledgeSearchChunkSchema),
});
export type KnowledgeSearchResponse = z.infer<typeof KnowledgeSearchResponseSchema>;

/** Form schema for knowledge search: query (min 1). Result count is fixed; no user limit control. */
export const KnowledgeSearchFormSchema = z.object({
  query: z.string().min(1, 'Enter a search query'),
});
export type KnowledgeSearchFormValues = z.infer<typeof KnowledgeSearchFormSchema>;
