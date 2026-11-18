import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { GaussianBlur } from "../../effects/blur/GaussianBlur.js";

describe("Fase 4C — Animated Effect Parameters Tests", () => {
  it("animates effect parameter (blur amount) smoothly across keyframes", () => {
    const blur = new GaussianBlur();

    // Keyframes: t=0 -> amount=0, t=0.5 -> amount=20, t=1.0 -> amount=0
    blur.amount.addKeyframe(0, 0);
    blur.amount.addKeyframe(0.5, 20);
    blur.amount.addKeyframe(1.0, 0);

    // Evaluar en t=0 -> amount = 0
    const at0 = blur.evaluate(0);
    assert.strictEqual(at0.params.amount, 0);

    // Evaluar en t=0.25 -> amount = 10
    const at025 = blur.evaluate(0.25);
    assert.strictEqual(at025.params.amount, 10);

    // Evaluar en t=0.5 -> amount = 20
    const at05 = blur.evaluate(0.5);
    assert.strictEqual(at05.params.amount, 20);

    // Evaluar en t=1.0 -> amount = 0
    const at1 = blur.evaluate(1.0);
    assert.strictEqual(at1.params.amount, 0);
  });
});
