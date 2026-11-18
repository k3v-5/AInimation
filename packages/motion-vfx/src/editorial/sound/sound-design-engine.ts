import crypto from "crypto";
import { EditorialProfile } from "../contracts/content-profile.types.js";
import {
  JLCutPlan,
  JLCutPlanSchema,
  RoomToneProfile,
  RoomToneProfileSchema,
} from "./sound-design.types.js";

/**
 * REQ-020, REQ-062, REQ-063: Master Sound Design Engine.
 * Plans narrative-driven J-Cuts and L-Cuts, and manages room-tone acoustic continuity
 * to eliminate dead digital silence between dialogue edits.
 */
export class SoundDesignEngine {
  /**
   * Plans an audio split transition (J-Cut, L-Cut or Hard Cut) between two consecutive visual clips.
   */
  public static planTransition(params: {
    fromClipId: string;
    toClipId: string;
    visualCutTimestampSeconds: number;
    fromIsDialogue: boolean;
    toIsDialogue: boolean;
    toIsBRoll: boolean;
    fromIsBRoll: boolean;
    profile: EditorialProfile;
  }): JLCutPlan {
    const {
      fromClipId,
      toClipId,
      visualCutTimestampSeconds,
      fromIsDialogue,
      toIsDialogue,
      toIsBRoll,
      fromIsBRoll,
      profile,
    } = params;

    const id = `jl_${crypto.createHash("sha256").update(`${fromClipId}_${toClipId}_${visualCutTimestampSeconds}`).digest("hex").substring(0, 10)}`;

    if (!profile.transitionPolicy.preferJCutLcut) {
      return JLCutPlanSchema.parse({
        id,
        cutType: "HARD_CUT",
        visualCutTimestampSeconds,
        audioLeadSeconds: 0,
        audioTailSeconds: 0,
        fromClipId,
        toClipId,
        reason: "Hard cut assigned per profile transition policy.",
      });
    }

    // 1. L-Cut: Talking head continues speaking over B-roll insertion
    if (fromIsDialogue && toIsBRoll) {
      const audioTailSeconds = Math.min(1.5, Math.max(0.2, profile.transitionPolicy.defaultAudioTailSeconds));
      return JLCutPlanSchema.parse({
        id,
        cutType: "L_CUT",
        visualCutTimestampSeconds,
        audioLeadSeconds: 0,
        audioTailSeconds,
        fromClipId,
        toClipId,
        reason: `L-Cut: dialogue extends ${audioTailSeconds}s over B-roll for fluid thematic transition.`,
      });
    }

    // 2. J-Cut: Dialogue of speaker enters before visual cut to speaker camera
    if (fromIsBRoll && toIsDialogue) {
      const audioLeadSeconds = Math.min(1.5, Math.max(0.2, profile.transitionPolicy.defaultAudioLeadSeconds));
      return JLCutPlanSchema.parse({
        id,
        cutType: "J_CUT",
        visualCutTimestampSeconds,
        audioLeadSeconds,
        audioTailSeconds: 0,
        fromClipId,
        toClipId,
        reason: `J-Cut: speaker voice leads by ${audioLeadSeconds}s before camera reveal.`,
      });
    }

    // 3. Dialogue-to-dialogue exchange: subtle J-Cut for conversational flow
    if (fromIsDialogue && toIsDialogue) {
      const audioLeadSeconds = Math.min(0.4, profile.transitionPolicy.defaultAudioLeadSeconds * 0.7);
      return JLCutPlanSchema.parse({
        id,
        cutType: "J_CUT",
        visualCutTimestampSeconds,
        audioLeadSeconds,
        audioTailSeconds: 0,
        fromClipId,
        toClipId,
        reason: `J-Cut: next speaker audio pre-rolls ${audioLeadSeconds}s for natural conversational cadence.`,
      });
    }

    // Default to hard cut
    return JLCutPlanSchema.parse({
      id,
      cutType: "HARD_CUT",
      visualCutTimestampSeconds,
      audioLeadSeconds: 0,
      audioTailSeconds: 0,
      fromClipId,
      toClipId,
      reason: "Standard hard cut between non-dialogue segments.",
    });
  }

  /**
   * Plans room tone patch regions across detected silence gaps to maintain acoustic bed continuity.
   */
  public static planRoomToneBed(params: {
    locationId: string;
    measuredNoiseFloorDb: number;
    silenceGaps: { startSeconds: number; durationSeconds: number }[];
    ambientBedAssetId?: string;
  }): RoomToneProfile {
    const { locationId, measuredNoiseFloorDb, silenceGaps, ambientBedAssetId } = params;

    // Filter gaps larger than 0.25s that risk sounding like artificial digital vacuum
    const eligibleGaps = silenceGaps.filter((g) => g.durationSeconds >= 0.25);

    // Target fill gain is typically 3 dB below the dialogue baseline noise floor
    const targetFillGainDb = Math.max(-60, Math.min(-24, measuredNoiseFloorDb - 3.0));

    return RoomToneProfileSchema.parse({
      locationId,
      noiseFloorDb: measuredNoiseFloorDb,
      ambientBedAssetId,
      targetFillGainDb,
      suggestedPatchRegions: eligibleGaps,
    });
  }
}
