import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import { ConfidencePolicy, DEFAULT_HUMAN_REVIEW_CONFIDENCE_THRESHOLD } from "../../../editorial/qa/confidence-policy.js";

describe("Editorial QA — Confidence Policy Suite (REQ-QA-026, REQ-QA-044, REQ-QA-057)", () => {
  it("accepts valid finite confidence values in [0.0, 1.0]", () => {
    assert.doesNotThrow(() => ConfidencePolicy.validateConfidence(0.0));
    assert.doesNotThrow(() => ConfidencePolicy.validateConfidence(0.5));
    assert.doesNotThrow(() => ConfidencePolicy.validateConfidence(0.7));
    assert.doesNotThrow(() => ConfidencePolicy.validateConfidence(1.0));
  });

  it("strictly rejects out-of-range, NaN and Infinite confidence values (REQ-QA-044)", () => {
    assert.throws(() => ConfidencePolicy.validateConfidence(-0.01));
    assert.throws(() => ConfidencePolicy.validateConfidence(1.01));
    assert.throws(() => ConfidencePolicy.validateConfidence(NaN));
    assert.throws(() => ConfidencePolicy.validateConfidence(Infinity));
    assert.throws(() => ConfidencePolicy.validateConfidence(-Infinity));
  });

  it("enforces strict threshold boundary at 0.70 (REQ-QA-026, REQ-QA-057)", () => {
    // 0.6999 must enter human review
    assert.equal(ConfidencePolicy.shouldRouteToHumanReview(0.6999), true);

    // 0.70 does NOT enter human review on its own
    assert.equal(ConfidencePolicy.shouldRouteToHumanReview(0.7), false);

    // 0.7001 does NOT enter human review
    assert.equal(ConfidencePolicy.shouldRouteToHumanReview(0.7001), false);
  });

  it("applies deterministic non-invention penalties for missing data (REQ-QA-045)", () => {
    const penalized = ConfidencePolicy.penalizeMissingData(0.9, 1);
    assert.equal(penalized, 0.65); // 0.90 - 0.25 = 0.65
    assert.ok(ConfidencePolicy.shouldRouteToHumanReview(penalized)); // 0.65 < 0.70 -> routes to human

    const zeroFloored = ConfidencePolicy.penalizeMissingData(0.2, 2);
    assert.equal(zeroFloored, 0.0); // Never negative
  });

  it("PBT: any finite number in [0.0, 1.0] never throws and behaves monotonically", () => {
    fc.assert(
      fc.property(fc.double({ min: 0.0, max: 1.0, noNaN: true }), (conf) => {
        ConfidencePolicy.validateConfidence(conf);
        const routes = ConfidencePolicy.shouldRouteToHumanReview(conf, DEFAULT_HUMAN_REVIEW_CONFIDENCE_THRESHOLD);
        if (conf < 0.7) {
          assert.equal(routes, true);
        } else {
          assert.equal(routes, false);
        }
      }),
      { numRuns: 100 }
    );
  });
});
