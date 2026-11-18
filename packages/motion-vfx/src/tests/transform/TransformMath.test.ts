import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Matrix2D } from "../../transform/Matrix2D.js";
import { TransformMath } from "../../transform/TransformMath.js";

describe("Fase 2A — TransformMath & Anchor Point Order Tests", () => {
  it("element 100x100 with center anchor (0.5, 0.5) rotated 90 deg keeps its center at position (500, 500)", () => {
    const position = { x: 500, y: 500 };
    const bounds = { width: 100, height: 100 };
    const anchorCenter = { x: 0.5, y: 0.5 };

    const m = TransformMath.composeFromBounds(position, { x: 1, y: 1 }, 90, anchorCenter, bounds);

    // El centro geométrico local (50, 50) debe proyectarse exactamente a (500, 500)
    const centerWorld = Matrix2D.transformPoint(m, { x: 50, y: 50 });
    assert.ok(Math.abs(centerWorld.x - 500) < 1e-10);
    assert.ok(Math.abs(centerWorld.y - 500) < 1e-10);
  });

  it("element 100x100 with top-left anchor (0, 0) rotated 90 deg rotates around (500, 500)", () => {
    const position = { x: 500, y: 500 };
    const bounds = { width: 100, height: 100 };
    const anchorTopLeft = { x: 0, y: 0 };

    const m = TransformMath.composeFromBounds(position, { x: 1, y: 1 }, 90, anchorTopLeft, bounds);

    // La esquina top-left local (0, 0) se mantiene en (500, 500)
    const topLeftWorld = Matrix2D.transformPoint(m, { x: 0, y: 0 });
    assert.ok(Math.abs(topLeftWorld.x - 500) < 1e-10);
    assert.ok(Math.abs(topLeftWorld.y - 500) < 1e-10);

    // La esquina top-right local (100, 0) rotada 90 deg se proyecta a (500, 600)
    const topRightWorld = Matrix2D.transformPoint(m, { x: 100, y: 0 });
    assert.ok(Math.abs(topRightWorld.x - 500) < 1e-10);
    assert.ok(Math.abs(topRightWorld.y - 600) < 1e-10);
  });

  it("applies scale and rotation combined without drift", () => {
    const m = TransformMath.composeFromBounds(
      { x: 200, y: 300 },
      { x: 2, y: 2 },
      180,
      { x: 0.5, y: 0.5 },
      { width: 50, height: 50 }
    );

    // Centro (25, 25) permanece en (200, 300)
    const center = Matrix2D.transformPoint(m, { x: 25, y: 25 });
    assert.ok(Math.abs(center.x - 200) < 1e-10);
    assert.ok(Math.abs(center.y - 300) < 1e-10);
  });
});
