import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { MotionBudgetManager } from "../../motion-graphics/core/MotionBudgetManager.js";

describe("Fase 11 — Motion Budget & Visual Complexity Tests", () => {
  it("calculates complexity score and determines if scene violates budget limits", () => {
    // 1. Escena simple dentro de presupuesto bajo
    const simpleScene = MotionBudgetManager.evaluateComplexity(2, 2, false, false, "low");
    assert.strictEqual(simpleScene.isWithinBudget, true);
    assert.strictEqual(simpleScene.score <= 0.4, true);

    // 2. Escena sobrecargada violando presupuesto bajo
    const overloadedScene = MotionBudgetManager.evaluateComplexity(8, 10, true, true, "low");
    assert.strictEqual(overloadedScene.isWithinBudget, false);
    assert.strictEqual(overloadedScene.score > 0.4, true);
  });
});
