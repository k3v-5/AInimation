import { z } from "zod";

export const QASeveritySchema = z.enum(["BLOCKING", "WARNING", "SUGGESTION"]);
export type QASeverity = z.infer<typeof QASeveritySchema>;

export const QAEvidenceSchema = z.object({
  field: z.string().min(1),
  actualValue: z.unknown(),
  expectedValue: z.unknown().optional(),
});
export type QAEvidence = z.infer<typeof QAEvidenceSchema>;

export const EditorialQAFindingSchema = z.object({
  id: z.string().min(1),
  ruleId: z.string().min(1),
  severity: QASeveritySchema,
  timestampSeconds: z.number().finite().nonnegative().optional(),
  durationSeconds: z.number().finite().positive().optional(),
  message: z.string().min(1),
  reason: z.string().min(1),
  evidence: z.array(QAEvidenceSchema).default([]),
  confidence: z.number().finite().min(0.0).max(1.0).default(1.0),
  autoFixAvailable: z.boolean().default(false),
  suggestedFix: z.string().optional(),
  deterministicFingerprint: z.string().optional(),
});
export type EditorialQAFinding = z.infer<typeof EditorialQAFindingSchema>;

export const ReviewUrgencySchema = z.enum(["CRITICAL", "HIGH", "MEDIUM", "LOW"]);
export type ReviewUrgency = z.infer<typeof ReviewUrgencySchema>;

export const ReviewItemStatusSchema = z.enum(["PENDING", "APPROVED", "REJECTED", "DEFERRED"]);
export type ReviewItemStatus = z.infer<typeof ReviewItemStatusSchema>;

export const HumanReviewItemSchema = z.object({
  id: z.string().min(1),
  priority: z.number().finite().min(0.0).max(1.0),
  category: z.string().min(1),
  severity: QASeveritySchema,
  confidence: z.number().finite().min(0.0).max(1.0),
  title: z.string().min(1),
  description: z.string().min(1),
  affectedTimestamps: z.array(
    z.object({
      startSeconds: z.number().finite().nonnegative(),
      durationSeconds: z.number().finite().positive(),
    })
  ).default([]),
  proposedAction: z.string().optional(),
  evidence: z.array(QAEvidenceSchema).default([]),
  status: ReviewItemStatusSchema.default("PENDING"),
});
export type HumanReviewItem = z.infer<typeof HumanReviewItemSchema>;

export const EditorialAuditReportSchema = z.object({
  schemaVersion: z.string().default("1.0.0"),
  engineVersion: z.string().default("v4.0.0-editorial-master"),
  generatedAt: z.string().optional(),
  findings: z.array(EditorialQAFindingSchema),
  blockingCount: z.number().int().nonnegative(),
  warningCount: z.number().int().nonnegative(),
  suggestionCount: z.number().int().nonnegative(),
  canExport: z.boolean(),
  overallScore: z.number().finite().min(0.0).max(100.0),
  confidenceScore: z.number().finite().min(0.0).max(1.0),
  reviewQueue: z.array(HumanReviewItemSchema).default([]),
  checksumSha256: z.string().length(64),
});
export type EditorialAuditReport = z.infer<typeof EditorialAuditReportSchema>;

export const EditorialChangeOperationSchema = z.enum(["ADD", "REMOVE", "REPLACE", "MOVE"]);
export type EditorialChangeOperation = z.infer<typeof EditorialChangeOperationSchema>;

export const EditorialChangeSchema = z.object({
  path: z.string().min(1),
  operation: EditorialChangeOperationSchema,
  before: z.unknown().optional(),
  after: z.unknown().optional(),
});
export type EditorialChange = z.infer<typeof EditorialChangeSchema>;

export const EditorialImpactSchema = z.object({
  durationDeltaSeconds: z.number().finite(),
  cutCountDelta: z.number().int(),
  pacingAlignmentDelta: z.number().finite(),
  contrastScoreDelta: z.number().finite(),
  cognitiveLoadDelta: z.number().finite(),
  evidenceIntegrityDelta: z.number().finite(),
  affectedTimeRanges: z.array(
    z.object({
      startSeconds: z.number().finite().nonnegative(),
      durationSeconds: z.number().finite().positive(),
    })
  ).default([]),
});
export type EditorialImpact = z.infer<typeof EditorialImpactSchema>;

export const DiffRiskLevelSchema = z.enum(["LOW", "MEDIUM", "HIGH", "CRITICAL"]);
export type DiffRiskLevel = z.infer<typeof DiffRiskLevelSchema>;

export const EditorialDiffSchema = z.object({
  id: z.string().min(1),
  baseChecksum: z.string().length(64),
  candidateChecksum: z.string().length(64),
  changes: z.array(EditorialChangeSchema),
  impact: EditorialImpactSchema,
  riskLevel: DiffRiskLevelSchema,
  checksumSha256: z.string().length(64),
});
export type EditorialDiff = z.infer<typeof EditorialDiffSchema>;

export const EditorialProposalSchema = z.object({
  id: z.string().min(1),
  type: z.string().min(1),
  reason: z.string().min(1),
  confidence: z.number().finite().min(0.0).max(1.0),
  affectedRange: z
    .object({
      startSeconds: z.number().finite().nonnegative(),
      durationSeconds: z.number().finite().positive(),
    })
    .optional(),
  beforeChecksum: z.string().length(64),
  candidatePatch: z.unknown(),
});
export type EditorialProposal = z.infer<typeof EditorialProposalSchema>;
