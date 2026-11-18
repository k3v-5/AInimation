import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { registerBuiltinTransitions } from "../../transitions/builtins/index.js";
import { TransitionRegistry } from "../../transitions/core/TransitionRegistry.js";

describe("Fase 5C — Builtin Transitions Evaluation Tests", () => {
  registerBuiltinTransitions();

  it("evaluates Cut transition instantaneously", () => {
    const before = TransitionRegistry.evaluate("cut", 0.5, 0.25, 0.5, {}, "linear");
    assert.strictEqual(before.fromOpacity, 1);
    assert.strictEqual(before.toOpacity, 0);

    const end = TransitionRegistry.evaluate("cut", 1.0, 0.5, 0.5, {}, "linear");
    assert.strictEqual(end.fromOpacity, 0);
    assert.strictEqual(end.toOpacity, 1);
  });

  it("evaluates Crossfade smoothly across progress", () => {
    const at0 = TransitionRegistry.evaluate("crossfade", 0.0, 0, 1.0, {}, "linear");
    assert.strictEqual(at0.fromOpacity, 1);
    assert.strictEqual(at0.toOpacity, 0);

    const at50 = TransitionRegistry.evaluate("crossfade", 0.5, 0.5, 1.0, {}, "linear");
    assert.strictEqual(at50.fromOpacity, 0.5);
    assert.strictEqual(at50.toOpacity, 0.5);

    const at100 = TransitionRegistry.evaluate("crossfade", 1.0, 1.0, 1.0, {}, "linear");
    assert.strictEqual(at100.fromOpacity, 0);
    assert.strictEqual(at100.toOpacity, 1);
  });

  it("evaluates Zoom transition with scaling and midpoint blur", () => {
    const atMid = TransitionRegistry.evaluate("zoom", 0.5, 0.25, 0.5, { amount: 0.4, blur: 20 }, "linear");
    assert.ok((atMid.fromTransform?.scale ?? 0) > 1.0);
    assert.ok((atMid.toTransform?.scale ?? 0) < 1.0);
    assert.ok((atMid.fromBlur ?? 0) > 15); // blur peaks at progress = 0.5
  });

  it("evaluates Flash transition with white flash overlay peaking at midpoint", () => {
    const atMid = TransitionRegistry.evaluate("flash", 0.5, 0.25, 0.5, {}, "linear");
    assert.strictEqual(atMid.colorOverlay?.color.r, 1);
    assert.ok(Math.abs((atMid.colorOverlay?.opacity ?? 0) - 1.0) < 1e-5);
  });

  it("evaluates Slide and Whip transitions with coordinate translations", () => {
    const slide = TransitionRegistry.evaluate("slide", 0.5, 0.25, 0.5, { direction: "left", distance: 1000 }, "linear");
    assert.strictEqual(slide.fromTransform?.translateX, -500);
    assert.strictEqual(slide.toTransform?.translateX, 500);
  });
});
