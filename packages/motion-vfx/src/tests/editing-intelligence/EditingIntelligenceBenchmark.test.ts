import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { ConstraintSolver } from "../../editing-intelligence/core/ConstraintSolver.js";
import { ContentModelBuilder } from "../../editing-intelligence/core/ContentModelBuilder.js";
import { SemanticEditPlanner } from "../../editing-intelligence/core/SemanticEditPlanner.js";

describe("Fase 14 — Editing Intelligence Benchmark Suite", () => {
  it("benchmarks 1,000 content models, 500 edit plans and 500 constraint evaluations", () => {
    const raw = [
      { start: 0, end: 3.0, text: "¿Cómo funciona la IA generativa?" },
      { start: 3.0, end: 6.0, text: "Requiere miles de GPUs y servidores." },
    ];

    // 1. Benchmark 1,000 Content Model Constructions
    const t0 = performance.now();
    for (let i = 0; i < 1000; i++) {
      ContentModelBuilder.buildContentModel(raw, "Tech");
    }
    const modelElapsed = performance.now() - t0;

    // 2. Benchmark 500 Semantic Edit Plan Generations
    const model = ContentModelBuilder.buildContentModel(raw, "Tech");
    const t1 = performance.now();
    for (let i = 0; i < 500; i++) {
      SemanticEditPlanner.generatePlan(model, "fast_social");
    }
    const planElapsed = performance.now() - t1;

    // 3. Benchmark 500 Constraint Solver Runs
    const t2 = performance.now();
    for (let i = 0; i < 500; i++) {
      ConstraintSolver.resolveCaptionPlacement({ x: 0.2, y: 0.7, width: 0.3, height: 0.2 }, "bottom");
      ConstraintSolver.snapAudioToVisual(4.0, 4.05);
    }
    const solverElapsed = performance.now() - t2;

    // Presupuestos: < 100ms para cada tarea
    assert.ok(modelElapsed < 100, `Content model took ${modelElapsed.toFixed(2)}ms (budget: <100ms)`);
    assert.ok(planElapsed < 100, `Edit planner took ${planElapsed.toFixed(2)}ms (budget: <100ms)`);
    assert.ok(solverElapsed < 100, `Constraint solver took ${solverElapsed.toFixed(2)}ms (budget: <100ms)`);
  });
});
