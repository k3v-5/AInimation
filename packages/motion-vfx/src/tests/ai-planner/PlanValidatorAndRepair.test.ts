import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { PlanRepairEngine } from "../../ai-planner/core/PlanRepairEngine.js";
import { PlanValidator } from "../../ai-planner/core/PlanValidator.js";
import { BuiltinStyleProfiles } from "../../ai-planner/presets/StyleProfiles.js";
import { EditingPlan } from "../../ai-planner/types/index.js";

describe("Fase 7 — Plan Validator & Deterministic Repair Tests", () => {
  it("detects inverted section timestamps and non-positive shot durations", () => {
    const invalidPlan: EditingPlan = {
      id: "plan_err_01",
      version: 1,
      brief: { objective: "Test Error", platform: "tiktok", targetDuration: 30 },
      style: BuiltinStyleProfiles["fast-tiktok"],
      sections: [
        { id: "sec_01", type: "hook", start: 10, end: 5, objective: "Inverted", energy: 0.9 },
      ],
      scenes: [
        {
          id: "sc_01",
          sectionId: "sec_01",
          purpose: "Hook",
          start: 0,
          end: 5,
          shots: [{ id: "shot_01", duration: -2.0, start: 0, purpose: "Bad duration" }],
        },
      ],
    };

    const issues = PlanValidator.validate(invalidPlan);
    const errors = issues.filter((i) => i.severity === "error");
    assert.strictEqual(errors.length, 2);
    assert.throws(() => PlanValidator.assertValid(invalidPlan));

    // Reparar el plan deterministamente
    const repaired = PlanRepairEngine.repair(invalidPlan);
    assert.strictEqual(repaired.sections[0].start, 5);
    assert.strictEqual(repaired.sections[0].end, 10);
    assert.strictEqual(repaired.scenes[0].shots[0].duration, 2.0); // Clamped a valor por defecto

    // El plan reparado ahora debe pasar la validación
    assert.doesNotThrow(() => PlanValidator.assertValid(repaired));
  });
});
