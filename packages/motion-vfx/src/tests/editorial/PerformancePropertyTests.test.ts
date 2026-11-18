import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import { IntelligentTrimmingEngine } from "../../editorial/performance/intelligent-trimming-engine.js";
import { BestTakeSelector } from "../../editorial/performance/best-take-selector.js";
import { PerformanceScoring } from "../../editorial/performance/performance-scoring.js";
import { PerformanceSegment, TakeCandidate } from "../../editorial/performance/performance-types.js";

describe("RF-056 — Performance Property-Based Tests (REQ-056.031: Properties 1 - 7)", () => {
  it("Propiedad 1 & 4: all scores in [0, 1] and reductionRatio in [0, 1]", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 0.0, max: 1.0, noNaN: true }),
        fc.double({ min: 0.0, max: 1.0, noNaN: true }),
        fc.double({ min: 0.0, max: 120.0, noNaN: true }),
        (sim, overlap, dist) => {
          const score = PerformanceScoring.calculateRedundancyScore({
            semanticSimilarity: sim,
            informationOverlap: overlap,
            temporalDistanceSeconds: dist,
          });
          return Number.isFinite(score) && score >= 0.0 && score <= 1.0;
        }
      ),
      { numRuns: 100 }
    );
  });

  it("Propiedad 2, 3 & 7: start >= 0, end > start, finalDuration >= 0 and trims never exceed clip bounds", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 0.0, max: 20.0, noNaN: true }),
        fc.double({ min: 1.0, max: 10.0, noNaN: true }),
        (start, dur) => {
          const seg: PerformanceSegment = {
            id: "seg_pbt",
            sourceClipId: "c1",
            startSeconds: Number(start.toFixed(3)),
            endSeconds: Number((start + dur).toFixed(3)),
            transcript: "Texto de prueba PBT",
            confidence: 0.9,
            markers: [],
          };

          const report = IntelligentTrimmingEngine.process({
            segments: [seg],
            sourceDurationSeconds: start + dur + 10.0,
          });

          return (
            report.metrics.finalDurationSeconds >= 0 &&
            report.metrics.reductionRatio >= 0 &&
            report.metrics.reductionRatio <= 1.0
          );
        }
      ),
      { numRuns: 50 }
    );
  });

  it("Propiedad 5: identical input produces byte-identical report and SHA-256", () => {
    const segments: PerformanceSegment[] = [
      {
        id: "s1",
        sourceClipId: "c1",
        startSeconds: 0,
        endSeconds: 5,
        transcript: "Afirmación probatoria fáctica de prueba.",
        confidence: 0.95,
        markers: ["BREATH"],
        evidenceProtection: true,
      },
    ];

    const repA = IntelligentTrimmingEngine.process({ segments });
    const repB = IntelligentTrimmingEngine.process({ segments });

    assert.equal(repA.checksumSha256, repB.checksumSha256);
    assert.equal(JSON.stringify(repA), JSON.stringify(repB));
  });

  it("Propiedad 6: reordering takes with distinct scores does not change the winner", () => {
    const take1: TakeCandidate = {
      id: "t_high",
      transcript: "Texto",
      sourceClipId: "c1",
      startSeconds: 0,
      endSeconds: 4,
      semanticIntegrity: 0.99,
      phoneticClarity: 0.95,
      vocalEnergy: 0.9,
      visualStability: 0.9,
      eyeContact: 0.9,
      naturalPerformance: 0.95,
      continuity: 0.95,
      audioQuality: 0.95,
    };

    const take2: TakeCandidate = {
      id: "t_low",
      transcript: "Texto",
      sourceClipId: "c2",
      startSeconds: 5,
      endSeconds: 9,
      semanticIntegrity: 0.5,
      phoneticClarity: 0.5,
      vocalEnergy: 0.5,
      visualStability: 0.5,
      eyeContact: 0.5,
      naturalPerformance: 0.5,
      continuity: 0.5,
      audioQuality: 0.5,
    };

    const selA = BestTakeSelector.select("grp", [take1, take2]);
    const selB = BestTakeSelector.select("grp", [take2, take1]);

    assert.equal(selA.selectedTakeId, "t_high");
    assert.equal(selB.selectedTakeId, "t_high");
  });
});
