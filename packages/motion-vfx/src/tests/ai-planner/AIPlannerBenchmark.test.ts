import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { EditingPlanCompiler } from "../../ai-planner/core/EditingPlanCompiler.js";
import { PlanRepairEngine } from "../../ai-planner/core/PlanRepairEngine.js";
import { PlanValidator } from "../../ai-planner/core/PlanValidator.js";
import { BuiltinStyleProfiles } from "../../ai-planner/presets/StyleProfiles.js";
import { EditingPlan } from "../../ai-planner/types/index.js";

describe("Fase 7 — AI Planner Benchmark Suite", () => {
  it("benchmarks validating, repairing and compiling 1,000 editing plans", () => {
    const templatePlan: EditingPlan = {
      id: "bench_plan",
      version: 1,
      brief: { objective: "Bench", platform: "tiktok", targetDuration: 30 },
      style: BuiltinStyleProfiles["fast-tiktok"],
      sections: [
        { id: "s1", type: "hook", start: 0, end: 5, objective: "Hook", energy: 1 },
        { id: "s2", type: "main-point", start: 5, end: 25, objective: "Main", energy: 0.8 },
        { id: "s3", type: "cta", start: 25, end: 30, objective: "CTA", energy: 0.9 },
      ],
      scenes: [
        {
          id: "sc1",
          sectionId: "s1",
          purpose: "Hook",
          start: 0,
          end: 5,
          shots: [{ id: "sh1", duration: 5, start: 0, purpose: "Shot 1" }],
        },
        {
          id: "sc2",
          sectionId: "s2",
          purpose: "Main",
          start: 5,
          end: 25,
          shots: [{ id: "sh2", duration: 20, start: 5, purpose: "Shot 2" }],
        },
      ],
    };

    // 1. Benchmark 1,000 Validations
    const t0 = performance.now();
    for (let i = 0; i < 1000; i++) {
      PlanValidator.validate(templatePlan);
    }
    const valElapsed = performance.now() - t0;

    // 2. Benchmark 1,000 Repairs
    const t1 = performance.now();
    for (let i = 0; i < 1000; i++) {
      PlanRepairEngine.repair(templatePlan);
    }
    const repElapsed = performance.now() - t1;

    // 3. Benchmark 500 Compilations
    const t2 = performance.now();
    for (let i = 0; i < 500; i++) {
      EditingPlanCompiler.compile(templatePlan);
    }
    const compElapsed = performance.now() - t2;

    // Presupuesto: < 100ms para cada tarea
    assert.ok(valElapsed < 100, `Validation took ${valElapsed.toFixed(2)}ms (budget: <100ms)`);
    assert.ok(repElapsed < 100, `Repair took ${repElapsed.toFixed(2)}ms (budget: <100ms)`);
    assert.ok(compElapsed < 150, `Compilation took ${compElapsed.toFixed(2)}ms (budget: <150ms)`);
  });
});
