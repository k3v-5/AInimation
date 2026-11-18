import { z } from "zod";
import { DocumentaryBeatTypeSchema } from "./narrative.types.js";

/**
 * Supported promotional trailer formats.
 */
export const TrailerFormatSchema = z.enum([
  "15s_teaser",
  "30s_promo",
  "60s_trailer",
  "90s_epic",
]);

export type TrailerFormat = z.infer<typeof TrailerFormatSchema>;

/**
 * Editorial narrative purpose of a cut segment in the trailer.
 */
export const TrailerPurposeSchema = z.enum([
  "HOOK_PUNCH",
  "INTRIGUE_BUILD",
  "EVIDENCE_FLASH",
  "CLIMAX_DROP",
  "TITLE_CALL_TO_ACTION",
]);

export type TrailerPurpose = z.infer<typeof TrailerPurposeSchema>;

/**
 * Synchronized musical or sound impact cue.
 */
export const MusicCueTypeSchema = z.enum([
  "RISER",
  "HIT",
  "DROP",
  "SILENCE_BREAKER",
  "BED",
]);

export type MusicCueType = z.infer<typeof MusicCueTypeSchema>;

/**
 * Cut segment inside a compiled promotional trailer.
 */
export const TrailerCutSegmentSchema = z.object({
  id: z.string().min(1),
  sourceBeatType: DocumentaryBeatTypeSchema,
  sceneId: z.string().min(1),
  sourceStartSeconds: z.number().nonnegative(),
  sourceEndSeconds: z.number().nonnegative(),
  trailerStartSeconds: z.number().nonnegative(),
  trailerEndSeconds: z.number().nonnegative(),
  durationSeconds: z.number().positive(),
  purpose: TrailerPurposeSchema,
  soundbiteText: z.string().optional(),
  musicCue: MusicCueTypeSchema.default("BED"),
});

export type TrailerCutSegment = z.infer<typeof TrailerCutSegmentSchema>;

/**
 * Quantitative metrics analyzing the first 3 to 6 seconds for audience retention.
 */
export const SocialHookMetricsSchema = z.object({
  windowDurationSeconds: z.number().min(2.0).max(10.0),
  visualPaceScore: z.number().min(0.0).max(100.0),
  verbalIntrigueScore: z.number().min(0.0).max(100.0),
  acousticImpactScore: z.number().min(0.0).max(100.0),
  retentionPredictionScore: z.number().min(0.0).max(100.0),
  cutTimestamps: z.array(z.number().nonnegative()),
  intrigueWordsDetected: z.array(z.string()),
  recommendations: z.array(z.string()),
});

export type SocialHookMetrics = z.infer<typeof SocialHookMetricsSchema>;

/**
 * Fully compiled, immutable trailer plan.
 */
export const TrailerPlanSchema = z.object({
  id: z.string().min(1),
  projectId: z.string().min(1),
  format: TrailerFormatSchema,
  targetDurationSeconds: z.number().positive(),
  actualDurationSeconds: z.number().positive(),
  segments: z.array(TrailerCutSegmentSchema),
  socialHookMetrics: SocialHookMetricsSchema,
  callToActionText: z.string(),
  checksumSha256: z.string().length(64),
});

export type TrailerPlan = z.infer<typeof TrailerPlanSchema>;
