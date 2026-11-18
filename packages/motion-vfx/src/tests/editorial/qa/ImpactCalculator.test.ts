import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import { ImpactCalculator } from "../../../editorial/qa/impact-calculator.js";
import { EditorialDiff } from "../../../editorial/qa/editorial-diff-types.js";

describe("Editorial QA — Impact Calculator & Regression Detector (REQ-QA-032 to REQ-QA-039, REQ-QA-043)", () => {
  it("calculates exact duration delta without floating point artifacts (REQ-QA-033)", () => {
    assert.equal(ImpactCalculator.calculateDurationDelta(10.0, 12.5), 2.5);
    assert.equal(ImpactCalculator.calculateDurationDelta(15.0, 14.1), -0.9);
    assert.equal(ImpactCalculator.calculateDurationDelta(5.0, 5.0), 0.0);
  });

  it("calculates pacing delta and accurately classifies trend (REQ-QA-034)", () => {
    const improvement = ImpactCalculator.calculatePacingImpact(0.5, 0.7);
    assert.equal(improvement.pacingDelta, 0.2);
    assert.equal(improvement.trend, "IMPROVES");

    const degradation = ImpactCalculator.calculatePacingImpact(0.8, 0.6);
    assert.equal(degradation.pacingDelta, -0.2);
    assert.equal(degradation.trend, "WORSENS");

    const neutral = ImpactCalculator.calculatePacingImpact(0.7, 0.72);
    assert.equal(neutral.pacingDelta, 0.02);
    assert.equal(neutral.trend, "NEUTRAL");
  });

  it("detects critical BLOCKING regressions when evidence or key beats are removed (REQ-QA-043)", () => {
    const beforeIR: any = {
      claims: [
        { id: "claim_1", statement: "Verified metric 1" },
        { id: "claim_2", statement: "Verified metric 2" },
      ],
      beats: [{ id: "beat_rev", type: "REVELATION" }],
    };

    const afterIR: any = {
      claims: [
        { id: "claim_1", statement: "Verified metric 1" },
        // claim_2 removed!
      ],
      beats: [], // REVELATION removed!
    };

    const diffs: EditorialDiff[] = [
      {
        id: "diff_claim_2",
        type: "REMOVED",
        category: "EVIDENCE",
        entityId: "claim_2",
        impact: {
          durationDeltaSeconds: 0,
          pacingDelta: 0,
          attentionDelta: 0,
          cognitiveLoadDelta: 0,
          contrastDelta: 0,
          narrativeImpactScore: 0,
          evidenceImpactScore: -0.5,
          continuityImpactScore: 0,
          overallImpactScore: 25,
        },
        fingerprint: "rm_claim_2",
      },
      {
        id: "diff_beat_rev",
        type: "REMOVED",
        category: "NARRATIVE",
        entityId: "beat_rev",
        impact: {
          durationDeltaSeconds: 0,
          pacingDelta: 0,
          attentionDelta: 0,
          cognitiveLoadDelta: 0,
          contrastDelta: 0,
          narrativeImpactScore: -0.8,
          evidenceImpactScore: 0,
          continuityImpactScore: 0,
          overallImpactScore: 40,
        },
        fingerprint: "rm_beat_rev",
      },
    ];

    const regressions = ImpactCalculator.detectRegressions(diffs, beforeIR, afterIR);
    assert.equal(regressions.length, 2);
    assert.ok(regressions.every((r) => r.severity === "BLOCKING"));
    assert.ok(regressions.some((r) => r.ruleId === "QA-EVID-001"));
    assert.ok(regressions.some((r) => r.ruleId === "QA-NARR-003"));
  });

  it("PBT: overall impact score is always strictly bounded within [0, 100]", () => {
    fc.assert(
      fc.property(
        fc.double({ min: -50.0, max: 50.0, noNaN: true }),
        fc.double({ min: -1.0, max: 1.0, noNaN: true }),
        fc.double({ min: 0.0, max: 1.0, noNaN: true }),
        (durDelta, paceDelta, narrScore) => {
          const score = ImpactCalculator.computeOverallScore({
            durationDeltaSeconds: durDelta,
            pacingDelta: paceDelta,
            narrativeImpactScore: narrScore,
          });
          return Number.isFinite(score) && score >= 0.0 && score <= 100.0;
        }
      ),
      { numRuns: 100 }
    );
  });
});
