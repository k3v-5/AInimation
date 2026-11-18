import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { NaturalPerformancePreservation } from "../../editorial/performance/natural-performance-preservation.js";
import { PerformanceSegment } from "../../editorial/performance/performance-types.js";

describe("RF-056 — NaturalPerformancePreservation Suite (REQ-056.030 - REQ-056.032)", () => {
  it("protects expressive human markers (BREATH, LAUGH, REFLECTIVE_PAUSE) with preservationWeight >= 0.75", () => {
    const humanSeg: PerformanceSegment = {
      id: "seg_human",
      sourceClipId: "clip_01",
      startSeconds: 0,
      endSeconds: 5,
      transcript: "Fue un momento de gran tensión... (risas).",
      confidence: 0.95,
      markers: ["BREATH", "LAUGH", "REFLECTIVE_PAUSE"],
    };

    const decisions = NaturalPerformancePreservation.evaluate(humanSeg);
    assert.equal(decisions.length, 3);
    assert.ok(decisions.every((d) => d.action === "PRESERVE"));
    assert.ok(decisions.every((d) => d.preservationScore >= 0.75));
    assert.ok(NaturalPerformancePreservation.hasProtectedHumanMarkers(humanSeg));
    assert.equal(NaturalPerformancePreservation.hasOnlyTechnicalErrors(humanSeg), false);
  });

  it("proposes removal for technical defects (FALSE_START, STUTTER, TECHNICAL_ERROR)", () => {
    const techSeg: PerformanceSegment = {
      id: "seg_tech",
      sourceClipId: "clip_02",
      startSeconds: 6,
      endSeconds: 8.5,
      transcript: "Yo... yo creo que...",
      confidence: 0.9,
      markers: ["FALSE_START", "STUTTER"],
    };

    const decisions = NaturalPerformancePreservation.evaluate(techSeg);
    assert.equal(decisions.length, 2);
    assert.ok(decisions.every((d) => d.action === "TRIM"));
    assert.ok(decisions.every((d) => d.technicalDefectScore > d.authenticityScore));
    assert.ok(NaturalPerformancePreservation.hasOnlyTechnicalErrors(techSeg));
  });

  it("routes ambiguous markers (HESITATION, FILLER) to REVIEW with confidence in [0, 1]", () => {
    const ambigSeg: PerformanceSegment = {
      id: "seg_ambig",
      sourceClipId: "clip_03",
      startSeconds: 9,
      endSeconds: 12,
      transcript: "Este... bueno, quizás.",
      confidence: 0.85,
      markers: ["FILLER", "HESITATION"],
    };

    const decisions = NaturalPerformancePreservation.evaluate(ambigSeg);
    assert.equal(decisions.length, 2);
    assert.ok(decisions.every((d) => d.action === "REVIEW"));
    assert.ok(decisions.every((d) => d.preservationScore >= 0.0 && d.preservationScore <= 1.0));
  });
});
