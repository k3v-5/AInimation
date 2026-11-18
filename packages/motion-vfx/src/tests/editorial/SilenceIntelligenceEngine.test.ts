import test from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import {
  SilenceIntelligenceEngine,
  EditorialProfileRegistry,
  RawSilenceInterval,
} from "../../editorial/index.js";

test("Fase 4A — Silence Intelligence Engine Suite", async (t) => {
  const docProfile = EditorialProfileRegistry.getProfile("DOCUMENTARY");
  const vlogProfile = EditorialProfileRegistry.getProfile("VLOG");

  await t.test("classifies dramatic pauses and preserves them in Documentary profile", () => {
    const intervals: RawSilenceInterval[] = [
      {
        startSeconds: 10.0,
        endSeconds: 11.5, // 1.5s pause
        isEmotionalPeakProximity: true,
      },
    ];

    const classifiedDoc = SilenceIntelligenceEngine.classifySilences(intervals, docProfile);
    assert.equal(classifiedDoc.length, 1);
    assert.equal(classifiedDoc[0].type, "DRAMATIC_PAUSE");
    assert.equal(classifiedDoc[0].decision, "REPLACE_WITH_ROOM_TONE");
    assert.equal(classifiedDoc[0].targetDurationSeconds, 1.5);
    assert.match(classifiedDoc[0].reasoning, /Preserving .* dramatic pause/);

    // In Vlog profile, dramatic pause is trimmed aggressively for rapid pacing
    const classifiedVlog = SilenceIntelligenceEngine.classifySilences(intervals, vlogProfile);
    assert.equal(classifiedVlog[0].decision, "TRIM");
    assert.equal(classifiedVlog[0].targetDurationSeconds, 0.25);
  });

  await t.test("detects respiratory breaths and applies profile policy", () => {
    const breathInterval: RawSilenceInterval[] = [
      {
        startSeconds: 5.0,
        endSeconds: 5.3, // 0.3s
        hasInhaleAcousticProfile: true,
        rmsLevelDb: -32,
      },
    ];

    const docResult = SilenceIntelligenceEngine.classifySilences(breathInterval, docProfile);
    assert.equal(docResult[0].type, "BREATH");
    assert.equal(docResult[0].decision, "KEEP");

    const vlogResult = SilenceIntelligenceEngine.classifySilences(breathInterval, vlogProfile);
    assert.equal(vlogResult[0].type, "BREATH");
    assert.equal(vlogResult[0].decision, "ATTENUATE");
  });

  await t.test("prunes dead air filler silence in all profiles when exceeding limit", () => {
    const deadAir: RawSilenceInterval[] = [
      {
        startSeconds: 20.0,
        endSeconds: 22.0, // 2.0s dead air
      },
    ];

    const result = SilenceIntelligenceEngine.classifySilences(deadAir, vlogProfile);
    assert.equal(result[0].type, "FILLER_SILENCE");
    assert.equal(result[0].decision, "TRIM");
    assert.ok(result[0].targetDurationSeconds < 1.0);
  });

  await t.test("PBT: classified silence start is strictly <= end and duration is non-negative", () => {
    fc.assert(
      fc.property(
        fc.float({ min: 0, max: 1000, noNaN: true }),
        fc.float({ min: 0, max: 10, noNaN: true }),
        fc.boolean(),
        (start, duration, isEmotional) => {
          const end = start + duration;
          const intervals: RawSilenceInterval[] = [
            {
              startSeconds: start,
              endSeconds: end,
              isEmotionalPeakProximity: isEmotional,
            },
          ];

          const classified = SilenceIntelligenceEngine.classifySilences(intervals, docProfile);
          const c = classified[0];
          return c.startSeconds <= c.endSeconds && c.durationSeconds >= 0 && c.confidence >= 0 && c.confidence <= 1;
        }
      ),
      { numRuns: 100 }
    );
  });
});
