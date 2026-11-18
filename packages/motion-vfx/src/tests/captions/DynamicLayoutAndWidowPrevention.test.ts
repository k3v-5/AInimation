import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { DynamicCaptionLayoutEngine } from "../../captions/layout/DynamicCaptionLayoutEngine.js";
import { CaptionStyle, CaptionWord } from "../../captions/types/index.js";

describe("Fase 16 — Dynamic Layout & Widow Prevention Tests", () => {
  const baseStyle: CaptionStyle = {
    fontFamily: "Montserrat",
    fontSize: 60,
    fontWeight: 800,
    color: { r: 1, g: 1, b: 1, a: 1 },
    alignment: "center",
  };

  it("prevents orphan words by rebalancing words across the last two lines", () => {
    // 4 palabras donde las 3 primeras ocuparían la línea 1 y la 4ta quedaría sola en línea 2
    const words: CaptionWord[] = [
      { id: "w1", text: "Aprende", start: 0, end: 0.5, index: 0 },
      { id: "w2", text: "edición", start: 0.5, end: 1.0, index: 1 },
      { id: "w3", text: "con", start: 1.0, end: 1.3, index: 2 },
      { id: "w4", text: "inteligencia", start: 1.3, end: 2.0, index: 3 },
    ];

    // Con ancho suficiente para 3 palabras pero no 4
    const layout = DynamicCaptionLayoutEngine.layout(words, baseStyle, {
      maxWidth: 750,
      preventWidows: true,
    });

    assert.equal(layout.lines.length, 2);
    // Sin prevención, línea 1 tendría 3 palabras y línea 2 tendría 1 palabra ("inteligencia").
    // Con prevención de huérfanas, ambas líneas deben tener 2 palabras:
    assert.equal(layout.lines[0].words.length, 2);
    assert.equal(layout.lines[1].words.length, 2);
    assert.equal(layout.lines[0].text, "Aprende edición");
    assert.equal(layout.lines[1].text, "con inteligencia");
    assert.ok(layout.diagnostics.includes("widow-prevented-rebalanced-lines"));
  });

  it("handles single-word captions properly centered without errors", () => {
    const words: CaptionWord[] = [
      { id: "w1", text: "¡BOOM!", start: 0, end: 0.5, index: 0 },
    ];

    const layout = DynamicCaptionLayoutEngine.layout(words, baseStyle, { maxWidth: 800 });
    assert.equal(layout.lines.length, 1);
    assert.equal(layout.words.length, 1);
    assert.equal(layout.overflowStatus, "none");
    assert.ok(layout.width > 0);
  });

  it("detects max-lines-exceeded overflow status when text is too long", () => {
    const longWords: CaptionWord[] = [
      "Esta", "es", "una", "frase", "extremadamente", "larga", "que", "debería", "ocupar",
      "muchas", "líneas", "y", "desbordar", "el", "máximo", "permitido",
    ].map((txt, idx) => ({
      id: `w_${idx}`,
      text: txt,
      start: idx * 0.2,
      end: (idx + 1) * 0.2,
      index: idx,
    }));

    const layout = DynamicCaptionLayoutEngine.layout(longWords, baseStyle, {
      maxWidth: 350,
      maxLines: 2,
    });

    assert.equal(layout.overflowStatus, "lines-exceeded");
    assert.ok(layout.diagnostics.some((d) => d.includes("max-lines-exceeded")));
  });

  it("aligns words correctly according to center, left and right text alignments", () => {
    const words: CaptionWord[] = [{ id: "w1", text: "Test", start: 0, end: 1, index: 0 }];

    const centerLayout = DynamicCaptionLayoutEngine.layout(words, { ...baseStyle, alignment: "center" });
    const leftLayout = DynamicCaptionLayoutEngine.layout(words, { ...baseStyle, alignment: "left" });
    const rightLayout = DynamicCaptionLayoutEngine.layout(words, { ...baseStyle, alignment: "right" });

    assert.ok(centerLayout.lines[0].x < 0); // centrado alrededor del eje 0
    assert.equal(leftLayout.lines[0].x, 0); // comienza en 0
    assert.ok(rightLayout.lines[0].x < 0); // alineado a la derecha del eje 0
  });
});
