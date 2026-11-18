import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { EditingPlanCompiler } from "../../ai-planner/core/EditingPlanCompiler.js";
import { BuiltinStyleProfiles } from "../../ai-planner/presets/StyleProfiles.js";
import { EditingPlan } from "../../ai-planner/types/index.js";

describe("Fase 7 — Editing Plan Compiler Tests", () => {
  it("compiles structured EditingPlan into a complete project with video and audio tracks", () => {
    const plan: EditingPlan = {
      id: "plan_tiktok_01",
      version: 1,
      brief: {
        objective: "Viral TikTok on AI",
        platform: "tiktok",
        targetDuration: 15.0,
      },
      style: BuiltinStyleProfiles["fast-tiktok"],
      sections: [
        { id: "sec_hook", type: "hook", start: 0, end: 3, objective: "Grab attention", energy: 1.0 },
        { id: "sec_main", type: "main-point", start: 3, end: 12, objective: "Explain core idea", energy: 0.8 },
        { id: "sec_cta", type: "cta", start: 12, end: 15, objective: "Call to action", energy: 0.9 },
      ],
      scenes: [
        {
          id: "sc_01",
          sectionId: "sec_hook",
          purpose: "Hook scene",
          start: 0,
          end: 3,
          shots: [
            { id: "sh_01", assetId: "broll_ai_chip", purpose: "Close-up AI chip", start: 0, duration: 3.0 },
          ],
        },
        {
          id: "sc_02",
          sectionId: "sec_main",
          purpose: "Main scene",
          start: 3,
          end: 12,
          shots: [
            { id: "sh_02", assetId: "broll_person_laptop", purpose: "Person coding", start: 3, duration: 4.5 },
            { id: "sh_03", assetId: "broll_chart_growth", purpose: "Chart rising", start: 7.5, duration: 4.5 },
          ],
        },
      ],
      audio: {
        musicAssetId: "audio_cyber_beat",
        musicVolume: 0.35,
        enableDucking: true,
      },
    };

    const compiled = EditingPlanCompiler.compile(plan);
    assert.strictEqual(compiled.width, 1080); // Formato vertical 9:16 para TikTok
    assert.strictEqual(compiled.height, 1920);
    assert.strictEqual(compiled.duration, 15.0);
    assert.strictEqual(compiled.sectionCount, 3);
    assert.strictEqual(compiled.shotCount, 3);
    assert.strictEqual(compiled.timeline.tracks.length, 2); // Video track + Audio track
  });
});
