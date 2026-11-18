import { z } from "zod";

/**
 * REQ-036: Types of automated editorial QA checks.
 */
export const QACheckTypeSchema = z.enum([
  "FLASH_FRAME",                 // Video clip with duration < 0.1s
  "TRACK_GAP",                   // Unintended gap in primary video track
  "AUDIO_CLIPPING",              // Volume level exceeds 0 dB
  "DIALOGUE_LUFS_OUT_OF_BOUNDS", // Dialogue level diverges > 2.5 LUFS from target
  "SAFE_ZONE_VIOLATION",         // Graphic elements breach 9:16 safe zones
  "MISSING_MEDIA_SOURCE",        // Missing or empty assetId
]);

export type QACheckType = z.infer<typeof QACheckTypeSchema>;

export const QASeveritySchema = z.enum(["INFO", "WARNING", "BLOCKING"]);
export type QASeverity = z.infer<typeof QASeveritySchema>;

/**
 * Single QA audit issue.
 */
export const QAIssueSchema = z.object({
  id: z.string().min(1),
  checkType: QACheckTypeSchema,
  severity: QASeveritySchema,
  trackId: z.string().optional(),
  clipId: z.string().optional(),
  timestampSeconds: z.number().min(0),
  description: z.string().min(1),
  suggestedFix: z.string().min(1),
});

export type QAIssue = z.infer<typeof QAIssueSchema>;

/**
 * REQ-037: Comprehensive Editorial QA Audit Report.
 */
export const QAReportSchema = z.object({
  projectId: z.string().min(1),
  qaScore: z.number().min(0.0).max(100.0),
  totalChecksRun: z.number().int().min(0),
  issues: z.array(QAIssueSchema),
  isReadyForExport: z.boolean(),
  auditedAt: z.string().datetime(),
});

export type QAReport = z.infer<typeof QAReportSchema>;
