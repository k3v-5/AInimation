import { z } from "zod";

/**
 * REQ-046: Attention profile parameters governing the differential decay and baseline.
 */
export const AttentionProfileSchema = z.object({
  initialAttention: z.number().finite().min(0.0).max(1.0).default(0.85),
  baselineAttention: z.number().finite().min(0.0).max(1.0).default(0.40),
  decayLambda: z.number().finite().nonnegative().default(0.035),
  simulationStepSeconds: z.number().finite().positive().default(0.1),
  reportingStepSeconds: z.number().finite().positive().default(1.0),
});

export type AttentionProfile = z.infer<typeof AttentionProfileSchema>;

export const AttentionPointSchema = z.object({
  timestampSeconds: z.number().finite().nonnegative(),
  attentionScore: z.number().finite().min(0.0).max(1.0),
});

export type AttentionPoint = z.infer<typeof AttentionPointSchema>;

export const AttentionDipAlertSchema = z.object({
  startTimeSeconds: z.number().finite().nonnegative(),
  endTimeSeconds: z.number().finite().nonnegative(),
  minScore: z.number().finite().min(0.0).max(1.0),
  recommendedFix: z.string().min(1),
});

export type AttentionDipAlert = z.infer<typeof AttentionDipAlertSchema>;

export const AudienceAttentionReportSchema = z.object({
  averageAttention: z.number().finite().min(0.0).max(1.0),
  minAttention: z.number().finite().min(0.0).max(1.0),
  dipAlerts: z.array(AttentionDipAlertSchema),
  attentionPoints: z.array(AttentionPointSchema),
  checksumSha256: z.string().length(64),
});

export type AudienceAttentionReport = z.infer<typeof AudienceAttentionReportSchema>;

/**
 * REQ-047: Cognitive Load contracts.
 */
export const CognitiveMitigationTypeSchema = z.enum([
  "SHIFT_GRAPHIC",
  "DUCK_AUDIO",
  "SPLIT_DENSE_SEGMENT",
]);

export type CognitiveMitigationType = z.infer<typeof CognitiveMitigationTypeSchema>;

export const CognitiveMitigationProposalSchema = z.object({
  id: z.string().min(1),
  timestampSeconds: z.number().finite().nonnegative(),
  type: CognitiveMitigationTypeSchema,
  offsetSeconds: z.number().finite().optional(),
  gainDeltaDb: z.number().finite().optional(),
  reason: z.string().min(1),
  confidence: z.number().finite().min(0.0).max(1.0),
});

export type CognitiveMitigationProposal = z.infer<typeof CognitiveMitigationProposalSchema>;

export const CognitiveOverloadAlertSchema = z.object({
  timestampSeconds: z.number().finite().nonnegative(),
  durationSeconds: z.number().finite().positive(),
  loadIndex: z.number().finite().min(0.0).max(1.0),
  primaryCause: z.string().min(1),
});

export type CognitiveOverloadAlert = z.infer<typeof CognitiveOverloadAlertSchema>;

export const CognitiveLoadReportSchema = z.object({
  averageLoad: z.number().finite().min(0.0).max(1.0),
  peakLoad: z.number().finite().min(0.0).max(1.0),
  detectedOverloadsCount: z.number().int().nonnegative(),
  overloadAlerts: z.array(CognitiveOverloadAlertSchema),
  recommendedMitigations: z.array(CognitiveMitigationProposalSchema),
  checksumSha256: z.string().length(64),
});

export type CognitiveLoadReport = z.infer<typeof CognitiveLoadReportSchema>;

/**
 * REQ-048: Dramatic tension scale and contrast report.
 */
export const TensionLevelSchema = z.enum([
  "LOW",
  "MEDIUM",
  "HIGH",
  "PEAK",
  "RELEASE",
]);

export type TensionLevel = z.infer<typeof TensionLevelSchema>;

export const TensionRunSchema = z.object({
  level: z.enum(["HIGH", "PEAK"]),
  startBeatIndex: z.number().int().nonnegative(),
  endBeatIndex: z.number().int().nonnegative(),
  durationSeconds: z.number().finite().nonnegative(),
});

export type TensionRun = z.infer<typeof TensionRunSchema>;

export const EditorialContrastPenaltiesSchema = z.object({
  monotonyPenalty: z.number().finite().nonnegative(),
  stagnationPenalty: z.number().finite().nonnegative(),
  missingReleasePenalty: z.number().finite().nonnegative(),
  erraticPenalty: z.number().finite().nonnegative(),
});

export type EditorialContrastPenalties = z.infer<typeof EditorialContrastPenaltiesSchema>;

export const EditorialContrastReportSchema = z.object({
  contrastScore: z.number().finite().min(0.0).max(100.0),
  penalties: EditorialContrastPenaltiesSchema,
  monotonyRuns: z.array(TensionRunSchema),
  violations: z.array(z.string()),
  isValidContrast: z.boolean(),
  checksumSha256: z.string().length(64),
});

export type EditorialContrastReport = z.infer<typeof EditorialContrastReportSchema>;

/**
 * REQ-049: Pacing Profile and Alignment report.
 */
export const PacingProfileSchema = z.object({
  windowSeconds: z.number().finite().positive().default(6.0),
  maxCutsPerWindow: z.number().finite().positive().default(5.0),
});

export type PacingProfile = z.infer<typeof PacingProfileSchema>;

export const PacingDiscrepancySchema = z.object({
  timestampSeconds: z.number().finite().nonnegative(),
  delta: z.number().finite(),
  recommendation: z.string().min(1),
});

export type PacingDiscrepancy = z.infer<typeof PacingDiscrepancySchema>;

export const PacingAlignmentReportSchema = z.object({
  alignmentScore: z.number().finite().min(0.0).max(100.0),
  meanL1Distance: z.number().finite().min(0.0).max(1.0),
  discrepancies: z.array(PacingDiscrepancySchema),
  checksumSha256: z.string().length(64),
});

export type PacingAlignmentReport = z.infer<typeof PacingAlignmentReportSchema>;
