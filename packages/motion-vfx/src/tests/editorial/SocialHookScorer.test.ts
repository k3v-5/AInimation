import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import { SocialHookScorer } from "../../editorial/trailer/social-hook-scorer.js";

describe("Fase 4F — Social Hook Intelligence Scorer Suite", () => {
  it("scores high retention for dynamic visual cuts, verbal intrigue, and audio impact (REQ-029)", () => {
    const metrics = SocialHookScorer.evaluateHook({
      windowDurationSeconds: 5.0,
      cutsCount: 3,
      initialSilenceSeconds: 0.05,
      hasVisualPunchIn: true,
      hasAudioRiserOrImpact: true,
      speechText: "¿Por qué nadie investigó el secreto detrás del colapso?",
      firstSpokenWordTimestamp: 0.1,
    });

    assert.ok(metrics.retentionPredictionScore >= 75.0);
    assert.ok(metrics.visualPaceScore >= 80.0);
    assert.ok(metrics.verbalIntrigueScore >= 75.0);
    assert.ok(metrics.acousticImpactScore >= 85.0);
    assert.ok(metrics.intrigueWordsDetected.length >= 2);
  });

  it("penalizes static single shot with long initial dead air and missing audio cues", () => {
    const metrics = SocialHookScorer.evaluateHook({
      windowDurationSeconds: 5.0,
      cutsCount: 0,
      initialSilenceSeconds: 0.85,
      hasVisualPunchIn: false,
      hasAudioRiserOrImpact: false,
      speechText: "Buenas tardes a todos los presentes en esta reunión.",
      firstSpokenWordTimestamp: 0.9,
    });

    assert.ok(metrics.retentionPredictionScore < 45.0);
    assert.ok(metrics.visualPaceScore <= 30.0);
    assert.ok(metrics.acousticImpactScore <= 40.0);
    assert.ok(metrics.recommendations.length >= 2);
  });

  it("generates actionable recommendations when opening is suboptimal", () => {
    const metrics = SocialHookScorer.evaluateHook({
      windowDurationSeconds: 4.0,
      cutsCount: 0,
      initialSilenceSeconds: 0.40,
      hasVisualPunchIn: false,
      hasAudioRiserOrImpact: false,
      speechText: "Hola amigos.",
    });

    const recsJoined = metrics.recommendations.join(" ");
    assert.ok(recsJoined.includes("initial silence") || recsJoined.includes("Trim"));
    assert.ok(recsJoined.includes("cut") || recsJoined.includes("punch-in"));
    assert.ok(recsJoined.includes("audio riser") || recsJoined.includes("impact"));
  });

  it("guarantees 100% deterministic metrics across evaluation runs", () => {
    const input = {
      windowDurationSeconds: 5.0,
      cutsCount: 2,
      initialSilenceSeconds: 0.1,
      hasVisualPunchIn: true,
      hasAudioRiserOrImpact: true,
      speechText: "The untold secret of the twentieth century.",
    };

    const res1 = SocialHookScorer.evaluateHook(input);
    const res2 = SocialHookScorer.evaluateHook(input);

    assert.deepEqual(res1, res2);
  });

  it("PBT: retentionPredictionScore is always strictly bounded within [0.0, 100.0]", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 10 }),
        fc.float({ min: 0.0, max: 3.0, noNaN: true }),
        fc.boolean(),
        fc.boolean(),
        fc.string({ maxLength: 100 }),
        (cuts, silence, punchIn, impact, text) => {
          const metrics = SocialHookScorer.evaluateHook({
            windowDurationSeconds: 5.0,
            cutsCount: cuts,
            initialSilenceSeconds: silence,
            hasVisualPunchIn: punchIn,
            hasAudioRiserOrImpact: impact,
            speechText: text,
          });

          return (
            metrics.retentionPredictionScore >= 0.0 &&
            metrics.retentionPredictionScore <= 100.0 &&
            metrics.visualPaceScore >= 0.0 &&
            metrics.visualPaceScore <= 100.0 &&
            metrics.verbalIntrigueScore >= 0.0 &&
            metrics.verbalIntrigueScore <= 100.0 &&
            metrics.acousticImpactScore >= 0.0 &&
            metrics.acousticImpactScore <= 100.0
          );
        }
      ),
      { numRuns: 50 }
    );
  });
});
