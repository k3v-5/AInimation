import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { RotoMaskEngine } from "../../tracking-rotoscopy/core/RotoMaskEngine.js";
import { RotoMask } from "../../tracking-rotoscopy/types/index.js";

describe("Fase 12 — RotoMask & Subject Cutout Tests", () => {
  it("evaluates mask alpha across feather border and handles inversion", () => {
    const mask: RotoMask = {
      id: "mask_person",
      trackId: "track_person",
      feather: 20,
      opacity: 1.0,
      invert: false,
    };

    // 1. Totalmente dentro (-20px): alpha = 1.0
    const inside = RotoMaskEngine.evaluateMaskAlpha(mask, -25);
    assert.strictEqual(inside, 1.0);

    // 2. Justo en el borde (0px): alpha = 0.5
    const edge = RotoMaskEngine.evaluateMaskAlpha(mask, 0);
    assert.strictEqual(edge, 0.5);

    // 3. Totalmente fuera (+20px): alpha = 0.0
    const outside = RotoMaskEngine.evaluateMaskAlpha(mask, 25);
    assert.strictEqual(outside, 0.0);

    // 4. Máscara invertida en el borde: 1.0 - 0.5 = 0.5
    const invertedEdge = RotoMaskEngine.evaluateMaskAlpha({ ...mask, invert: true }, 0);
    assert.strictEqual(invertedEdge, 0.5);
  });

  it("builds correct canonical occlusion layers order for text behind person", () => {
    const layers = RotoMaskEngine.buildOcclusionLayerOrder("bg_01", "text_title", "person_cutout");
    assert.deepStrictEqual(layers, ["bg_01", "text_title", "person_cutout"]);
  });
});
