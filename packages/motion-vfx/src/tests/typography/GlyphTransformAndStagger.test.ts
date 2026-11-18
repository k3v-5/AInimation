import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { TextLayoutEngine } from "../../typography/layout/TextLayoutEngine.js";
import { GlyphTransformEngine } from "../../typography/motion/GlyphTransformEngine.js";
import { TextDocument } from "../../typography/types/index.js";

describe("Fase 5F — Glyph Transforms & Deterministic Stagger Tests", () => {
  it("calculates forward, reverse, and center stagger delays accurately", () => {
    const total = 5;
    const step = 0.1;

    // Forward: 0.0, 0.1, 0.2, 0.3, 0.4
    assert.strictEqual(GlyphTransformEngine.calculateStaggerDelay(0, total, "forward", step), 0.0);
    assert.strictEqual(GlyphTransformEngine.calculateStaggerDelay(4, total, "forward", step), 0.4);

    // Reverse: 0.4, 0.3, 0.2, 0.1, 0.0
    assert.strictEqual(GlyphTransformEngine.calculateStaggerDelay(0, total, "reverse", step), 0.4);
    assert.strictEqual(GlyphTransformEngine.calculateStaggerDelay(4, total, "reverse", step), 0.0);

    // Center: center is index 2 -> dist from center 2 is 0.0
    assert.strictEqual(GlyphTransformEngine.calculateStaggerDelay(2, total, "center", step), 0.0);
  });

  it("guarantees 100% determinism in random stagger with PRNG seed", () => {
    const total = 10;
    const seed = 98765;

    const run1 = Array.from({ length: total }, (_, i) =>
      GlyphTransformEngine.calculateStaggerDelay(i, total, "random", 0.05, seed)
    );
    const run2 = Array.from({ length: total }, (_, i) =>
      GlyphTransformEngine.calculateStaggerDelay(i, total, "random", 0.05, seed)
    );

    assert.deepStrictEqual(run1, run2);
  });

  it("evaluates kinetic glyph motion transforms at local timestamps", () => {
    const doc: TextDocument = {
      id: "doc_m",
      content: "POP",
      defaultStyle: { fontFamily: "Inter", fontSize: 60, fontWeight: 700, letterSpacing: 0, lineHeight: 1.2, alignment: "left" },
      defaultPaint: { fill: { r: 1, g: 1, b: 1 } },
    };

    const layout = TextLayoutEngine.calculateLayout(doc);
    // En t = 0.0s -> inicio de animación, primer glifo comienza con escala 0 y opacidad 0
    const transformsAt0 = GlyphTransformEngine.evaluateGlyphMotion(layout.glyphs, 0.0, 0.5, "forward", 0.1);
    assert.strictEqual(transformsAt0.length, 3);
    assert.strictEqual(transformsAt0[0].opacity, 0.0);

    // En t = 1.0s -> todos los glifos han completado la animación (opacity = 1.0, scale = 1.0)
    const transformsAt1 = GlyphTransformEngine.evaluateGlyphMotion(layout.glyphs, 1.0, 0.5, "forward", 0.1);
    assert.strictEqual(transformsAt1[0].opacity, 1.0);
    assert.strictEqual(transformsAt1[0].scale.x, 1.0);
    assert.strictEqual(transformsAt1[2].opacity, 1.0);
  });
});
