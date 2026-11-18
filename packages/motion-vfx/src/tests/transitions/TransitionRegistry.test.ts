import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { registerBuiltinTransitions } from "../../transitions/builtins/index.js";
import { TransitionRegistry } from "../../transitions/core/TransitionRegistry.js";

describe("Fase 5C — Transition Registry & Parameter Schema Tests", () => {
  registerBuiltinTransitions();

  it("registers and discovers all standard builtin transitions", () => {
    assert.strictEqual(TransitionRegistry.has("cut"), true);
    assert.strictEqual(TransitionRegistry.has("crossfade"), true);
    assert.strictEqual(TransitionRegistry.has("dipToColor"), true);
    assert.strictEqual(TransitionRegistry.has("zoom"), true);
    assert.strictEqual(TransitionRegistry.has("slide"), true);
    assert.strictEqual(TransitionRegistry.has("whip"), true);
    assert.strictEqual(TransitionRegistry.has("blur"), true);
    assert.strictEqual(TransitionRegistry.has("flash"), true);

    const list = TransitionRegistry.list();
    assert.ok(list.length >= 8);
  });

  it("throws ValidationError on duplicate transition type registration", () => {
    assert.throws(
      () =>
        TransitionRegistry.register({
          type: "crossfade",
          name: "Duplicate Crossfade",
          description: "dup",
          parameters: [],
          evaluate: () => ({} as any),
        }),
      /DUPLICATE_TRANSITION/
    );
  });

  it("validates transition parameters against schema bounds", () => {
    assert.throws(
      () =>
        TransitionRegistry.evaluate("zoom", 0.5, 0.25, 0.5, {
          amount: 5.0, // max is 2.0
        }),
      /exceeds maximum/
    );

    assert.throws(
      () =>
        TransitionRegistry.evaluate("slide", 0.5, 0.25, 0.5, {
          direction: "diagonal", // valid: left, right, up, down
        }),
      /must be one of/
    );
  });
});
