import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { IterativePlanPatcher } from "../../editing-intelligence/core/IterativePlanPatcher.js";
import { SemanticEditPlan } from "../../editing-intelligence/types/index.js";

describe("Fase 14 — Iterative Plan Patcher Tests", () => {
  it("applies delta durationMultiplier patch making all scenes faster", () => {
    const originalPlan: SemanticEditPlan = {
      id: "p1",
      pacingProfile: "medium_social",
      scenes: [
        { id: "s1", role: "hook", start: 0, duration: 4.0, shotType: "talking_head" },
        { id: "s2", role: "context", start: 4.0, duration: 4.0, shotType: "talking_head" },
      ],
      decisionLog: [],
      parameters: {},
    };

    // Parche: 20% más rápido (multiplier = 0.8)
    const patched = IterativePlanPatcher.applyPatch(originalPlan, {
      operation: "modify",
      target: "scenes",
      changes: { durationMultiplier: 0.8 },
    });

    assert.strictEqual(patched.scenes[0].duration, 3.2);
    assert.strictEqual(patched.scenes[1].start, 3.2);
    assert.strictEqual(patched.scenes[1].duration, 3.2);
  });
});
