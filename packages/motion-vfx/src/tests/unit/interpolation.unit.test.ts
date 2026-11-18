import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { clamp01, cloneValue, interpolate } from "../../animation/interpolation.js";
import { Color, Vector2, Vector3 } from "../../core/types.js";
import { ValidationError } from "../../errors/index.js";

describe("Nivel 1 — Unit Tests: Interpolation & Non-Mutation", () => {
  it("interpolates numbers correctly in standard and reverse directions", () => {
    assert.strictEqual(interpolate(0, 100, 0), 0);
    assert.strictEqual(interpolate(0, 100, 0.5), 50);
    assert.strictEqual(interpolate(0, 100, 1), 100);
    assert.strictEqual(interpolate(100, 0, 0.5), 50);
    assert.strictEqual(interpolate(-100, 100, 0.5), 0);
  });

  it("strictly clamps progress outside [0, 1]", () => {
    assert.strictEqual(interpolate(0, 100, -1), 0);
    assert.strictEqual(interpolate(0, 100, -0.0001), 0);
    assert.strictEqual(interpolate(0, 100, 1.0001), 100);
    assert.strictEqual(interpolate(0, 100, 2), 100);
    assert.strictEqual(interpolate(0, 100, 1000), 100);
  });

  it("interpolates Vector2 correctly", () => {
    const v1: Vector2 = { x: 0, y: 0 };
    const v2: Vector2 = { x: 100, y: 200 };

    assert.deepStrictEqual(interpolate(v1, v2, 0), { x: 0, y: 0 });
    assert.deepStrictEqual(interpolate(v1, v2, 0.5), { x: 50, y: 100 });
    assert.deepStrictEqual(interpolate(v1, v2, 1), { x: 100, y: 200 });
  });

  it("interpolates Vector3 correctly", () => {
    const v1: Vector3 = { x: 0, y: 0, z: 0 };
    const v2: Vector3 = { x: 100, y: 200, z: 300 };

    assert.deepStrictEqual(interpolate(v1, v2, 0), { x: 0, y: 0, z: 0 });
    assert.deepStrictEqual(interpolate(v1, v2, 0.5), { x: 50, y: 100, z: 150 });
    assert.deepStrictEqual(interpolate(v1, v2, 1), { x: 100, y: 200, z: 300 });
  });

  it("interpolates Color RGBA correctly", () => {
    const red: Color = { r: 1, g: 0, b: 0, a: 1 };
    const blue: Color = { r: 0, g: 0, b: 1, a: 0.5 };

    const mid = interpolate(red, blue, 0.5);
    assert.deepStrictEqual(mid, { r: 0.5, g: 0, b: 0.5, a: 0.75 });
  });

  it("GUARANTEES NON-MUTATION of input objects", () => {
    const a: Vector2 = { x: 0, y: 0 };
    const b: Vector2 = { x: 100, y: 100 };

    const result = interpolate(a, b, 0.5);

    // Inputs must remain totally intact
    assert.deepStrictEqual(a, { x: 0, y: 0 });
    assert.deepStrictEqual(b, { x: 100, y: 100 });

    // Modifying result must not mutate a or b
    result.x = 999;
    assert.strictEqual(a.x, 0);
    assert.strictEqual(b.x, 100);
  });

  it("throws ValidationError on incompatible types", () => {
    assert.throws(() => {
      // @ts-expect-error test invalid types
      interpolate({ x: 10, y: 20 }, 100, 0.5);
    }, ValidationError);
  });
});
