import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { PresetRegistry } from "../../presets/core/registry.js";
import { PresetResolver } from "../../presets/core/resolver.js";

describe("Fase 4A — Circular Preset Dependency Detection Tests", () => {
  it("detects recursive cyclic preset dependencies and throws ValidationError", () => {
    // Definir preset A que llama a B
    PresetRegistry.register({
      id: "presetA",
      name: "Preset A",
      category: "utility",
      version: 1,
      description: "Test preset A",
      tags: [],
      parameters: [],
      build(context) {
        return PresetResolver.resolve("presetB", context.target, {}, ["presetA"]);
      },
    });

    // Definir preset B que llama a A
    PresetRegistry.register({
      id: "presetB",
      name: "Preset B",
      category: "utility",
      version: 1,
      description: "Test preset B",
      tags: [],
      parameters: [],
      build(context) {
        return PresetResolver.resolve("presetA", context.target, {}, ["presetA", "presetB"]);
      },
    });

    assert.throws(
      () => PresetResolver.resolve("presetA", { id: "test_node" }),
      /CIRCULAR_PRESET_DEPENDENCY/
    );
  });
});
