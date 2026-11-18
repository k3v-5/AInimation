import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import {
  PacingCurveComposer,
  TargetPacingSegment,
} from "../../editorial/attention/pacing-curve-composer.js";

describe("Fase 4H — Pacing Curve Composer Suite", () => {
  it("rewards aligned cut cadence with high alignment score (REQ-049)", () => {
    // Target curve: moderate pace (0.4) for 0-10s, fast pace (0.8) for 10-20s
    const targetCurve: TargetPacingSegment[] = [
      { startSeconds: 0.0, endSeconds: 10.0, targetPacing: 0.40 },
      { startSeconds: 10.0, endSeconds: 20.0, targetPacing: 0.80 },
    ];

    // Cuts: 2 cuts in first 10s (approx 0.4 of 5 max), 4 cuts in second 10s (approx 0.8 of 5 max)
    const cutTimestamps = [2.0, 6.0, 11.0, 13.5, 16.0, 18.5];

    const report = PacingCurveComposer.evaluate({
      totalDurationSeconds: 20.0,
      cutTimestampsSeconds: cutTimestamps,
      targetCurve,
    });

    assert.ok(report.alignmentScore >= 75.0, `Alignment score should be high, was ${report.alignmentScore}`);
    assert.ok(report.meanL1Distance <= 0.25);
  });

  it("penalizes zero-cut static sequence against high target pace", () => {
    const targetCurve: TargetPacingSegment[] = [
      { startSeconds: 0.0, endSeconds: 20.0, targetPacing: 0.85 },
    ];

    const report = PacingCurveComposer.evaluate({
      totalDurationSeconds: 20.0,
      cutTimestampsSeconds: [], // no cuts at all
      targetCurve,
    });

    // Distance will be ~0.85 -> score ~15
    assert.ok(report.alignmentScore <= 30.0, `Score should be low, was ${report.alignmentScore}`);
    assert.ok(report.discrepancies.length > 0);
    assert.ok(report.discrepancies[0].recommendation.includes("Pacing is too slow"));
  });

  it("identifies frantic cuts exceeding calm target pace", () => {
    const targetCurve: TargetPacingSegment[] = [
      { startSeconds: 0.0, endSeconds: 10.0, targetPacing: 0.20 }, // calm
    ];

    // 6 rapid cuts in 6 seconds
    const cutTimestamps = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0];

    const report = PacingCurveComposer.evaluate({
      totalDurationSeconds: 10.0,
      cutTimestampsSeconds: cutTimestamps,
      targetCurve,
    });

    assert.ok(report.discrepancies.some((d) => d.recommendation.includes("Pacing is too frantic")));
  });

  it("guarantees deterministic SHA-256 checksum", () => {
    const input = {
      totalDurationSeconds: 15.0,
      cutTimestampsSeconds: [3.0, 7.0, 11.0],
      targetCurve: [{ startSeconds: 0.0, endSeconds: 15.0, targetPacing: 0.5 }],
    };

    const run1 = PacingCurveComposer.evaluate(input);
    const run2 = PacingCurveComposer.evaluate(input);

    assert.equal(run1.checksumSha256, run2.checksumSha256);
    assert.equal(run1.checksumSha256.length, 64);
  });

  it("PBT: alignmentScore is always strictly bounded in [0.0, 100.0]", () => {
    fc.assert(
      fc.property(
        fc.array(fc.double({ min: 0.0, max: 30.0, noNaN: true }), { maxLength: 20 }),
        fc.double({ min: 0.0, max: 1.0, noNaN: true }),
        (cuts, target) => {
          const report = PacingCurveComposer.evaluate({
            totalDurationSeconds: 30.0,
            cutTimestampsSeconds: cuts,
            targetCurve: [{ startSeconds: 0.0, endSeconds: 30.0, targetPacing: target }],
          });

          return (
            Number.isFinite(report.alignmentScore) &&
            report.alignmentScore >= 0.0 &&
            report.alignmentScore <= 100.0 &&
            Number.isFinite(report.meanL1Distance) &&
            report.meanL1Distance >= 0.0 &&
            report.meanL1Distance <= 1.0
          );
        }
      ),
      { numRuns: 40 }
    );
  });
});
