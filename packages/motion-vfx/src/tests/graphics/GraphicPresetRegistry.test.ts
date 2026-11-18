import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { GraphicPresetRegistry } from "../../graphics/presets/GraphicPresetRegistry.js";

describe("Fase 5J — Graphic Preset Registry Tests", () => {
  it("registers, lists and instantiates builtin semantic presets", () => {
    assert.strictEqual(GraphicPresetRegistry.has("modern-card"), true);
    assert.strictEqual(GraphicPresetRegistry.has("highlight-circle"), true);
    assert.strictEqual(GraphicPresetRegistry.has("warning-badge"), true);

    const cardPreset = GraphicPresetRegistry.get("modern-card");
    const elements = cardPreset.createElements({ width: 700, height: 300, radius: 16 });
    assert.strictEqual(elements.length, 1);
    assert.strictEqual(elements[0].geometry.type, "rounded-rectangle");
    assert.strictEqual((elements[0].geometry as any).width, 700);
  });
});
