import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { TextLayoutEngine } from "../../typography/layout/TextLayoutEngine.js";
import { TextDocument } from "../../typography/types/index.js";

describe("Fase 5F — Rich Text Spans & Paint Stack Tests", () => {
  it("applies per-span style and paint overrides across character ranges", () => {
    const doc: TextDocument = {
      id: "doc_rich",
      content: "HOLA MUNDO",
      defaultStyle: {
        fontFamily: "Inter",
        fontSize: 60,
        fontWeight: 400,
        letterSpacing: 0,
        lineHeight: 1.2,
        alignment: "left",
      },
      defaultPaint: {
        fill: { r: 1, g: 1, b: 1 }, // Blanco
      },
      spans: [
        {
          start: 5, // 'MUNDO'
          end: 10,
          paint: {
            fill: { r: 1, g: 0.9, b: 0 }, // Amarillo
          },
        },
      ],
    };

    const layout = TextLayoutEngine.calculateLayout(doc);
    assert.strictEqual(layout.glyphs.length, 10);

    // 'H' (char 0) -> Blanco
    const g0 = layout.glyphs[0];
    assert.strictEqual((g0.paint.fill as any).r, 1);
    assert.strictEqual((g0.paint.fill as any).g, 1);
    assert.strictEqual((g0.paint.fill as any).b, 1);

    // 'M' (char 5) -> Amarillo
    const g5 = layout.glyphs[5];
    assert.strictEqual((g5.paint.fill as any).r, 1);
    assert.strictEqual((g5.paint.fill as any).g, 0.9);
    assert.strictEqual((g5.paint.fill as any).b, 0);
  });
});
