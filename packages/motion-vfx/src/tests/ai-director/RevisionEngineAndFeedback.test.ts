import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AIDirector } from "../../ai-director/core/AIDirector.js";
import { RevisionEngine } from "../../ai-director/core/RevisionEngine.js";

describe("Fase 8 — Revision Engine & Human Feedback Tests", () => {
  it("partially updates plan upon human feedback without corrupting remaining scenes", async () => {
    const director = new AIDirector();
    const session = await director.directSession({
      objective: "AI Video Editing Revolution",
      platform: "tiktok",
      targetDuration: 25.0,
    });

    const originalPlan = session.plan!;

    // 1. Feedback: "no music"
    const revisedNoMusic = RevisionEngine.revise(originalPlan, {
      category: "audio",
      instruction: "Please remove the background music, I want silence.",
    });

    assert.strictEqual(revisedNoMusic.audio?.musicAssetId, undefined);
    assert.strictEqual(revisedNoMusic.scenes.length, originalPlan.scenes.length); // Escenas intactas
    assert.strictEqual(revisedNoMusic.version, 2);

    // 2. Feedback: "karaoke style captions"
    const revisedKaraoke = RevisionEngine.revise(revisedNoMusic, {
      category: "caption",
      instruction: "Switch to karaoke captions style.",
    });

    assert.strictEqual(revisedKaraoke.captions?.style, "karaoke");
    assert.strictEqual(revisedKaraoke.version, 3);
  });
});
