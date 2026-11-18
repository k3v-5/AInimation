import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { popInPreset } from "../../presets/builtins/popIn.js";
import { PresetRegistry } from "../../presets/core/registry.js";
import { registerBuiltinPresets } from "../../presets/builtins/index.js";

describe("Fase 4A — Preset Registry & Discovery Tests", () => {
  it("initializes and lists builtin popIn preset", () => {
    registerBuiltinPresets();
    assert.strictEqual(PresetRegistry.has("popIn"), true);

    const pop = PresetRegistry.get("popIn");
    assert.strictEqual(pop.id, "popIn");
    assert.strictEqual(pop.category, "entrance");
    assert.ok(pop.tags.includes("smooth"));
  });

  it("throws ValidationError on duplicate preset registration", () => {
    assert.throws(
      () => PresetRegistry.register(popInPreset),
      /DUPLICATE_PRESET_ID/
    );
  });

  it("searches presets by category, tags and element compatibility", () => {
    const entranceResults = PresetRegistry.search({ category: "entrance" });
    assert.ok(entranceResults.some((p) => p.id === "popIn"));

    const textResults = PresetRegistry.search({ compatibleWith: "text" });
    assert.ok(textResults.some((p) => p.id === "popIn"));

    const tagResults = PresetRegistry.search({ tags: ["modern", "pop"] });
    assert.ok(tagResults.some((p) => p.id === "popIn"));

    const nonExistentCategory = PresetRegistry.search({ category: "camera" });
    assert.strictEqual(nonExistentCategory.length, 0);
  });
});
