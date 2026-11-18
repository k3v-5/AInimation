import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { GaussianBlur } from "../../effects/blur/GaussianBlur.js";
import { Brightness } from "../../effects/color/Brightness.js";
import { EffectRegistry } from "../../effects/core/EffectRegistry.js";
import { EffectStack } from "../../effects/core/EffectStack.js";
import { Glow } from "../../effects/glow/Glow.js";
import { registerBuiltinEffects } from "../../effects/builtins/index.js";

describe("Fase 4C — Effect Stack Serialization & Deserialization Tests", () => {
  registerBuiltinEffects();

  it("serializes and deserializes full EffectStack retaining parameter states", () => {
    const originalStack = new EffectStack();
    originalStack
      .add(new GaussianBlur({ id: "fx_blur", amount: 25 }))
      .add(new Brightness({ id: "fx_bright", amount: 1.4 }))
      .add(new Glow({ id: "fx_glow", radius: 40, intensity: 2.0 }));

    const serialized = originalStack.toJSON();
    assert.strictEqual(serialized.length, 3);

    // Reconstruir
    const reconstructedStack = new EffectStack();
    for (const fxData of serialized) {
      const fx = EffectRegistry.fromJSON(fxData);
      reconstructedStack.add(fx);
    }

    assert.strictEqual(reconstructedStack.length, 3);
    const evOriginal = originalStack.evaluate(0);
    const evReconstructed = reconstructedStack.evaluate(0);

    assert.deepStrictEqual(evReconstructed, evOriginal);
  });
});
