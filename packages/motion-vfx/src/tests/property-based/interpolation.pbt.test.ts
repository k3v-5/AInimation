import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import { interpolate } from "../../animation/interpolation.js";

describe("Nivel 6 — Property-Based Tests: Mathematical Invariants (fast-check)", () => {
  it("PBT: interpolate(a, b, 0) === a and interpolate(a, b, 1) === b for all real numbers", () => {
    fc.assert(
      fc.property(
        fc.double({ noNaN: true, noDefaultInfinity: true, min: -1e6, max: 1e6 }),
        fc.double({ noNaN: true, noDefaultInfinity: true, min: -1e6, max: 1e6 }),
        (a, b) => {
          assert.strictEqual(interpolate(a, b, 0), a);
          assert.strictEqual(interpolate(a, b, 1), b);
        }
      ),
      { numRuns: 1000 }
    );
  });

  it("PBT: interpolate(a, b, p) clamps strictly for p < 0 and p > 1", () => {
    fc.assert(
      fc.property(
        fc.double({ noNaN: true, noDefaultInfinity: true, min: -1e6, max: 1e6 }),
        fc.double({ noNaN: true, noDefaultInfinity: true, min: -1e6, max: 1e6 }),
        fc.double({ noNaN: true, noDefaultInfinity: true, min: -1000, max: -0.0001 }),
        fc.double({ noNaN: true, noDefaultInfinity: true, min: 1.0001, max: 1000 }),
        (a, b, underProgress, overProgress) => {
          assert.strictEqual(interpolate(a, b, underProgress), a);
          assert.strictEqual(interpolate(a, b, overProgress), b);
        }
      ),
      { numRuns: 1000 }
    );
  });

  it("PBT: Vector2 interpolation boundary invariants for thousands of random vectors", () => {
    const vector2Arbitrary = fc
      .tuple(
        fc.double({ noNaN: true, noDefaultInfinity: true, min: -1e5, max: 1e5 }),
        fc.double({ noNaN: true, noDefaultInfinity: true, min: -1e5, max: 1e5 })
      )
      .map(([x, y]) => ({ x, y }));

    fc.assert(
      fc.property(vector2Arbitrary, vector2Arbitrary, (v1, v2) => {
        const at0 = interpolate(v1, v2, 0);
        const at1 = interpolate(v1, v2, 1);
        assert.strictEqual(at0.x, v1.x);
        assert.strictEqual(at0.y, v1.y);
        assert.strictEqual(at1.x, v2.x);
        assert.strictEqual(at1.y, v2.y);
      }),
      { numRuns: 1000 }
    );
  });

  it("PBT: Vector3 interpolation boundary invariants for thousands of random vectors", () => {
    const vector3Arbitrary = fc
      .tuple(
        fc.double({ noNaN: true, noDefaultInfinity: true, min: -1e5, max: 1e5 }),
        fc.double({ noNaN: true, noDefaultInfinity: true, min: -1e5, max: 1e5 }),
        fc.double({ noNaN: true, noDefaultInfinity: true, min: -1e5, max: 1e5 })
      )
      .map(([x, y, z]) => ({ x, y, z }));

    fc.assert(
      fc.property(vector3Arbitrary, vector3Arbitrary, (v1, v2) => {
        const at0 = interpolate(v1, v2, 0);
        const at1 = interpolate(v1, v2, 1);
        assert.strictEqual(at0.x, v1.x);
        assert.strictEqual(at0.y, v1.y);
        assert.strictEqual(at0.z, v1.z);
        assert.strictEqual(at1.x, v2.x);
        assert.strictEqual(at1.y, v2.y);
        assert.strictEqual(at1.z, v2.z);
      }),
      { numRuns: 1000 }
    );
  });
});
