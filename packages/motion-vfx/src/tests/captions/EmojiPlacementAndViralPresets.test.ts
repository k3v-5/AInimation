import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { EmojiPlacementEngine } from "../../captions/icons/EmojiPlacementEngine.js";
import { ViralCaptionPresetRegistry, VIRAL_CAPTION_PRESETS } from "../../captions/presets/ViralCaptionPresets.js";
import { PositionedWord } from "../../captions/types/index.js";
import { CaptionPresetError } from "../../errors/index.js";

describe("Fase 16 — Emoji Placement Engine Tests", () => {
  it("matches keywords to semantic emojis and computes placement coordinates", () => {
    const engine = new EmojiPlacementEngine();

    const word: PositionedWord = {
      id: "w1",
      text: "dinero",
      start: 0,
      end: 0.5,
      index: 0,
      x: 100,
      y: 500,
      width: 140,
      height: 70,
      line: 0,
    };

    const match = engine.findMatchForWord(word);
    assert.ok(match);
    assert.equal(match.assetRef, "💸");
    assert.equal(match.semanticTag, "money");

    const placement = engine.createPlacementInstance(word, match);
    assert.equal(placement.assetRef, "💸");
    assert.ok(placement.y < word.y); // posicionado encima de la palabra
    assert.equal(placement.opacity, 1.0);
  });

  it("returns undefined when no emoji match is found", () => {
    const engine = new EmojiPlacementEngine();
    const word: PositionedWord = {
      id: "w2",
      text: "computadora",
      start: 0,
      end: 0.5,
      index: 0,
      x: 0,
      y: 0,
      width: 100,
      height: 50,
      line: 0,
    };

    assert.equal(engine.findMatchForWord(word), undefined);
  });
});

describe("Fase 16 — Viral Caption Presets Tests", () => {
  const presetIds = ["hormozi-impact", "beast-clean", "vox-minimal", "karaoke-gradient", "neon-glow"] as const;

  it("registers and discovers all 5 viral presets with distinct design identities", () => {
    const allPresets = ViralCaptionPresetRegistry.listPresets();
    assert.equal(allPresets.length, 5);

    for (const id of presetIds) {
      const preset = ViralCaptionPresetRegistry.getPreset(id);
      assert.equal(preset.id, id);
      assert.ok(preset.name.length > 0);
      assert.ok(preset.style.fontSize > 0);
      assert.ok(preset.backgroundConfig);
    }
  });

  it("guarantees preset immutability when applying custom parameter overrides", () => {
    const originalFontSize = VIRAL_CAPTION_PRESETS["hormozi-impact"].style.fontSize;

    const customized = ViralCaptionPresetRegistry.getPreset("hormozi-impact", {
      fontSize: 90,
      emojisEnabled: false,
    });

    assert.equal(customized.style.fontSize, 90);
    assert.equal(customized.emojisEnabled, false);

    // El preset original base debe permanecer intacto
    assert.equal(VIRAL_CAPTION_PRESETS["hormozi-impact"].style.fontSize, originalFontSize);
    assert.equal(VIRAL_CAPTION_PRESETS["hormozi-impact"].emojisEnabled, true);
  });

  it("throws CaptionPresetError on unknown preset id", () => {
    assert.throws(() => ViralCaptionPresetRegistry.getPreset("unknown-preset" as any), CaptionPresetError);
  });
});
