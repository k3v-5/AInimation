import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AudioAgent } from "../../ai-director/agents/AudioAgent.js";
import { CaptionAgent } from "../../ai-director/agents/CaptionAgent.js";
import { BuiltinStyleProfiles } from "../../ai-planner/presets/StyleProfiles.js";

describe("Fase 8 — Audio & Caption Agents Tests", () => {
  it("AudioAgent proposes music track, ducking and transition SFX", async () => {
    const audioAgent = new AudioAgent();
    const proposal = await audioAgent.analyze({
      brief: { objective: "AI Beats", platform: "tiktok", targetDuration: 20 },
      style: BuiltinStyleProfiles["fast-tiktok"],
    });

    assert.strictEqual(proposal.role, "audio");
    const audio = proposal.recommendations[0].parameters.audio as any;
    assert.strictEqual(audio.enableDucking, true);
    assert.strictEqual(audio.soundEffects.length >= 2, true);
  });

  it("CaptionAgent proposes kinetic styled captions with word emphasis", async () => {
    const captionAgent = new CaptionAgent();
    const proposal = await captionAgent.analyze({
      brief: { objective: "VIRAL CAPTION TITLE", platform: "tiktok", targetDuration: 15 },
      style: BuiltinStyleProfiles["fast-tiktok"],
    });

    assert.strictEqual(proposal.role, "caption");
    const captions = proposal.recommendations[0].parameters.captions as any;
    assert.strictEqual(captions.style, "word-pop");
    assert.strictEqual(captions.segments[0].isEmphasized, true);
  });
});
