import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import {
  AudienceAttentionModel,
  TimelineStimulusEvent,
} from "../../editorial/attention/audience-attention-model.js";

describe("Fase 4H — Audience Attention Model Suite", () => {
  it("natural decay converges towards baseline 0.40 and sustains above 0.60 after 18 seconds (REQ-046)", () => {
    const report = AudienceAttentionModel.simulate({
      totalDurationSeconds: 30.0,
      events: [],
    });

    assert.equal(report.attentionPoints[0].attentionScore, 0.85);

    // Find point near 18 seconds
    const pt18 = report.attentionPoints.find((p) => Math.abs(p.timestampSeconds - 18.0) < 0.5);
    assert.ok(pt18 !== undefined);
    assert.ok(pt18.attentionScore >= 0.60, `Attention at 18s must be >= 0.60, was ${pt18.attentionScore}`);

    // Last point near 30 seconds
    const pt30 = report.attentionPoints[report.attentionPoints.length - 1];
    assert.ok(pt30.attentionScore >= 0.40, `Attention must not drop below baseline 0.40`);
  });

  it("stimuli injections sustain high attention throughout the timeline", () => {
    const events: TimelineStimulusEvent[] = [
      { timestampSeconds: 5.0, visualCut: true },
      { timestampSeconds: 10.0, narrativeBeatTransition: true },
      { timestampSeconds: 15.0, audioHitOrRiser: true },
      { timestampSeconds: 20.0, dataOrEvidenceReveal: true },
      { timestampSeconds: 25.0, visualCut: true },
    ];

    const report = AudienceAttentionModel.simulate({
      totalDurationSeconds: 30.0,
      events,
    });

    assert.ok(report.averageAttention >= 0.70, `Average attention should be high, was ${report.averageAttention}`);
    assert.equal(report.dipAlerts.length, 0, "No dips should be triggered with regular stimuli");
  });

  it("detects attention dip alerts and generates actionable recommendations for low baseline", () => {
    const report = AudienceAttentionModel.simulate({
      totalDurationSeconds: 60.0,
      events: [],
      profile: {
        initialAttention: 0.50,
        baselineAttention: 0.25, // Lower baseline to test dip detector
        decayLambda: 0.08,
      },
    });

    assert.ok(report.dipAlerts.length >= 1, "Should detect at least one attention dip");
    const dip = report.dipAlerts[0];
    assert.ok(dip.minScore < 0.40);
    assert.ok(dip.recommendedFix.includes("insert visual cut") || dip.recommendedFix.includes("riser"));
  });

  it("PBT: simultaneous stimuli are order-independent (commutativity)", () => {
    fc.assert(
      fc.property(
        fc.boolean(),
        fc.boolean(),
        fc.boolean(),
        fc.boolean(),
        (vis, audio, beat, data) => {
          const ev1: TimelineStimulusEvent = {
            timestampSeconds: 5.0,
            visualCut: vis,
            audioHitOrRiser: audio,
          };
          const ev2: TimelineStimulusEvent = {
            timestampSeconds: 5.0,
            narrativeBeatTransition: beat,
            dataOrEvidenceReveal: data,
          };

          const runA = AudienceAttentionModel.simulate({
            totalDurationSeconds: 10.0,
            events: [ev1, ev2],
          });

          const runB = AudienceAttentionModel.simulate({
            totalDurationSeconds: 10.0,
            events: [ev2, ev1],
          });

          return (
            runA.checksumSha256 === runB.checksumSha256 &&
            runA.averageAttention === runB.averageAttention
          );
        }
      ),
      { numRuns: 30 }
    );
  });

  it("PBT: adding a positive stimulus never reduces attention (monotonicity)", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 1.0, max: 20.0, noNaN: true }),
        (stimulusTime) => {
          const baseRun = AudienceAttentionModel.simulate({
            totalDurationSeconds: 25.0,
            events: [],
          });

          const boostedRun = AudienceAttentionModel.simulate({
            totalDurationSeconds: 25.0,
            events: [{ timestampSeconds: stimulusTime, visualCut: true }],
          });

          // Boosted run must have >= average attention
          return boostedRun.averageAttention >= baseRun.averageAttention - 1e-6;
        }
      ),
      { numRuns: 30 }
    );
  });

  it("PBT: all attention points are finite and bounded in [0.0, 1.0]", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 0.0, max: 1.0, noNaN: true }),
        fc.double({ min: 0.0, max: 1.0, noNaN: true }),
        fc.double({ min: 0.01, max: 0.2, noNaN: true }),
        (initAtt, baseAtt, lambda) => {
          const report = AudienceAttentionModel.simulate({
            totalDurationSeconds: 15.0,
            events: [{ timestampSeconds: 3.0, visualCut: true }],
            profile: {
              initialAttention: initAtt,
              baselineAttention: baseAtt,
              decayLambda: lambda,
            },
          });

          return report.attentionPoints.every(
            (p) => Number.isFinite(p.attentionScore) && p.attentionScore >= 0.0 && p.attentionScore <= 1.0
          );
        }
      ),
      { numRuns: 30 }
    );
  });
});
