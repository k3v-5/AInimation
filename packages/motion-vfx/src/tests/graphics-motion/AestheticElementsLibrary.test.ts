import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AestheticElementsLibrary } from "../../graphics-motion/core/AestheticElementsLibrary.js";

describe("Graphics Motion — AestheticElementsLibrary Tests", () => {
  it("generates well-formed animated highlighter ExtendScript snippet", () => {
    const snippet = AestheticElementsLibrary.generateHighlighterSnippet(
      "comp",
      "Highlighter_Keyword_01",
      [540, 720],
      1.5,
      0.4,
      { width: 380, height: 50, roundness: 12 }
    );

    assert.ok(snippet.includes('var hl = comp.layers.addShape()'));
    assert.ok(snippet.includes('hl.name = "Highlighter_Keyword_01"'));
    assert.ok(snippet.includes('hl.blendingMode = BlendingMode.MULTIPLY'));
    assert.ok(snippet.includes('hl.transform.scale.setValueAtTime(1.5, [0, 100])'));
    assert.ok(snippet.includes('hl.transform.scale.setValueAtTime(1.9, [100, 100])'));
  });

  it("generates well-formed tape sticker ExtendScript snippet", () => {
    const snippet = AestheticElementsLibrary.generateTapeStickerSnippet(
      "comp",
      "Tape_Corner_01",
      [300, 400],
      0.0,
      5.0,
      { width: 160, height: 45, rotationDeg: 7.5 }
    );

    assert.ok(snippet.includes('var tape = comp.layers.addShape()'));
    assert.ok(snippet.includes('tape.name = "Tape_Corner_01"'));
    assert.ok(snippet.includes('tape.transform.rotation.setValue(7.5)'));
  });

  it("generates retro camcorder HUD snippet with blinking REC indicator", () => {
    const snippet = AestheticElementsLibrary.generateCamcorderHUDSnippet(
      "comp",
      1080,
      1920,
      0.0,
      10.0,
      { title: "LIVE // 4K CINEMATIC" }
    );

    assert.ok(snippet.includes('HUD_REC_Indicator'));
    assert.ok(snippet.includes('HUD_Meta_Header'));
    assert.ok(snippet.includes('LIVE // 4K CINEMATIC'));
    assert.ok(snippet.includes('Math.floor(time * 2) % 2 === 0 ? 100 : 0'));
  });
});
