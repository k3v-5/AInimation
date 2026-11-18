import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { EffectRegistry } from "../../effects/core/EffectRegistry.js";
import { registerBuiltinEffects } from "../../effects/builtins/index.js";

describe("Fase 4C — Effect Registry & Builtin Discovery Tests", () => {
  registerBuiltinEffects();

  it("registers and lists all standard builtin effects", () => {
    assert.strictEqual(EffectRegistry.has("blur"), true);
    assert.strictEqual(EffectRegistry.has("brightness"), true);
    assert.strictEqual(EffectRegistry.has("contrast"), true);
    assert.strictEqual(EffectRegistry.has("glow"), true);
    assert.strictEqual(EffectRegistry.has("dropShadow"), true);
    assert.strictEqual(EffectRegistry.has("outline"), true);

    const list = EffectRegistry.list();
    assert.ok(list.length >= 6);
  });

  it("throws ValidationError on duplicate effect type registration", () => {
    assert.throws(
      () =>
        EffectRegistry.register({
          type: "blur",
          name: "Duplicate Blur",
          category: "blur",
          description: "duplicate",
          parameters: [],
          factory: () => null as any,
        }),
      /DUPLICATE_EFFECT_TYPE/
    );
  });
});
