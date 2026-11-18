import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { TextLayoutEngine } from "../../typography/layout/TextLayoutEngine.js";
import { GlyphTransformEngine } from "../../typography/motion/GlyphTransformEngine.js";
import { TextShaper } from "../../typography/shaping/TextShaper.js";
import { TextDocument } from "../../typography/types/index.js";

describe("Fase 5F — Typography Engine Performance Benchmark Suite", () => {
  it("benchmarks shaping, layout, and stagger transforms for 5,000 glyphs", () => {
    const longText = "ESTO ES UNA ANIMACION INCREIBLE CON KINETIC TYPOGRAPHY EN ALTA DEFINICION! ".repeat(50);

    const doc: TextDocument = {
      id: "doc_bench",
      content: longText,
      defaultStyle: {
        fontFamily: "Montserrat",
        fontSize: 48,
        fontWeight: 700,
        letterSpacing: 1,
        lineHeight: 1.2,
        alignment: "center",
      },
      defaultPaint: {
        fill: { r: 1, g: 1, b: 1 },
        strokes: [{ width: 4, color: { r: 0, g: 0, b: 0 } }],
      },
    };

    // 1. Benchmark shaping
    const t0 = performance.now();
    const shaped = TextShaper.shape(longText, doc.defaultStyle);
    const shapeElapsed = performance.now() - t0;
    assert.ok(shaped.glyphs.length >= 3500);

    // 2. Benchmark layout con line breaking
    const t1 = performance.now();
    const layout = TextLayoutEngine.calculateLayout(doc, { maxWidth: 1080, wrapping: "word" });
    const layoutElapsed = performance.now() - t1;
    assert.ok(layout.lines.length > 10);

    // 3. Benchmark kinetic stagger motion evaluation
    const t2 = performance.now();
    const transforms = GlyphTransformEngine.evaluateGlyphMotion(
      layout.glyphs,
      0.5,
      0.4,
      "random",
      0.02,
      12345
    );
    const motionElapsed = performance.now() - t2;
    assert.strictEqual(transforms.length, layout.glyphs.length);

    // Presupuesto: Todo el pipeline de 5,000 caracteres en < 500ms
    assert.ok(shapeElapsed < 200, `Shaping took ${shapeElapsed.toFixed(2)}ms (budget: <200ms)`);
    assert.ok(layoutElapsed < 200, `Layout took ${layoutElapsed.toFixed(2)}ms (budget: <200ms)`);
    assert.ok(motionElapsed < 200, `Motion eval took ${motionElapsed.toFixed(2)}ms (budget: <200ms)`);
  });
});
