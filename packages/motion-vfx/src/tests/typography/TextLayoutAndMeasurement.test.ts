import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { TextLayoutEngine } from "../../typography/layout/TextLayoutEngine.js";
import { TextDocument } from "../../typography/types/index.js";

describe("Fase 5F — Text Layout, Line Breaking & Visual Bounds Tests", () => {
  const doc: TextDocument = {
    id: "doc_test",
    content: "Esto es una animación increíble",
    defaultStyle: {
      fontFamily: "Inter",
      fontSize: 60,
      fontWeight: 700,
      letterSpacing: 0,
      lineHeight: 1.25,
      alignment: "center",
    },
    defaultPaint: {
      fill: { r: 1, g: 1, b: 1 },
      strokes: [{ width: 10, color: { r: 0, g: 0, b: 0 } }],
      shadow: { offsetX: 4, offsetY: 8, blur: 16, color: { r: 0, g: 0, b: 0 } },
      background: {
        color: { r: 0, g: 0, b: 0 },
        padding: { top: 20, right: 30, bottom: 20, left: 30 },
      },
    },
  };

  it("breaks lines accurately according to maxWidth constraint", () => {
    // Con maxWidth = 500px debe dividir en múltiples líneas
    const layout = TextLayoutEngine.calculateLayout(doc, { maxWidth: 500, wrapping: "word" });
    assert.ok(layout.lines.length >= 2);
    assert.strictEqual(layout.lines[0].lineIndex, 0);
    assert.ok(layout.layoutBounds.width <= 500);
  });

  it("calculates visualBounds with expansion for strokes, shadows and backgrounds", () => {
    const layout = TextLayoutEngine.calculateLayout(doc);
    // visualBounds debe ser estrictamente más grande que layoutBounds
    assert.ok(layout.visualBounds.width > layout.layoutBounds.width);
    assert.ok(layout.visualBounds.height > layout.layoutBounds.height);
    assert.ok(layout.visualBounds.x < layout.layoutBounds.x);
    assert.ok(layout.visualBounds.y < layout.layoutBounds.y);
  });
});
