import { z } from "zod";
import { RulePriorityTierSchema } from "./rule-precedence.types.js";

/**
 * REQ-003: Multidimensional Editorial Score.
 */
export const EditorialScoreSchema = z.object({
  narrativeValue: z.number().min(0.0).max(1.0),
  emotionalValue: z.number().min(0.0).max(1.0),
  informationValue: z.number().min(0.0).max(1.0),
  visualValue: z.number().min(0.0).max(1.0),
  audioValue: z.number().min(0.0).max(1.0),
  redundancyPenalty: z.number().min(0.0).max(1.0),
  continuityScore: z.number().min(0.0).max(1.0),
  overallScore: z.number().min(0.0).max(100.0),
});

export type EditorialScore = z.infer<typeof EditorialScoreSchema>;

/**
 * Editorial actions permissible in the decision graph.
 */
export const EditorialActionSchema = z.enum([
  "CUT",
  "KEEP",
  "INSERT_BROLL",
  "APPLY_J_CUT",
  "APPLY_L_CUT",
  "HOLD_SILENCE",
  "TRIM_SILENCE",
  "PUNCH_IN",
  "SWAP_TAKE",
  "REPLACE_WITH_ROOM_TONE",
]);

export type EditorialAction = z.infer<typeof EditorialActionSchema>;

/**
 * REQ-031: Human control level.
 */
export const ControlLevelSchema = z.enum([
  "AUTO",              // Fully autonomous execution (confidence >= threshold)
  "SUGGEST",           // Proposed for human review (thresholds in intermediate range)
  "LOCKED_BY_EDITOR",  // Sacred decision locked by human; AI cannot override
]);

export type ControlLevel = z.infer<typeof ControlLevelSchema>;

/**
 * Evaluated alternative that was considered and discarded.
 */
export const EditorialAlternativeSchema = z.object({
  action: EditorialActionSchema,
  score: z.number().min(0).max(100),
  rejectionReason: z.string().min(1),
});

export type EditorialAlternative = z.infer<typeof EditorialAlternativeSchema>;

/**
 * REQ-032: Fully explainable decision node.
 */
export const EditorialDecisionNodeSchema = z.object({
  decisionId: z.string().min(1),
  timestampSeconds: z.number().min(0),
  durationSeconds: z.number().min(0),
  action: EditorialActionSchema,
  targetAssetId: z.string().min(1),
  tier: RulePriorityTierSchema,
  reason: z.string().min(1),
  confidence: z.number().min(0.0).max(1.0),
  narrativeEffect: z.string().min(1),
  score: EditorialScoreSchema,
  controlLevel: ControlLevelSchema,
  alternativesConsidered: z.array(EditorialAlternativeSchema).default([]),
  parentDecisionId: z.string().optional(),
});

export type EditorialDecisionNode = z.infer<typeof EditorialDecisionNodeSchema>;

/**
 * REQ-032 & REQ-034: Complete Editorial Decision Graph.
 */
export const EditorialDecisionGraphSchema = z.object({
  projectId: z.string().min(1),
  profileName: z.string().min(1),
  decisions: z.array(EditorialDecisionNodeSchema),
  checksum: z.string().length(64), // SHA-256
  createdAt: z.string().datetime(),
});

export type EditorialDecisionGraph = z.infer<typeof EditorialDecisionGraphSchema>;
