import { z } from "zod";
import { ShotClassificationScaleSchema } from "../contracts/knowledge-graph.types.js";

/**
 * REQ-013 & REQ-014: Semantic B-Roll candidate asset metadata.
 */
export const SemanticBRollCandidateSchema = z.object({
  id: z.string().min(1),
  assetId: z.string().min(1),
  description: z.string(),
  tags: z.array(z.string()).default([]),
  semanticConcepts: z.array(z.string()).default([]),
  emotionalTone: z.enum(["NEUTRAL", "TENSE", "HOPEFUL", "MELANCHOLY", "ENERGETIC", "CALM"]).default("NEUTRAL"),
  durationSeconds: z.number().positive(),
  scale: ShotClassificationScaleSchema.default("WIDE"),
  categoryFamily: z.string().default("generic"),
  technicalQuality: z.number().min(0.0).max(1.0).default(0.9),
});

export type SemanticBRollCandidate = z.infer<typeof SemanticBRollCandidateSchema>;

/**
 * Detailed multi-criteria scoring breakdown.
 */
export const SemanticMatchScoreSchema = z.object({
  conceptualMatch: z.number().min(0.0).max(1.0),
  emotionalMatch: z.number().min(0.0).max(1.0),
  narrativeRelevance: z.number().min(0.0).max(1.0),
  repetitionPenalty: z.number().min(0.0).max(1.0), // 0 = never used, 1 = severely overused
  finalScore: z.number().min(0.0).max(100.0),
});

export type SemanticMatchScore = z.infer<typeof SemanticMatchScoreSchema>;

/**
 * Evaluated candidate with its calculated scores.
 */
export const RankedSemanticBRollCandidateSchema = z.object({
  candidate: SemanticBRollCandidateSchema,
  score: SemanticMatchScoreSchema,
});

export type RankedSemanticBRollCandidate = z.infer<typeof RankedSemanticBRollCandidateSchema>;

/**
 * Master result of B-Roll selection.
 */
export const BRollSelectionResultSchema = z.object({
  selectedCandidate: SemanticBRollCandidateSchema.nullable(),
  matchScore: SemanticMatchScoreSchema.nullable(),
  rankedAlternatives: z.array(RankedSemanticBRollCandidateSchema),
  queryContext: z.object({
    spokenSentence: z.string(),
    requiredDurationSeconds: z.number().positive(),
    targetTone: z.string().optional(),
  }),
});

export type BRollSelectionResult = z.infer<typeof BRollSelectionResultSchema>;
