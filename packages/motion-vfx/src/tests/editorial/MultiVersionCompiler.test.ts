import test from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import {
  EditorialIRBuilder,
  MultiVersionCompiler,
  CutdownTarget,
  AspectRatioTarget,
} from "../../editorial/index.js";

test("Fase 4D — Multi-Version Editorial Compiler Suite", async (t) => {
  const baseMetadata = {
    title: "Deep Sea Expedition",
    profile: "DOCUMENTARY",
    frameRate: 30,
    width: 1920,
    height: 1080,
    sampleRate: 48000,
    targetDialogueLufs: -20,
  };

  // Build a 90-second master timeline with 9 clips (10s each)
  const builder = new EditorialIRBuilder("proj_deep_sea", baseMetadata);
  builder.createTrack({ id: "v1", name: "Primary Video", type: "VIDEO_PRIMARY", index: 0 });
  builder.createTrack({ id: "a1", name: "Dialogue Track", type: "AUDIO_DIALOGUE", index: 1 });

  for (let i = 0; i < 9; i++) {
    builder.addClip("v1", {
      id: `clip_v_${i}`,
      assetId: `assets/ocean_shot_${i}.mp4`,
      label: `Ocean Beat ${i}`,
      sourceRange: { startSeconds: 0, durationSeconds: 10 },
      timelineRange: { startSeconds: i * 10, durationSeconds: 10 },
    });
    builder.addClip("a1", {
      id: `clip_a_${i}`,
      assetId: `assets/audio_beat_${i}.wav`,
      label: `Dialogue ${i}`,
      sourceRange: { startSeconds: 0, durationSeconds: 10 },
      timelineRange: { startSeconds: i * 10, durationSeconds: 10 },
    });
  }

  const masterIR = builder.build("2026-09-02T10:00:00.000Z");

  await t.test("compiles 60s, 30s, 15s and 6s cutdowns strictly respecting max duration bounds", () => {
    const targets: CutdownTarget[] = [
      "CUTDOWN_60S",
      "CUTDOWN_30S",
      "CUTDOWN_15S",
      "HOOK_TEASER_6S",
    ];

    const expectedMaxDurations: Record<string, number> = {
      CUTDOWN_60S: 60.0,
      CUTDOWN_30S: 30.0,
      CUTDOWN_15S: 15.0,
      HOOK_TEASER_6S: 6.0,
    };

    for (const target of targets) {
      const { variantIR, plan } = MultiVersionCompiler.compileVariant({
        masterIR,
        target,
        aspectRatio: "16:9",
      });

      assert.ok(plan.actualDurationSeconds <= expectedMaxDurations[target]);
      assert.ok(plan.actualDurationSeconds > 0);
      assert.ok(plan.retainedClipIds.length > 0);
      assert.equal(variantIR.tracks.length, 2);
    }
  });

  await t.test("compiles vertical 9:16 and square 1:1 variants updating metadata dimensions", () => {
    const vertical = MultiVersionCompiler.compileVariant({
      masterIR,
      target: "CUTDOWN_30S",
      aspectRatio: "9:16",
    });

    assert.equal(vertical.variantIR.metadata.width, 1080);
    assert.equal(vertical.variantIR.metadata.height, 1920);

    const square = MultiVersionCompiler.compileVariant({
      masterIR,
      target: "CUTDOWN_15S",
      aspectRatio: "1:1",
    });

    assert.equal(square.variantIR.metadata.width, 1080);
    assert.equal(square.variantIR.metadata.height, 1080);
  });

  await t.test("PBT: any cutdown derivative actual duration is strictly <= target duration", () => {
    fc.assert(
      fc.property(
        fc.constantFrom(
          "CUTDOWN_60S",
          "CUTDOWN_30S",
          "CUTDOWN_15S",
          "HOOK_TEASER_6S"
        ),
        fc.constantFrom("16:9", "9:16", "1:1", "4:5", "21:9"),
        (target, aspect) => {
          const { plan } = MultiVersionCompiler.compileVariant({
            masterIR,
            target: target as CutdownTarget,
            aspectRatio: aspect as AspectRatioTarget,
          });

          return plan.actualDurationSeconds <= plan.targetDurationSeconds;
        }
      ),
      { numRuns: 25 }
    );
  });
});
