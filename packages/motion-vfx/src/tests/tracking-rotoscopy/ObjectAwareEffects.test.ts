import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { ObjectAwareEffectRegistry } from "../../tracking-rotoscopy/core/ObjectAwareEffectRegistry.js";

describe("Fase 12 — Object Aware Effects Registry Tests", () => {
  it("lists and retrieves builtin object effects (background-blur, subject-pop, highlight-outline)", () => {
    const list = ObjectAwareEffectRegistry.list();
    assert.strictEqual(list.length >= 4, true);

    const bgBlur = ObjectAwareEffectRegistry.get("background-blur");
    assert.strictEqual(bgBlur !== undefined, true);
    assert.strictEqual(bgBlur?.parameters.blurRadius, 25);
    assert.strictEqual(bgBlur?.parameters.keepSubjectSharp, true);

    const subjectPop = ObjectAwareEffectRegistry.get("subject-pop");
    assert.strictEqual(subjectPop !== undefined, true);
    assert.strictEqual(subjectPop?.parameters.outlineColor, "#ffeb3b");
  });
});
