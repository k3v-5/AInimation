import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { ConstraintSolver } from "../../editing-intelligence/core/ConstraintSolver.js";
import { PlanValidatorAndRepair } from "../../editing-intelligence/core/PlanValidatorAndRepair.js";
import { SemanticEditPlan } from "../../editing-intelligence/types/index.js";

describe("Fase 14 — Constraint Solver & Plan Repair Tests", () => {
  it("resolves caption placement to top when face is located in bottom area", () => {
    const bottomFace = { x: 0.3, y: 0.7, width: 0.4, height: 0.25 };
    const placement = ConstraintSolver.resolveCaptionPlacement(bottomFace, "bottom");
    assert.strictEqual(placement, "top");
  });

  it("snaps audio triggers falling within tolerance to the exact visual timestamp", () => {
    const visualTime = 4.0;
    const rawAudioTime = 4.05; // 50ms después
    const snapped = ConstraintSolver.snapAudioToVisual(visualTime, rawAudioTime, 0.1);
    assert.strictEqual(snapped, 4.0);
  });

  it("automatically repairs misaligned scenes with invalid durations", () => {
    const brokenPlan: SemanticEditPlan = {
      id: "plan_broken",
      pacingProfile: "fast_social",
      scenes: [
        { id: "s1", role: "hook", start: 0, duration: 2.0, shotType: "talking_head" },
        { id: "s2", role: "context", start: 5.0, duration: -1.0, shotType: "talking_head" }, // Duración negativa y gap
      ],
      decisionLog: [],
      parameters: {},
    };

    const res = PlanValidatorAndRepair.validateAndRepair(brokenPlan);
    assert.strictEqual(res.isValid, false);
    assert.strictEqual(res.repairedPlan !== undefined, true);
    assert.strictEqual(res.repairedPlan?.scenes[1].duration, 1.5);
    assert.strictEqual(res.repairedPlan?.scenes[1].start, 2.0); // Contiguo tras s1 (2.0)
  });
});
