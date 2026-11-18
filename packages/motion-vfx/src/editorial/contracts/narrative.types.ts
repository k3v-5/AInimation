import { z } from "zod";

/**
 * REQ-008: Canonical 10 Documentary Narrative Beats.
 */
export const DocumentaryBeatTypeSchema = z.enum([
  "HOOK",
  "CONTEXT",
  "QUESTION",
  "EVIDENCE",
  "TESTIMONY",
  "CONFLICT",
  "ESCALATION",
  "REVELATION",
  "RESOLUTION",
  "REFLECTION",
]);

export type DocumentaryBeatType = z.infer<typeof DocumentaryBeatTypeSchema>;

/**
 * Default canonical sequence order and target energy levels (0.0 to 1.0)
 */
export const CANONICAL_BEAT_ENERGY_TARGETS: Record<DocumentaryBeatType, number> = {
  HOOK: 0.85,
  CONTEXT: 0.40,
  QUESTION: 0.55,
  EVIDENCE: 0.60,
  TESTIMONY: 0.50,
  CONFLICT: 0.75,
  ESCALATION: 0.90,
  REVELATION: 1.00,
  RESOLUTION: 0.45,
  REFLECTION: 0.30,
};

/**
 * REQ-008: Narrative Beat Node.
 */
export const NarrativeBeatNodeSchema = z.object({
  id: z.string().min(1),
  beat: DocumentaryBeatTypeSchema,
  sceneId: z.string().min(1),
  title: z.string().min(1),
  targetDurationSeconds: z.number().positive(),
  actualDurationSeconds: z.number().nonnegative(),
  timelineStartSeconds: z.number().nonnegative(),
  timelineEndSeconds: z.number().nonnegative(),
  targetEnergyLevel: z.number().min(0.0).max(1.0),
  actualEnergyLevel: z.number().min(0.0).max(1.0).default(0.5),
  claimIds: z.array(z.string()).default([]),
  causalDependencies: z.array(z.string()).default([]),
  prohibitedRevealItemIds: z.array(z.string()).default([]),
});

export type NarrativeBeatNode = z.infer<typeof NarrativeBeatNodeSchema>;

/**
 * REQ-044: Narrative Causality Edge (Causal dependency graph).
 */
export const NarrativeCausalityEdgeSchema = z.object({
  fromBeatId: z.string().min(1),
  toBeatId: z.string().min(1),
  reason: z.string().min(1),
  strict: z.boolean().default(true),
});

export type NarrativeCausalityEdge = z.infer<typeof NarrativeCausalityEdgeSchema>;

/**
 * REQ-045: Reveal Constraint (Spoiler and premature reveal protection).
 */
export const RevealConstraintSchema = z.object({
  itemId: z.string().min(1),
  itemType: z.enum(["CLAIM", "EVIDENCE_ASSET", "KEY_ENTITY", "PLOT_TWIST"]),
  prohibitedBeforeBeat: DocumentaryBeatTypeSchema,
  description: z.string().min(1),
});

export type RevealConstraint = z.infer<typeof RevealConstraintSchema>;

/**
 * REQ-008, REQ-044 & REQ-045: Master Narrative Arc Plan.
 */
export const NarrativeArcPlanSchema = z.object({
  projectId: z.string().min(1),
  totalDurationSeconds: z.number().nonnegative(),
  beats: z.array(NarrativeBeatNodeSchema),
  causalityEdges: z.array(NarrativeCausalityEdgeSchema).default([]),
  revealConstraints: z.array(RevealConstraintSchema).default([]),
  energyPoints: z
    .array(
      z.object({
        timestampSeconds: z.number().nonnegative(),
        energy: z.number().min(0.0).max(1.0),
      })
    )
    .default([]),
  checksumSha256: z.string().length(64),
});

export type NarrativeArcPlan = z.infer<typeof NarrativeArcPlanSchema>;
