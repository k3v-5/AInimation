import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import {
  CognitiveLoadEngine,
  InstantaneousCognitiveState,
} from "../../editorial/attention/cognitive-load-engine.js";

describe("Fase 4H — Cognitive Load Engine Suite", () => {
  it("computes exact load for isolated voice matching channel weight formula (REQ-047)", () => {
    // Normalization formula: V = (WPM - 100) / (220 - 100)
    // To get V = 0.45: WPM = 100 + 0.45 * 120 = 154 WPM
    const vNormal = CognitiveLoadEngine.normalizeVoice(154, true);
    assert.equal(vNormal, 0.45);

    const report = CognitiveLoadEngine.evaluate({
      totalDurationSeconds: 10.0,
      states: [
        {
          timestampSeconds: 2.0,
          speechActive: true,
          speechWordsPerMinute: 154,
        },
      ],
    });

    // C(t) = 0.30 * 0.45 = 0.1350
    assert.equal(report.averageLoad, 0.135);
    assert.equal(report.peakLoad, 0.135);
    assert.equal(report.detectedOverloadsCount, 0);
  });

  it("detects multimodal overload (C >= 0.85) and emits actionable mitigation proposals", () => {
    // High voice + 3 on-screen graphics + fast subtitles + loud music + fast cuts
    const states: InstantaneousCognitiveState[] = [
      {
        timestampSeconds: 1.0,
        speechActive: true,
        speechWordsPerMinute: 220, // V = 1.0
        onScreenDataElementsCount: 3, // D = 1.0
        subtitlesCharsPerSecond: 25, // S = 1.0
        audioEnergyDbfs: -6.0, // M = 1.0
        cutsInRecent3Seconds: 4, // K = 1.0
      },
      {
        timestampSeconds: 2.0,
        speechActive: true,
        speechWordsPerMinute: 220,
        onScreenDataElementsCount: 3,
        subtitlesCharsPerSecond: 25,
        audioEnergyDbfs: -6.0,
        cutsInRecent3Seconds: 4,
      },
      {
        timestampSeconds: 3.0,
        speechActive: true,
        speechWordsPerMinute: 220,
        onScreenDataElementsCount: 3,
        subtitlesCharsPerSecond: 25,
        audioEnergyDbfs: -6.0,
        cutsInRecent3Seconds: 4,
      },
      {
        timestampSeconds: 4.5,
        speechActive: true,
        speechWordsPerMinute: 220,
        onScreenDataElementsCount: 3,
        subtitlesCharsPerSecond: 25,
        audioEnergyDbfs: -6.0,
        cutsInRecent3Seconds: 4,
      },
    ];

    const report = CognitiveLoadEngine.evaluate({
      totalDurationSeconds: 10.0,
      states,
    });

    assert.equal(report.peakLoad, 1.0);
    assert.ok(report.detectedOverloadsCount >= 1, "Must detect at least 1 overload");
    assert.ok(report.overloadAlerts.length >= 1);
    assert.ok(report.recommendedMitigations.length >= 1);

    const mitig = report.recommendedMitigations[0];
    assert.ok(mitig.type === "SHIFT_GRAPHIC" || mitig.type === "SPLIT_DENSE_SEGMENT");
    assert.ok(mitig.reason.length > 10);
  });

  it("stays in safe bounds under moderate load without generating false alerts", () => {
    const states: InstantaneousCognitiveState[] = [
      {
        timestampSeconds: 2.0,
        speechActive: true,
        speechWordsPerMinute: 130, // moderate speech
        audioEnergyDbfs: -24.0, // background bed
      },
      {
        timestampSeconds: 5.0,
        onScreenDataElementsCount: 1, // single label
        subtitlesCharsPerSecond: 12,
      },
    ];

    const report = CognitiveLoadEngine.evaluate({
      totalDurationSeconds: 10.0,
      states,
    });

    assert.ok(report.peakLoad < 0.60, `Peak load should be moderate, was ${report.peakLoad}`);
    assert.equal(report.detectedOverloadsCount, 0);
    assert.equal(report.overloadAlerts.length, 0);
  });

  it("guarantees deterministic SHA-256 report checksum", () => {
    const input = {
      totalDurationSeconds: 15.0,
      states: [
        { timestampSeconds: 2.0, speechActive: true, speechWordsPerMinute: 160 },
        { timestampSeconds: 6.0, onScreenDataElementsCount: 2 },
      ],
    };

    const run1 = CognitiveLoadEngine.evaluate(input);
    const run2 = CognitiveLoadEngine.evaluate(input);

    assert.equal(run1.checksumSha256, run2.checksumSha256);
    assert.equal(run1.checksumSha256.length, 64);
  });

  it("PBT: cognitive load is always strictly bounded within [0.0, 1.0] and finite", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 50, max: 300 }),
        fc.integer({ min: 0, max: 8 }),
        fc.integer({ min: 0, max: 50 }),
        fc.double({ min: -60.0, max: 0.0, noNaN: true }),
        fc.integer({ min: 0, max: 8 }),
        fc.double({ min: 0.0, max: 1.0, noNaN: true }),
        (wpm, dataCount, cps, dbfs, cuts, motion) => {
          const report = CognitiveLoadEngine.evaluate({
            totalDurationSeconds: 10.0,
            states: [
              {
                timestampSeconds: 2.0,
                speechActive: true,
                speechWordsPerMinute: wpm,
                onScreenDataElementsCount: dataCount,
                subtitlesCharsPerSecond: cps,
                audioEnergyDbfs: dbfs,
                cutsInRecent3Seconds: cuts,
                cameraMotionIntensity: motion,
              },
            ],
          });

          return (
            Number.isFinite(report.averageLoad) &&
            report.averageLoad >= 0.0 &&
            report.averageLoad <= 1.0 &&
            report.peakLoad >= 0.0 &&
            report.peakLoad <= 1.0
          );
        }
      ),
      { numRuns: 50 }
    );
  });
});
