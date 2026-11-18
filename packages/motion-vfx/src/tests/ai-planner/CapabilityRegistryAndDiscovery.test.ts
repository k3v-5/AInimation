import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { CapabilityRegistry } from "../../ai-planner/core/CapabilityRegistry.js";

describe("Fase 7 — Capability Registry & AI Discovery Tests", () => {
  it("registers and lists builtin engine capabilities", () => {
    assert.strictEqual(CapabilityRegistry.has("graphics.callout"), true);
    assert.strictEqual(CapabilityRegistry.has("camera.push-in"), true);
    assert.strictEqual(CapabilityRegistry.has("caption.word-pop"), true);
    assert.strictEqual(CapabilityRegistry.has("audio.ducking"), true);

    const calloutCap = CapabilityRegistry.get("graphics.callout");
    assert.strictEqual(calloutCap?.category, "graphics");
    assert.strictEqual(typeof calloutCap?.parameters.text, "string");
  });
});
