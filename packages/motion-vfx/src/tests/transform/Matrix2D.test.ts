import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Matrix2D } from "../../transform/Matrix2D.js";

describe("Fase 2A — Matrix2D Pure Mathematical Tests", () => {
  it("identity multiplication: identity * A = A and A * identity = A", () => {
    const id = Matrix2D.identity();
    const a = Matrix2D.multiply(Matrix2D.translation(50, 100), Matrix2D.scale(2, 3));

    const idA = Matrix2D.multiply(id, a);
    const aId = Matrix2D.multiply(a, id);

    assert.deepStrictEqual(idA, a);
    assert.deepStrictEqual(aId, a);
  });

  it("translation translates points accurately: translate(100, 50) on (0, 0) -> (100, 50)", () => {
    const t = Matrix2D.translation(100, 50);
    const p = Matrix2D.transformPoint(t, { x: 0, y: 0 });
    assert.strictEqual(p.x, 100);
    assert.strictEqual(p.y, 50);
  });

  it("scale scales points multiplicatively: scale(2, 3) on (10, 10) -> (20, 30)", () => {
    const s = Matrix2D.scale(2, 3);
    const p = Matrix2D.transformPoint(s, { x: 10, y: 10 });
    assert.strictEqual(p.x, 20);
    assert.strictEqual(p.y, 30);
  });

  it("rotation rotates points clockwise in degrees: rotate(90 deg) on (1, 0) -> (0, 1)", () => {
    const r90 = Matrix2D.rotation(90);
    const p = Matrix2D.transformPoint(r90, { x: 1, y: 0 });
    assert.ok(Math.abs(p.x - 0) < 1e-10, `Expected x ~ 0, got ${p.x}`);
    assert.ok(Math.abs(p.y - 1) < 1e-10, `Expected y ~ 1, got ${p.y}`);
  });

  it("matrix inversion: inverse(M) * M = identity for non-singular matrix", () => {
    const m = Matrix2D.multiply(
      Matrix2D.translation(123, 456),
      Matrix2D.multiply(Matrix2D.rotation(45), Matrix2D.scale(2, 0.5))
    );

    const inv = Matrix2D.inverse(m);
    const prod = Matrix2D.multiply(inv, m);

    assert.ok(Math.abs(prod.a - 1) < 1e-10);
    assert.ok(Math.abs(prod.b - 0) < 1e-10);
    assert.ok(Math.abs(prod.c - 0) < 1e-10);
    assert.ok(Math.abs(prod.d - 1) < 1e-10);
    assert.ok(Math.abs(prod.tx - 0) < 1e-10);
    assert.ok(Math.abs(prod.ty - 0) < 1e-10);
  });
});
