import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { SemanticSFXLibrary } from "../../audio-design/core/SemanticSFXLibrary.js";

describe("Fase 13 — Semantic SFX Library Tests", () => {
  it("finds appropriate SFX by intent, category and energy", () => {
    // 1. Buscar por intent 'punch' -> impact
    const punchSFX = SemanticSFXLibrary.findSFX({ intent: "punch" });
    assert.strictEqual(punchSFX !== undefined, true);
    assert.strictEqual(punchSFX?.category, "impact");

    // 2. Buscar por categoría 'whoosh'
    const whooshSFX = SemanticSFXLibrary.findSFX({ category: "whoosh" });
    assert.strictEqual(whooshSFX !== undefined, true);
    assert.strictEqual(whooshSFX?.category, "whoosh");

    // 3. Buscar por energía 'high'
    const highEnergy = SemanticSFXLibrary.findSFX({ energy: "high" });
    assert.strictEqual(highEnergy !== undefined, true);
    assert.strictEqual(highEnergy?.energy, "high");
  });
});
