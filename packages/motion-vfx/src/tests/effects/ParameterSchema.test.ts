import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { EffectRegistry } from "../../effects/core/EffectRegistry.js";
import { registerBuiltinEffects } from "../../effects/builtins/index.js";

describe("Fase 4C — Effect Parameter Schema & Validation Tests", () => {
  registerBuiltinEffects();

  it("throws ValidationError when unknown parameter is supplied", () => {
    assert.throws(
      () => EffectRegistry.create("blur", { banana: 100 }),
      /UNKNOWN_EFFECT_PARAMETER/
    );
  });

  it("throws ValidationError when parameter exceeds bounds", () => {
    assert.throws(
      () => EffectRegistry.create("brightness", { amount: 10.0 }), // max is 5.0
      /PARAMETER_OUT_OF_RANGE/
    );
  });

  it("throws ValidationError when enum parameter has invalid value", () => {
    assert.throws(
      () => EffectRegistry.create("blur", { quality: "ultra-hd" }), // valid: low, medium, high
      /INVALID_ENUM_VALUE/
    );
  });
});
