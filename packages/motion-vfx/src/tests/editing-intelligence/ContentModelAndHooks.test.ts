import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { ContentModelBuilder } from "../../editing-intelligence/core/ContentModelBuilder.js";

describe("Fase 14 — Content Model & Hook Detection Tests", () => {
  it("enriches transcript segments with word timings and importance scoring", () => {
    const raw = [
      { start: 0, end: 2.0, text: "Hola bueno este video es un ejemplo" },
      { start: 2.0, end: 5.0, text: "El error más grande que cometes al editar" },
    ];

    const model = ContentModelBuilder.buildContentModel(raw, "Video Editing");
    assert.strictEqual(model.segments.length, 2);

    // Segmento 0 es filler/intro -> importancia baja
    assert.strictEqual(model.segments[0].importance <= 0.5, true);

    // Segmento 1 contiene 'error' -> importancia alta
    assert.strictEqual(model.segments[1].importance >= 0.9, true);
    assert.strictEqual(model.segments[1].words.length, 8);
  });

  it("detects and ranks high-converting hook candidates", () => {
    const raw = [
      { start: 0, end: 3.0, text: "¿Sabías que la IA puede editar por ti?" },
      { start: 3.0, end: 6.0, text: "No cometas este error crítico." },
    ];

    const model = ContentModelBuilder.buildContentModel(raw, "AI Video");
    assert.strictEqual(model.hooks.length >= 2, true);
    assert.strictEqual(model.hooks[0].score >= 0.9, true);
    assert.ok(model.hooks.some((h) => h.type === "question" || h.type === "curiosity"));
  });
});
