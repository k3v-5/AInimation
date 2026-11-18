import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { CaptionEvaluator } from "../../captions/core/CaptionEvaluator.js";
import { Caption } from "../../captions/types/index.js";

describe("Fase 5E — Caption Evaluation & Karaoke Highlight Tests", () => {
  it("evaluates active word, progress and styling at specific timestamps", () => {
    const caption: Caption = {
      id: "cap_karaoke",
      timelineRange: { start: 0.0, end: 3.0 },
      words: [
        { id: "w_esto", text: "ESTO", start: 0.0, end: 1.0 },
        { id: "w_es", text: "ES", start: 1.0, end: 2.0 },
        { id: "w_top", text: "INCREIBLE", start: 2.0, end: 3.0 },
      ],
      style: {
        fontFamily: "Montserrat",
        fontSize: 64,
        fontWeight: 900,
        color: { r: 1, g: 1, b: 1 },
        alignment: "center",
      },
      layoutMode: "highlight",
      position: "bottom-center",
    };

    const activeOverride = {
      color: { r: 1, g: 1, b: 0 }, // Amarillo
      scale: 1.2,
    };

    // 1. En t = 0.5s -> 'ESTO' activo con progreso 0.5
    const stateAt05 = CaptionEvaluator.evaluate(caption, 0.5, undefined, activeOverride);
    assert.strictEqual(stateAt05.active, true);
    assert.strictEqual(stateAt05.activeWordId, "w_esto");

    const w0 = stateAt05.words.find((w) => w.id === "w_esto")!;
    assert.strictEqual(w0.active, true);
    assert.strictEqual(w0.progress, 0.5);
    assert.strictEqual(w0.style.color.r, 1);
    assert.strictEqual(w0.style.color.g, 1);
    assert.strictEqual(w0.style.color.b, 0); // Amarillo
    assert.strictEqual(w0.scale, 1.2);

    // 2. En t = 2.75s -> 'INCREIBLE' activo con progreso 0.75
    const stateAt275 = CaptionEvaluator.evaluate(caption, 2.75, undefined, activeOverride);
    assert.strictEqual(stateAt275.activeWordId, "w_top");
    const w2 = stateAt275.words.find((w) => w.id === "w_top")!;
    assert.strictEqual(w2.active, true);
    assert.strictEqual(w2.progress, 0.75);

    // 3. En t = 3.5s -> inactivo fuera de rango
    const stateAt35 = CaptionEvaluator.evaluate(caption, 3.5);
    assert.strictEqual(stateAt35.active, false);
    assert.strictEqual(stateAt35.words.length, 0);
  });
});
