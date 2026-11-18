import test from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import {
  SoundDesignEngine,
  EditorialProfileRegistry,
} from "../../editorial/index.js";

test("Fase 4B — Sound Design & Acoustic Continuity Suite", async (t) => {
  const docProfile = EditorialProfileRegistry.getProfile("DOCUMENTARY");
  const vlogProfile = EditorialProfileRegistry.getProfile("VLOG");

  await t.test("plans L-Cut when transitioning from dialogue A-Roll to illustrative B-Roll", () => {
    const plan = SoundDesignEngine.planTransition({
      fromClipId: "interview_clip_01",
      toClipId: "broll_landscape_02",
      visualCutTimestampSeconds: 14.5,
      fromIsDialogue: true,
      toIsDialogue: false,
      toIsBRoll: true,
      fromIsBRoll: false,
      profile: docProfile,
    });

    assert.equal(plan.cutType, "L_CUT");
    assert.ok(plan.audioTailSeconds > 0);
    assert.equal(plan.audioLeadSeconds, 0);
    assert.match(plan.reason, /dialogue extends .* over B-roll/);
  });

  await t.test("plans J-Cut when transitioning from B-Roll into interviewee talking head", () => {
    const plan = SoundDesignEngine.planTransition({
      fromClipId: "broll_landscape_02",
      toClipId: "interview_clip_03",
      visualCutTimestampSeconds: 22.0,
      fromIsDialogue: false,
      toIsDialogue: true,
      toIsBRoll: false,
      fromIsBRoll: true,
      profile: docProfile,
    });

    assert.equal(plan.cutType, "J_CUT");
    assert.ok(plan.audioLeadSeconds > 0);
    assert.equal(plan.audioTailSeconds, 0);
    assert.match(plan.reason, /speaker voice leads/);
  });

  await t.test("plans hard cut when profile does not prefer split cuts", () => {
    const plan = SoundDesignEngine.planTransition({
      fromClipId: "clip_a",
      toClipId: "clip_b",
      visualCutTimestampSeconds: 5.0,
      fromIsDialogue: true,
      toIsDialogue: false,
      toIsBRoll: true,
      fromIsBRoll: false,
      profile: vlogProfile, // Vlog profile disables preferJCutLcut by default
    });

    assert.equal(plan.cutType, "HARD_CUT");
    assert.equal(plan.audioLeadSeconds, 0);
    assert.equal(plan.audioTailSeconds, 0);
  });

  await t.test("generates room tone patch profile across silence gaps", () => {
    const roomTone = SoundDesignEngine.planRoomToneBed({
      locationId: "studio_a",
      measuredNoiseFloorDb: -38.0,
      silenceGaps: [
        { startSeconds: 10.0, durationSeconds: 0.15 }, // Sub-threshold (<0.25s), ignored
        { startSeconds: 25.0, durationSeconds: 1.2 },  // Eligible
        { startSeconds: 40.0, durationSeconds: 0.8 },  // Eligible
      ],
      ambientBedAssetId: "room_tone_studio_a.wav",
    });

    assert.equal(roomTone.locationId, "studio_a");
    assert.equal(roomTone.noiseFloorDb, -38.0);
    assert.equal(roomTone.targetFillGainDb, -41.0); // 3dB below measured noise floor
    assert.equal(roomTone.suggestedPatchRegions.length, 2);
  });

  await t.test("PBT: audio lead and tail seconds are always bounded in [0, 2.0]", () => {
    fc.assert(
      fc.property(
        fc.boolean(),
        fc.boolean(),
        fc.boolean(),
        fc.boolean(),
        (fromDiag, toDiag, toBroll, fromBroll) => {
          const plan = SoundDesignEngine.planTransition({
            fromClipId: "c1",
            toClipId: "c2",
            visualCutTimestampSeconds: 10,
            fromIsDialogue: fromDiag,
            toIsDialogue: toDiag,
            toIsBRoll: toBroll,
            fromIsBRoll: fromBroll,
            profile: docProfile,
          });

          return (
            plan.audioLeadSeconds >= 0 &&
            plan.audioLeadSeconds <= 2.0 &&
            plan.audioTailSeconds >= 0 &&
            plan.audioTailSeconds <= 2.0
          );
        }
      ),
      { numRuns: 50 }
    );
  });
});
