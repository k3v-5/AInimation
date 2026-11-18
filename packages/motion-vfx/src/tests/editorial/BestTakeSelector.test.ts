import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { BestTakeSelector } from "../../editorial/performance/best-take-selector.js";
import { TakeCandidate } from "../../editorial/performance/performance-types.js";

describe("RF-056 — BestTakeSelector Suite (REQ-056.040)", () => {
  const takeA: TakeCandidate = {
    id: "take_01",
    transcript: "La fiscalía intervino la institución.",
    sourceClipId: "clip_01",
    startSeconds: 0,
    endSeconds: 4.5,
    semanticIntegrity: 0.95,
    phoneticClarity: 0.92,
    vocalEnergy: 0.88,
    visualStability: 0.9,
    eyeContact: 0.92,
    naturalPerformance: 0.9,
    continuity: 0.9,
    audioQuality: 0.95,
  };

  const takeB: TakeCandidate = {
    id: "take_02",
    transcript: "La fiscalía intervino la institución.",
    sourceClipId: "clip_02",
    startSeconds: 5,
    endSeconds: 10.0,
    semanticIntegrity: 0.75,
    phoneticClarity: 0.7,
    vocalEnergy: 0.6,
    visualStability: 0.7,
    eyeContact: 0.65,
    naturalPerformance: 0.7,
    continuity: 0.75,
    audioQuality: 0.8,
  };

  it("selects higher scoring candidate when clear winner exists and auto-selects (threshold >= 0.80)", () => {
    const selection = BestTakeSelector.select("grp_1", [takeA, takeB]);
    assert.equal(selection.selectedTakeId, "take_01");
    assert.ok(selection.winnerScore >= 0.8);
    assert.equal(selection.isAutoSelected, true);
    assert.equal(selection.recommendation, "SELECT");
  });

  it("resolves ties deterministically prioritizing semantic integrity over speed", () => {
    // Two takes with nearly identical score (< 0.02 delta) but takeA has higher semantic integrity
    const take1: TakeCandidate = {
      ...takeA,
      id: "take_tie_1",
      semanticIntegrity: 0.96,
      visualStability: 0.8,
    };
    const take2: TakeCandidate = {
      ...takeA,
      id: "take_tie_2",
      semanticIntegrity: 0.88,
      visualStability: 0.95,
    };

    const selection = BestTakeSelector.select("grp_tie", [take1, take2]);
    assert.equal(selection.selectedTakeId, "take_tie_1");
    assert.ok(selection.desempateApplied?.includes("integridad"));
  });

  it("marks recommendation as REVIEW when score is below threshold or score diff is tight", () => {
    const weakTake1: TakeCandidate = {
      ...takeB,
      id: "weak_1",
      semanticIntegrity: 0.65,
    };
    const weakTake2: TakeCandidate = {
      ...takeB,
      id: "weak_2",
      semanticIntegrity: 0.64,
    };

    const selection = BestTakeSelector.select("grp_weak", [weakTake1, weakTake2]);
    assert.equal(selection.isAutoSelected, false);
    assert.equal(selection.recommendation, "REVIEW");
  });

  it("handles single candidate and throws on empty list", () => {
    const single = BestTakeSelector.select("grp_single", [takeA]);
    assert.equal(single.selectedTakeId, "take_01");
    assert.ok(single.winnerScore >= 0.8);

    assert.throws(() => {
      BestTakeSelector.select("grp_empty", []);
    }, /cannot select take from empty candidates/);
  });
});
