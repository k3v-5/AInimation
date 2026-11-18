import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AICritic } from "../../ai-planner/core/AICritic.js";
import { EditingPlanCompiler } from "../../ai-planner/core/EditingPlanCompiler.js";
import { PlanValidator } from "../../ai-planner/core/PlanValidator.js";
import { BuiltinStyleProfiles } from "../../ai-planner/presets/StyleProfiles.js";
import { EditingPlan } from "../../ai-planner/types/index.js";

describe("Fase 7 — Golden Editing Plans Suite", () => {
  it("compiles and validates a 35-second golden TikTok plan flawlessly", () => {
    const goldenTikTok: EditingPlan = {
      id: "golden_tiktok_35s",
      version: 1,
      brief: {
        objective: "35s AI Automation Breakdown",
        platform: "tiktok",
        targetDuration: 35.0,
      },
      style: BuiltinStyleProfiles["fast-tiktok"],
      sections: [
        { id: "sec_hook", type: "hook", start: 0, end: 3, objective: "Aggressive hook", energy: 1.0 },
        { id: "sec_setup", type: "setup", start: 3, end: 8, objective: "State the problem", energy: 0.8 },
        { id: "sec_main", type: "main-point", start: 8, end: 20, objective: "Reveal the solution", energy: 0.9 },
        { id: "sec_example", type: "example", start: 20, end: 29, objective: "Live demo proof", energy: 0.85 },
        { id: "sec_cta", type: "cta", start: 29, end: 35, objective: "Subscribe CTA", energy: 0.95 },
      ],
      scenes: [
        {
          id: "sc_hook",
          sectionId: "sec_hook",
          purpose: "Hook visual",
          start: 0,
          end: 3,
          shots: [{ id: "sh_01", duration: 3.0, start: 0, purpose: "Close-up reaction", framing: "close" }],
        },
        {
          id: "sc_setup",
          sectionId: "sec_setup",
          purpose: "Problem statement",
          start: 3,
          end: 8,
          shots: [
            { id: "sh_02", duration: 2.5, start: 3, purpose: "B-roll frustration", framing: "medium" },
            { id: "sh_03", duration: 2.5, start: 5.5, purpose: "Overhead desk", framing: "overhead" },
          ],
        },
        {
          id: "sc_main",
          sectionId: "sec_main",
          purpose: "Solution breakdown",
          start: 8,
          end: 20,
          shots: [
            { id: "sh_04", duration: 3.0, start: 8, purpose: "AI tool interface", framing: "wide" },
            { id: "sh_05", duration: 3.0, start: 11, purpose: "Fast typing code", framing: "close" },
            { id: "sh_06", duration: 3.0, start: 14, purpose: "Automation pipeline", framing: "medium" },
            { id: "sh_07", duration: 3.0, start: 17, purpose: "Result graphic", framing: "wide" },
          ],
        },
        {
          id: "sc_example",
          sectionId: "sec_example",
          purpose: "Proof metrics",
          start: 20,
          end: 29,
          shots: [
            { id: "sh_08", duration: 3.0, start: 20, purpose: "Revenue chart", framing: "close" },
            { id: "sh_09", duration: 3.0, start: 23, purpose: "Success dashboard", framing: "medium" },
            { id: "sh_10", duration: 3.0, start: 26, purpose: "Speaker smile", framing: "close" },
          ],
        },
        {
          id: "sc_cta",
          sectionId: "sec_cta",
          purpose: "Call to action",
          start: 29,
          end: 35,
          shots: [
            { id: "sh_11", duration: 3.0, start: 29, purpose: "Point to bio", framing: "medium" },
            { id: "sh_12", duration: 3.0, start: 32, purpose: "Logo outro", framing: "wide" },
          ],
        },
      ],
      audio: {
        musicAssetId: "audio_hyper_trap",
        musicVolume: 0.3,
        enableDucking: true,
      },
    };

    assert.doesNotThrow(() => PlanValidator.assertValid(goldenTikTok));

    const critique = AICritic.critique(goldenTikTok);
    assert.ok(critique.overallScore >= 8.0); // Calificación sobresaliente

    const compiled = EditingPlanCompiler.compile(goldenTikTok);
    assert.strictEqual(compiled.width, 1080);
    assert.strictEqual(compiled.height, 1920);
    assert.strictEqual(compiled.shotCount, 12);
  });
});
