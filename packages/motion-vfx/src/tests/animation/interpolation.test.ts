import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { clamp01, cloneValue, interpolate } from "../../animation/interpolation.js";
import { ValidationError } from "../../errors/index.js";

describe("Interpolation & Clamping", () => {
  it("clamp01 clamps values below 0 and above 1", () => {
    assert.strictEqual(clamp01(-0.5), 0);
    assert.strictEqual(clamp01(0), 0);
    assert.strictEqual(clamp01(0.5), 0.5);
    assert.strictEqual(clamp01(1), 1);
    assert.strictEqual(clamp01(1.5), 1);
    assert.strictEqual(clamp01(NaN), 0);
  });

  it("cloneValue performs deep copy", () => {
    const original = { pos: { x: 10, y: 20 }, arr: [1, 2, 3] };
    const copy = cloneValue(original);
    assert.deepStrictEqual(copy, original);
    copy.pos.x = 999;
    assert.strictEqual(original.pos.x, 10);
  });

  it("interpolates scalar numbers", () => {
    assert.strictEqual(interpolate(0, 100, 0), 0);
    assert.strictEqual(interpolate(0, 100, 0.5), 50);
    assert.strictEqual(interpolate(0, 100, 1), 100);
    // Clamping behavior
    assert.strictEqual(interpolate(0, 100, -0.2), 0);
    assert.strictEqual(interpolate(0, 100, 1.2), 100);
  });

  it("interpolates Vector2", () => {
    const from = { x: 0, y: 100 };
    const to = { x: 200, y: 300 };
    assert.deepStrictEqual(interpolate(from, to, 0), { x: 0, y: 100 });
    assert.deepStrictEqual(interpolate(from, to, 0.5), { x: 100, y: 200 });
    assert.deepStrictEqual(interpolate(from, to, 1), { x: 200, y: 300 });
  });

  it("interpolates Vector3", () => {
    const from = { x: 0, y: 0, z: 0 };
    const to = { x: 10, y: 20, z: 30 };
    assert.deepStrictEqual(interpolate(from, to, 0.5), { x: 5, y: 10, z: 15 });
  });

  it("interpolates Color RGBA", () => {
    const black = { r: 0, g: 0, b: 0, a: 1 };
    const white = { r: 1, g: 1, b: 1, a: 1 };
    const gray = interpolate(black, white, 0.5);
    assert.deepStrictEqual(gray, { r: 0.5, g: 0.5, b: 0.5, a: 1 });
  });

  it("throws ValidationError when interpolating incompatible types", () => {
    assert.throws(() => {
      // @ts-expect-error test invalid types
      interpolate(100, { x: 10, y: 20 }, 0.5);
    }, ValidationError);
  });
});
