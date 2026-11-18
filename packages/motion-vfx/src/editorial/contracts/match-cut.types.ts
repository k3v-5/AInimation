import { z } from "zod";

/**
 * Categorization of formal matching criteria between two shots.
 */
export const MatchCutTypeSchema = z.enum([
  "GEOMETRIC",
  "CHROMATIC",
  "KINETIC",
  "AUDIO_SEMANTIC",
  "COMPOSITE",
]);

export type MatchCutType = z.infer<typeof MatchCutTypeSchema>;

/**
 * Recognizable geometric primitives for visual shape matching.
 */
export const GeometricShapeSchema = z.enum([
  "CIRCLE",
  "RECTANGLE",
  "LINEAR_HORIZON",
  "SILHOUETTE",
  "EYE",
  "SPIRAL",
]);

export type GeometricShape = z.infer<typeof GeometricShapeSchema>;

export const NormalizedPointSchema = z.object({
  x: z.number().min(0.0).max(1.0),
  y: z.number().min(0.0).max(1.0),
});

export type NormalizedPoint = z.infer<typeof NormalizedPointSchema>;

/**
 * Extracted formal audiovisual features of a shot for match cut detection.
 */
export const FormalVisualFeaturesSchema = z.object({
  primaryShape: GeometricShapeSchema.optional(),
  shapeCenter: NormalizedPointSchema.optional(),
  shapeRadius: z.number().min(0.0).max(1.0).optional(),
  dominantColorHue: z.number().min(0.0).max(360.0).optional(), // 0-360 degrees
  motionVectorDegrees: z.number().min(0.0).max(360.0).optional(), // 0-360 degrees
  motionSpeed: z.number().min(0.0).max(1.0).optional(), // normalized velocity
  acousticMotif: z.string().optional(),
});

export type FormalVisualFeatures = z.infer<typeof FormalVisualFeaturesSchema>;

/**
 * Spatial offset and scale adjustment to align visual focal points at the cut point.
 */
export const SpatialOffsetCorrectionSchema = z.object({
  deltaX: z.number(),
  deltaY: z.number(),
  scaleCorrectionFactor: z.number().positive(),
});

export type SpatialOffsetCorrection = z.infer<typeof SpatialOffsetCorrectionSchema>;

/**
 * Evaluation result of a match cut candidate between two adjacent shots.
 */
export const MatchCutCandidateSchema = z.object({
  id: z.string().min(1),
  outgoingShotId: z.string().min(1),
  incomingShotId: z.string().min(1),
  type: MatchCutTypeSchema,
  matchScore: z.number().min(0.0).max(100.0),
  geometricAffinity: z.number().min(0.0).max(100.0),
  chromaticAffinity: z.number().min(0.0).max(100.0),
  kineticAffinity: z.number().min(0.0).max(100.0),
  soundAffinity: z.number().min(0.0).max(100.0),
  spatialOffset: SpatialOffsetCorrectionSchema,
  explanation: z.string(),
  isViableMatchCut: z.boolean(),
});

export type MatchCutCandidate = z.infer<typeof MatchCutCandidateSchema>;

/**
 * Report detailing all match cut opportunities detected in an editorial sequence.
 */
export const MatchCutReportSchema = z.object({
  sequenceId: z.string().min(1),
  totalPairsEvaluated: z.number().int().nonnegative(),
  viableMatchesCount: z.number().int().nonnegative(),
  candidates: z.array(MatchCutCandidateSchema),
  checksumSha256: z.string().length(64),
});

export type MatchCutReport = z.infer<typeof MatchCutReportSchema>;
