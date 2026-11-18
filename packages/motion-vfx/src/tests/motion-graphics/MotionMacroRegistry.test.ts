import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { MotionMacroRegistry } from "../../motion-graphics/core/MotionMacroRegistry.js";

describe("Fase 11 — Motion Macro Registry Tests", () => {
  it("lists and resolves builtin motion macros (high-impact-hook, statistic-pop, subscribe-cta)", () => {
    const macros = MotionMacroRegistry.list();
    assert.strictEqual(macros.length >= 3, true);

    const hookMacro = MotionMacroRegistry.get("high-impact-hook");
    assert.strictEqual(hookMacro !== undefined, true);
    assert.strictEqual(hookMacro?.elements.some((e) => e.type === "text"), true);
    assert.strictEqual(hookMacro?.elements.some((e) => e.type === "camera"), true);
    assert.strictEqual(hookMacro?.elements.some((e) => e.type === "sfx"), true);
  });
});
