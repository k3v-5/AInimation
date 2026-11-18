import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { easeIn, easeInOut, easeOut, getEasing, linear } from "../../animation/easing.js";

describe("Easing Functions", () => {
  const easings = [
    { name: "linear", fn: linear },
    { name: "easeIn", fn: easeIn },
    { name: "easeOut", fn: easeOut },
    { name: "easeInOut", fn: easeInOut },
  ];

  for (const { name, fn } of easings) {
    it(`${name} maps 0 to exact 0 and 1 to exact 1 without float jitter`, () => {
      assert.strictEqual(fn(0), 0);
      assert.strictEqual(fn(1), 1);
      // Strict clamping for out-of-range inputs
      assert.strictEqual(fn(-0.5), 0);
      assert.strictEqual(fn(-100), 0);
      assert.strictEqual(fn(1.5), 1);
      assert.strictEqual(fn(100), 1);
    });

    it(`${name} stays strictly bounded within [0, 1] for t in [0, 1]`, () => {
      for (let t = 0; t <= 1; t += 0.05) {
        const val = fn(t);
        assert.ok(val >= -1e-10 && val <= 1 + 1e-10, `${name}(${t}) = ${val} out of bounds`);
      }
    });

    it(`${name} is monotonically increasing`, () => {
      let prev = -1;
      for (let t = 0; t <= 1; t += 0.02) {
        const current = fn(t);
        assert.ok(current >= prev - 1e-10, `${name} violated monotonicity at t=${t}`);
        prev = current;
      }
    });
  }

  it("easeIn starts slower than linear", () => {
    assert.ok(easeIn(0.5) < linear(0.5));
    assert.strictEqual(easeIn(0.5), 0.125);
  });

  it("easeOut starts faster than linear", () => {
    assert.ok(easeOut(0.5) > linear(0.5));
    assert.strictEqual(easeOut(0.5), 0.875);
  });

  it("easeInOut is symmetric around t=0.5", () => {
    assert.strictEqual(easeInOut(0.5), 0.5);
    assert.strictEqual(easeInOut(0.25), 4 * Math.pow(0.25, 3)); // 0.0625
    assert.strictEqual(easeInOut(0.75), 1 - Math.pow(-2 * 0.75 + 2, 3) / 2); // 0.9375
  });

  it("getEasing returns appropriate function or defaults to linear", () => {
    assert.strictEqual(getEasing("easeIn"), easeIn);
    assert.strictEqual(getEasing("easeOut"), easeOut);
    assert.strictEqual(getEasing("easeInOut"), easeInOut);
    assert.strictEqual(getEasing("linear"), linear);
    assert.strictEqual(getEasing(undefined), linear);
    // @ts-expect-error test invalid string
    assert.strictEqual(getEasing("unknown"), linear);
  });
});
