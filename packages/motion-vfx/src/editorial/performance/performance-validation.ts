import { z } from "zod";

/**
 * RF-056: Zod Validation Schemas for Performance and Semantic Trimming Engine
 */

export const PerformanceMarkerSchema = z.enum([
  "BREATH",
  "LAUGH",
  "HESITATION",
  "REFLECTIVE_PAUSE",
  "FILLER",
  "STUTTER",
  "FALSE_START",
  "WORD_REPETITION",
  "TECHNICAL_ERROR",
  "EMPHATIC_PAUSE",
  "EMOTIONAL_REACTION",
  "UNCERTAINTY",
]);

export const PerformanceSegmentSchema = z.object({
  id: z.string().min(1),
  sourceClipId: z.string().min(1),
  startSeconds: z.number().min(0),
  endSeconds: z.number().positive(),
  transcript: z.string(),
  confidence: z.number().min(0).max(1),
  markers: z.array(PerformanceMarkerSchema).default([]),
  evidenceProtection: z.boolean().optional(),
  beatId: z.string().optional(),
  narrativeRole: z.string().optional(),
}).refine((s) => s.endSeconds > s.startSeconds, {
  message: "endSeconds must be strictly greater than startSeconds",
});

export const RedundancyRecommendationSchema = z.enum(["KEEP_BOTH", "KEEP_A", "KEEP_B", "REVIEW"]);

export const RedundancyCandidateSchema = z.object({
  id: z.string().min(1),
  segmentAId: z.string().min(1),
  segmentBId: z.string().min(1),
  semanticSimilarity: z.number().min(0).max(1),
  informationOverlap: z.number().min(0).max(1),
  temporalDistanceSeconds: z.number().min(0),
  narrativeRoleA: z.string().optional(),
  narrativeRoleB: z.string().optional(),
  redundancyScore: z.number().min(0).max(1),
  recommendation: RedundancyRecommendationSchema,
  reason: z.string(),
  confidence: z.number().min(0).max(1),
});

export const PreservationActionSchema = z.enum(["PRESERVE", "TRIM", "REVIEW"]);

export const PreservationDecisionSchema = z.object({
  marker: PerformanceMarkerSchema,
  action: PreservationActionSchema,
  preservationScore: z.number().min(0).max(1),
  authenticityScore: z.number().min(0).max(1),
  technicalDefectScore: z.number().min(0).max(1),
  reason: z.string(),
  confidence: z.number().min(0).max(1),
});

export const TakeCandidateSchema = z.object({
  id: z.string().min(1),
  transcript: z.string(),
  sourceClipId: z.string().min(1),
  startSeconds: z.number().min(0),
  endSeconds: z.number().positive(),
  semanticIntegrity: z.number().min(0).max(1),
  phoneticClarity: z.number().min(0).max(1),
  vocalEnergy: z.number().min(0).max(1),
  visualStability: z.number().min(0).max(1),
  eyeContact: z.number().min(0).max(1),
  naturalPerformance: z.number().min(0).max(1),
  continuity: z.number().min(0).max(1),
  audioQuality: z.number().min(0).max(1),
}).refine((t) => t.endSeconds > t.startSeconds, {
  message: "endSeconds must be strictly greater than startSeconds",
});

export const BestTakeSelectionSchema = z.object({
  takeGroupId: z.string().min(1),
  selectedTakeId: z.string().min(1),
  winnerScore: z.number().min(0).max(1),
  runnerUpScore: z.number().min(0).max(1).optional(),
  scoreDifference: z.number().min(0).max(1).optional(),
  isAutoSelected: z.boolean(),
  desempateApplied: z.string().optional(),
  recommendation: z.enum(["SELECT", "REVIEW"]),
});

export const TrimActionSchema = z.enum(["KEEP", "TRIM", "REPLACE_TAKE", "MERGE", "REVIEW"]);

export const AudioTransitionProposalSchema = z.object({
  startSeconds: z.number().min(0),
  durationSeconds: z.number().positive(),
  type: z.literal("MICRO_CROSSFADE"),
});

export const TrimProposalSchema = z.object({
  id: z.string().min(1),
  sourceClipId: z.string().min(1),
  startSeconds: z.number().min(0),
  endSeconds: z.number().positive(),
  action: TrimActionSchema,
  reason: z.string(),
  confidence: z.number().min(0).max(1),
  audioTransition: AudioTransitionProposalSchema.optional(),
}).refine((p) => p.endSeconds > p.startSeconds, {
  message: "endSeconds must be strictly greater than startSeconds",
});

export const PerformanceReviewItemSchema = z.object({
  id: z.string().min(1),
  priority: z.enum(["HIGH", "MEDIUM", "LOW"]),
  reason: z.string(),
  candidateIds: z.array(z.string()),
  confidence: z.number().min(0).max(1),
  affectedRange: z.object({
    startSeconds: z.number().min(0),
    endSeconds: z.number().positive(),
  }),
});

export const TrimmingMetricsSchema = z.object({
  originalDurationSeconds: z.number().min(0),
  finalDurationSeconds: z.number().min(0),
  removedDurationSeconds: z.number().min(0),
  reductionRatio: z.number().min(0).max(1),
  preservedSemanticCoverage: z.number().min(0).max(1),
  preservedPerformanceCoverage: z.number().min(0).max(1),
});

export const IntelligentTrimReportSchema = z.object({
  engineVersion: z.string(),
  processedSegments: z.number().int().min(0),
  redundancyCandidates: z.number().int().min(0),
  trimsProposed: z.number().int().min(0),
  trimsAccepted: z.number().int().min(0),
  trimsRejected: z.number().int().min(0),
  takesEvaluated: z.number().int().min(0),
  automaticTakeSelections: z.number().int().min(0),
  reviewItems: z.number().int().min(0),
  metrics: TrimmingMetricsSchema,
  proposals: z.array(TrimProposalSchema),
  takeSelections: z.array(BestTakeSelectionSchema),
  redundancy: z.array(RedundancyCandidateSchema),
  preservation: z.array(PreservationDecisionSchema),
  reviewQueue: z.array(PerformanceReviewItemSchema),
  status: z.enum(["WITHIN_SAFE_BOUNDS", "PROPOSALS_READY", "REVIEW_REQUIRED"]),
  checksumSha256: z.string().length(64),
});
