import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { TextPresetRegistry } from "../../typography/presets/TextPresetRegistry.js";

describe("Fase 5F — Text Preset Registry Tests", () => {
  it("registers and lists builtin kinetic text presets (title-impact, neon-glow, gradient-punch)", () => {
    assert.strictEqual(TextPresetRegistry.has("title-impact"), true);
    assert.strictEqual(TextPresetRegistry.has("neon-glow"), true);
    assert.strictEqual(TextPresetRegistry.has("gradient-punch"), true);

    const titleImpact = TextPresetRegistry.get("title-impact");
    assert.strictEqual(titleImpact.style.fontWeight, 900);
    assert.strictEqual(titleImpact.paint.strokes?.length, 1);
    assert.strictEqual(titleImpact.stagger?.mode, "forward");
  });

  it("throws ValidationError on duplicate preset registration", () => {
    assert.throws(
      () =>
        TextPresetRegistry.register({
          id: "title-impact",
          name: "Dup Title",
          description: "dup",
          style: {} as any,
          paint: {} as any,
        }),
      /DUPLICATE_TEXT_PRESET/
    );
  });
});
