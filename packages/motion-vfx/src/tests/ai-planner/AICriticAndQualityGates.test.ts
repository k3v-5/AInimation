import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AICritic } from "../../ai-planner/core/AICritic.js";
import { BuiltinStyleProfiles } from "../../ai-planner/presets/StyleProfiles.js";
import { EditingPlan } from "../../ai-planner/types/index.js";

describe("Fase 7 — AI Critic & Quality Gates Tests", () => {
  it("detects slow pacing and lack of CTA in TikTok editing plans", () => {
    const slowPlan: EditingPlan = {
      id: "plan_slow",
      version: 1,
      brief: { objective: "Slow Video", platform: "tiktok", targetDuration: 20 },
      style: BuiltinStyleProfiles["fast-tiktok"],
      sections: [
        { id: "sec_01", type: "main-point", start: 0, end: 20, objective: "Long single shot", energy: 0.5 },
      ],
      scenes: [
        {
          id: "sc_01",
          sectionId: "sec_01",
          purpose: "One long shot",
          start: 0,
          end: 20,
          shots: [
            { id: "shot_01", duration: 10, start: 0, purpose: "Long talking", framing: "close" },
            { id: "shot_02", duration: 10, start: 10, purpose: "More talking", framing: "close" },
          ],
        },
      ],
    };

    const critique = AICritic.critique(slowPlan);
    assert.ok(critique.pacingScore < 6.0); // Puntuación baja de ritmo por tomas de 10s
    assert.strictEqual(critique.issues.length >= 2, true); // Aviso de ritmo lento + falta de CTA
    assert.strictEqual(critique.suggestions.some((s) => s.action === "shorten_shots"), true);
  });
});
