import { z } from "zod";

/**
 * REQ-001: Canonical editorial genres supported by the engine.
 */
export const EditorialGenreSchema = z.enum([
  "VLOG",
  "DOCUMENTARY",
  "JOURNALISM",
  "EDUCATIONAL",
  "INTERVIEW",
  "NEWS",
  "CINEMATIC",
  "CORPORATE",
  "SHORT_FORM",
  "TECHNICAL",
]);

export type EditorialGenre = z.infer<typeof EditorialGenreSchema>;

/**
 * Policy governing silence handling and pruning.
 */
export const SilencePolicySchema = z.object({
  maxFillerSilenceSeconds: z.number().min(0.05).max(5.0),
  preserveDramaticPauses: z.boolean(),
  preserveBreaths: z.boolean(),
  roomToneReplacement: z.boolean(),
});

export type SilencePolicy = z.infer<typeof SilencePolicySchema>;

/**
 * Policy governing shot scales and visual progression.
 */
export const ShotGrammarPolicySchema = z.object({
  maxConsecutiveScale: z.number().int().min(1).max(10),
  preferredProgression: z.enum(["WIDE_TO_CLOSE", "RHYTHMIC", "FREE"]),
  enforceEyelineContinuity: z.boolean(),
  allowJumpCutsOnAroll: z.boolean(),
  allowDynamicPunchIn: z.boolean(),
});

export type ShotGrammarPolicy = z.infer<typeof ShotGrammarPolicySchema>;

/**
 * Policy governing B-Roll selection, duration, and diversity.
 */
export const BRollPolicySchema = z.object({
  minTalkingHeadDurationBeforeBroll: z.number().min(0),
  maxBrollRepetitionPerFamily: z.number().int().min(1),
  selectionMode: z.enum(["SEMANTIC_EVIDENCE", "DYNAMIC_FILL", "METAPHORIC"]),
  precedenceOverPunchIn: z.literal(true), // Universal invariant: B-Roll > Punch-In
});

export type BRollPolicy = z.infer<typeof BRollPolicySchema>;

/**
 * Policy governing transitions and audio leading/trailing.
 */
export const TransitionPolicySchema = z.object({
  preferJCutLcut: z.boolean(),
  defaultAudioLeadSeconds: z.number().min(0).max(2.0),
  defaultAudioTailSeconds: z.number().min(0).max(2.0),
  allowDissolves: z.boolean(),
});

export type TransitionPolicy = z.infer<typeof TransitionPolicySchema>;

/**
 * REQ-001 & REQ-002: Master Editorial Profile Schema.
 */
export const EditorialProfileSchema = z.object({
  genre: EditorialGenreSchema,
  name: z.string().min(1),
  description: z.string(),
  pacing: z.object({
    baseShotDurationSeconds: z.number().positive(),
    pacingCurve: z.enum(["CONTEMPLATIVE", "MODERATE", "AGGRESSIVE", "DYNAMIC_WAVE"]),
    wordsPerMinuteTarget: z.number().positive(),
  }),
  silencePolicy: SilencePolicySchema,
  shotGrammarPolicy: ShotGrammarPolicySchema,
  brollPolicy: BRollPolicySchema,
  transitionPolicy: TransitionPolicySchema,
  audioPolicy: z.object({
    roomTonePreservation: z.boolean(),
    dynamicDucking: z.boolean(),
    targetDialogueLufs: z.number().min(-30).max(-10),
  }),
});

export type EditorialProfile = z.infer<typeof EditorialProfileSchema>;
