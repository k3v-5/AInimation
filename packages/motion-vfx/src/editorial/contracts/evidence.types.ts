import { z } from "zod";
import { ClaimStatusSchema } from "./knowledge-graph.types.js";

/**
 * REQ-009 & REQ-010: Citation Card for On-Screen Attribution.
 */
export const CitationStyleSchema = z.enum([
  "LOWER_THIRD",
  "FULL_CARD",
  "SIDE_BOX",
  "SUBTITLE_FOOTNOTE",
]);

export type CitationStyle = z.infer<typeof CitationStyleSchema>;

export const CitationCardSchema = z.object({
  id: z.string().min(1),
  claimId: z.string().min(1),
  sourceTitle: z.string().min(1),
  sourceAuthorOrOrg: z.string().min(1),
  publicationDate: z.string().optional(),
  urlOrArchiveId: z.string().optional(),
  timelineStartSeconds: z.number().nonnegative(),
  timelineEndSeconds: z.number().nonnegative(),
  speakerId: z.string().optional(),
  onScreenText: z.string().min(1),
  style: CitationStyleSchema.default("LOWER_THIRD"),
});

export type CitationCard = z.infer<typeof CitationCardSchema>;

/**
 * REQ-009 & REQ-010: Individual Claim Audit.
 */
export const ClaimAuditResultSchema = z.object({
  claimId: z.string().min(1),
  claimText: z.string().min(1),
  status: ClaimStatusSchema,
  hasEvidence: z.boolean(),
  evidenceCount: z.number().int().nonnegative(),
  requiresCitation: z.boolean(),
  hasCitation: z.boolean(),
  confidence: z.number().min(0.0).max(1.0),
  blockingIssue: z.boolean(),
  notes: z.string(),
});

export type ClaimAuditResult = z.infer<typeof ClaimAuditResultSchema>;

/**
 * REQ-009 & REQ-010: Master Evidence & Fact Checking Audit Report.
 */
export const EvidenceAuditReportSchema = z.object({
  projectId: z.string().min(1),
  totalClaims: z.number().int().nonnegative(),
  verifiedClaims: z.number().int().nonnegative(),
  unverifiedClaims: z.number().int().nonnegative(),
  missingSourceClaims: z.number().int().nonnegative(),
  evidenceIntegrityScore: z.number().min(0.0).max(100.0),
  audits: z.array(ClaimAuditResultSchema),
  citationCards: z.array(CitationCardSchema),
  checksumSha256: z.string().length(64),
});

export type EvidenceAuditReport = z.infer<typeof EvidenceAuditReportSchema>;
