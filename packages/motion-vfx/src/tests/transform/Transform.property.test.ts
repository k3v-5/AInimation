import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import { Matrix2D } from "../../transform/Matrix2D.js";
import { TransformMath } from "../../transform/TransformMath.js";

describe("Fase 2A — Transform Property-Based Tests (fast-check)", () => {
  it("PBT: inverse(M) * M = identity for arbitrary random transforms", () => {
    fc.assert(
      fc.property(
        fc.double({ noNaN: true, noDefaultInfinity: true, min: -1000, max: 1000 }), // pos X
        fc.double({ noNaN: true, noDefaultInfinity: true, min: -1000, max: 1000 }), // pos Y
        fc.double({ noNaN: true, noDefaultInfinity: true, min: 0.1, max: 10 }), // scale X
        fc.double({ noNaN: true, noDefaultInfinity: true, min: 0.1, max: 10 }), // scale Y
        fc.double({ noNaN: true, noDefaultInfinity: true, min: -360, max: 360 }), // rotation
        fc.double({ noNaN: true, noDefaultInfinity: true, min: 0, max: 1 }), // anchor X
        fc.double({ noNaN: true, noDefaultInfinity: true, min: 0, max: 1 }), // anchor Y
        (px, py, sx, sy, rot, ax, ay) => {
          const m = TransformMath.composeFromBounds(
            { x: px, y: py },
            { x: sx, y: sy },
            rot,
            { x: ax, y: ay },
            { width: 100, height: 100 }
          );

          const inv = Matrix2D.inverse(m);
          const prod = Matrix2D.multiply(inv, m);

          // Verificar cercanía a la identidad
          assert.ok(Math.abs(prod.a - 1) < 1e-6, `prod.a expected ~ 1, got ${prod.a}`);
          assert.ok(Math.abs(prod.b - 0) < 1e-6, `prod.b expected ~ 0, got ${prod.b}`);
          assert.ok(Math.abs(prod.c - 0) < 1e-6, `prod.c expected ~ 0, got ${prod.c}`);
          assert.ok(Math.abs(prod.d - 1) < 1e-6, `prod.d expected ~ 1, got ${prod.d}`);
          assert.ok(Math.abs(prod.tx - 0) < 1e-4, `prod.tx expected ~ 0, got ${prod.tx}`);
          assert.ok(Math.abs(prod.ty - 0) < 1e-4, `prod.ty expected ~ 0, got ${prod.ty}`);
        }
      ),
      { numRuns: 1000 }
    );
  });
});
