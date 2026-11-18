import { z } from "zod";

/**
 * REQ-020: Transition type for audio/video split cuts.
 */
export const JLCutTypeSchema = z.enum(["J_CUT", "L_CUT", "HARD_CUT"]);
export type JLCutType = z.infer<typeof JLCutTypeSchema>;

/**
 * Detailed specification for a planned J-Cut or L-Cut.
 */
export const JLCutPlanSchema = z.object({
  id: z.string().min(1),
  cutType: JLCutTypeSchema,
  visualCutTimestampSeconds: z.number().min(0),
  audioLeadSeconds: z.number().min(0).max(2.0), // Audio starts before video (J-Cut)
  audioTailSeconds: z.number().min(0).max(2.0), // Audio lingers after video (L-Cut)
  fromClipId: z.string().min(1),
  toClipId: z.string().min(1),
  reason: z.string().min(1),
});

export type JLCutPlan = z.infer<typeof JLCutPlanSchema>;

/**
 * REQ-063: Room tone profile for acoustic continuity.
 */
export const RoomToneProfileSchema = z.object({
  locationId: z.string().min(1),
  noiseFloorDb: z.number().min(-90).max(-20),
  ambientBedAssetId: z.string().optional(),
  targetFillGainDb: z.number().min(-60).max(-10),
  suggestedPatchRegions: z.array(
    z.object({
      startSeconds: z.number().min(0),
      durationSeconds: z.number().positive(),
    })
  ).default([]),
});

export type RoomToneProfile = z.infer<typeof RoomToneProfileSchema>;

/**
 * REQ-062: Sound bridge linking two scenes.
 */
export const SoundBridgeCandidateSchema = z.object({
  id: z.string().min(1),
  assetId: z.string().min(1),
  category: z.enum(["ENVIRONMENTAL", "TRAFFIC", "WEATHER", "MECHANICAL", "CROWD", "MUSIC_REVERB"]),
  startSeconds: z.number().min(0),
  durationSeconds: z.number().positive(),
  fromSceneId: z.string().min(1),
  toSceneId: z.string().min(1),
  leadSeconds: z.number().min(0).max(3.0),
});

export type SoundBridgeCandidate = z.infer<typeof SoundBridgeCandidateSchema>;
