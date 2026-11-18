import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { PresetResolver } from "../../presets/core/resolver.js";
import { registerBuiltinPresets } from "../../presets/builtins/index.js";

describe("Fase 4A — Preset Parameter Schema & Validation Tests", () => {
  registerBuiltinPresets();
  const target = { id: "test_title", type: "text" as const };

  it("throws ValidationError when unknown parameter is passed in overrides", () => {
    assert.throws(
      () => PresetResolver.resolve("popIn", target, { banana: 10 }),
      /UNKNOWN_PRESET_PARAMETER/
    );
  });

  it("throws ValidationError when parameter exceeds maximum limit", () => {
    assert.throws(
      () => PresetResolver.resolve("popIn", target, { intensity: 5.0 }),
      /PARAMETER_OUT_OF_RANGE/
    );
  });

  it("throws ValidationError when parameter has wrong type", () => {
    assert.throws(
      () => PresetResolver.resolve("popIn", target, { duration: "slow" as any }),
      /INVALID_PARAMETER_TYPE/
    );
  });
});
