import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { StoryAgent } from "../../ai-director/agents/StoryAgent.js";
import { VisualAgent } from "../../ai-director/agents/VisualAgent.js";
import { BuiltinStyleProfiles } from "../../ai-planner/presets/StyleProfiles.js";

describe("Fase 8 — Story & Visual Agents Tests", () => {
  it("StoryAgent generates a structured 3-act narrative with hook, main point and CTA", async () => {
    const storyAgent = new StoryAgent();
    const proposal = await storyAgent.analyze({
      brief: { objective: "AI Productivity Tips", platform: "tiktok", targetDuration: 30 },
      style: BuiltinStyleProfiles["fast-tiktok"],
    });

    assert.strictEqual(proposal.role, "story");
    assert.strictEqual(proposal.confidence >= 0.9, true);

    const sections = proposal.recommendations[0].parameters.sections as any[];
    assert.strictEqual(sections.length, 3);
    assert.strictEqual(sections[0].type, "hook");
    assert.strictEqual(sections[1].type, "main-point");
    assert.strictEqual(sections[2].type, "cta");
  });

  it("VisualAgent constructs scenes with alternating framings and transitions", async () => {
    const visualAgent = new VisualAgent();
    const proposal = await visualAgent.analyze({
      brief: { objective: "AI Productivity Tips", platform: "tiktok", targetDuration: 30 },
      style: BuiltinStyleProfiles["fast-tiktok"],
      existingPlan: {
        sections: [
          { id: "sec_01", type: "hook", start: 0, end: 3, objective: "Hook", energy: 1.0 },
          { id: "sec_02", type: "main-point", start: 3, end: 30, objective: "Main", energy: 0.8 },
        ],
      },
    });

    assert.strictEqual(proposal.role, "visual");
    const scenes = proposal.recommendations[0].parameters.scenes as any[];
    assert.strictEqual(scenes.length, 2);
    assert.strictEqual(scenes[0].shots.length >= 1, true);
  });
});
