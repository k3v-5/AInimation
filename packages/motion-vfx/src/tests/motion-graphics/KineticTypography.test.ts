import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { KineticTypographyEngine } from "../../motion-graphics/core/KineticTypographyEngine.js";

describe("Fase 11 — Kinetic Typography & Stagger Tests", () => {
  it("segments text into words and applies forward, reverse and center staggers", () => {
    const text = "ESTO CAMBIO TODO";

    // 1. Forward Stagger
    const forward = KineticTypographyEngine.segmentText(text, { direction: "forward", staggerDelay: 0.1 });
    assert.strictEqual(forward.length, 3);
    assert.strictEqual(forward[0].startDelay, 0.0);
    assert.strictEqual(Math.abs(forward[1].startDelay - 0.1) < 1e-6, true);
    assert.strictEqual(Math.abs(forward[2].startDelay - 0.2) < 1e-6, true);

    // 2. Reverse Stagger
    const reverse = KineticTypographyEngine.segmentText(text, { direction: "reverse", staggerDelay: 0.1 });
    assert.strictEqual(Math.abs(reverse[0].startDelay - 0.2) < 1e-6, true);
    assert.strictEqual(reverse[2].startDelay, 0.0);

    // 3. Center Stagger
    const center = KineticTypographyEngine.segmentText(text, { direction: "center", staggerDelay: 0.1 });
    assert.strictEqual(center[1].startDelay, 0.0); // Palabra central empieza primero
  });

  it("applies scale punch, custom color and glow to emphasized keywords", () => {
    const text = "Este ERROR es crítico";
    const segments = KineticTypographyEngine.segmentText(text, {
      emphasizedWords: ["ERROR"],
      highlightColor: "#ff0055",
    });

    const errorWord = segments[1];
    assert.strictEqual(errorWord.text, "ERROR");
    assert.strictEqual(errorWord.isEmphasized, true);
    assert.strictEqual(errorWord.scale, 1.25);
    assert.strictEqual(errorWord.color, "#ff0055");
    assert.strictEqual(errorWord.glow, true);

    const normalWord = segments[0];
    assert.strictEqual(normalWord.isEmphasized, false);
    assert.strictEqual(normalWord.scale, 1.0);
  });
});
