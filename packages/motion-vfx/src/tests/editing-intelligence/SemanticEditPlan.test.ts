import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { ContentModelBuilder } from "../../editing-intelligence/core/ContentModelBuilder.js";
import { SemanticEditPlanner } from "../../editing-intelligence/core/SemanticEditPlanner.js";

describe("Fase 14 — Semantic Edit Plan Generation Tests", () => {
  it("generates structured edit plan with narrative roles, decision logs and B-roll requests", () => {
    const raw = [
      { start: 0, end: 3.0, text: "¿Cómo funciona la IA generativa?" },
      { start: 3.0, end: 6.0, text: "Requiere miles de GPUs y servidores." },
    ];
    const model = ContentModelBuilder.buildContentModel(raw, "Technology");
    const plan = SemanticEditPlanner.generatePlan(model, "fast_social");

    assert.strictEqual(plan.scenes.length >= 3, true);
    assert.strictEqual(plan.scenes[0].role, "hook");
    assert.strictEqual(plan.decisionLog.length, plan.scenes.length);

    const brollScene = plan.scenes.find((s) => s.shotType === "b_roll");
    assert.strictEqual(brollScene !== undefined, true);
    assert.strictEqual(brollScene?.brollKeyword, "technology");
  });
});
