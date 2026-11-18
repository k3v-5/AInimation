import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AIDirector } from "../../ai-director/core/AIDirector.js";

describe("Fase 8 — AI Director Multi-Agent Workflow Tests", () => {
  it("orchestrates a full multi-agent session from brief to validated EditingPlan", async () => {
    const director = new AIDirector();
    const session = await director.directSession({
      objective: "10x Productivity with AI Agents",
      platform: "tiktok",
      targetDuration: 30.0,
      styleId: "fast-tiktok",
    });

    assert.strictEqual(session.state, "approved");
    assert.strictEqual(session.plan !== undefined, true);
    assert.strictEqual(session.plan?.sections.length, 3);
    assert.strictEqual(session.plan?.scenes.length, 3);
    assert.strictEqual(session.plan?.captions !== undefined, true);
    assert.strictEqual(session.plan?.audio !== undefined, true);
    assert.strictEqual(session.decisions.length >= 3, true);
  });
});
