import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { TextLayoutEngine } from "../../typography/layout/TextLayoutEngine.js";
import { ArcTextPath, LinearTextPath, TextPathMapper } from "../../typography/path/TextPath.js";
import { TextDocument } from "../../typography/types/index.js";

describe("Fase 5F — Text-On-Path Parametric Mapping Tests", () => {
  const doc: TextDocument = {
    id: "doc_path",
    content: "HELLO",
    defaultStyle: { fontFamily: "Inter", fontSize: 60, fontWeight: 700, letterSpacing: 0, lineHeight: 1.2, alignment: "left" },
    defaultPaint: { fill: { r: 1, g: 1, b: 1 } },
  };

  it("maps glyphs along a straight linear text path", () => {
    const path = new LinearTextPath(0, 0, 500, 0); // Línea horizontal de 500px
    const layout = TextLayoutEngine.calculateLayout(doc);

    const mapped = TextPathMapper.mapGlyphsToPath(layout.glyphs, path);
    assert.strictEqual(mapped.length, 5);
    assert.strictEqual(mapped[0].position.y, 0);
    assert.ok(mapped[4].position.x > mapped[0].position.x);
    assert.strictEqual(mapped[0].rotation, 0);
  });

  it("maps glyphs along an arc curved text path with tangential rotation", () => {
    const arc = new ArcTextPath(500, 500, 200, 0, 180); // Semicírculo
    const layout = TextLayoutEngine.calculateLayout(doc);

    const mapped = TextPathMapper.mapGlyphsToPath(layout.glyphs, arc);
    assert.strictEqual(mapped.length, 5);
    // Verificar que los glifos tienen rotaciones tangenciales progresivas
    assert.ok(mapped[1].rotation !== mapped[0].rotation);
  });
});
