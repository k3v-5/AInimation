import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { overshoot } from "../../../animation/motion/OvershootMotion.js";

describe("Fase 3C — Overshoot / Back Motion Tests", () => {
  it("satisfies boundary conditions: evaluate(0) = 0 and evaluate(1) = 1", () => {
    const o = overshoot({ amount: 1.0 });
    assert.strictEqual(o.evaluate(0), 0);
    assert.strictEqual(o.evaluate(1), 1);
    assert.strictEqual(o.evaluate(-0.5), 0);
    assert.strictEqual(o.evaluate(1.5), 1);
  });

  it("exceeds 1.0 at peak (overshoots) when amount > 0", () => {
    const o = overshoot({ amount: 1.0 });

    // En p = 0.7 - 0.8, el valor debe ser mayor a 1.0 (overshoot peak)
    let maxVal = 0;
    for (let p = 0; p <= 1.0; p += 0.05) {
      const val = o.evaluate(p);
      if (val > maxVal) {
        maxVal = val;
      }
    }

    assert.ok(maxVal > 1.05, `Expected max overshoot peak > 1.05, got ${maxVal}`);
  });

  it("amount = 0 behaves like standard easeOut without overshoot", () => {
    const o = overshoot({ amount: 0 });
    for (let p = 0; p <= 1.0; p += 0.1) {
      const val = o.evaluate(p);
      assert.ok(val <= 1.0000001, `Value ${val} should not exceed 1.0 when amount=0`);
    }
  });
});
