import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { GeometryFactory } from "../../graphics/geometry/GeometryFactory.js";
import { ArrowGeometry, RoundedRectangleGeometry } from "../../graphics/types/index.js";

describe("Fase 5J — Geometry & 2D Shapes Tests", () => {
  it("calculates 7-vertex arrow polygon accurately from start to end points", () => {
    const arrow: ArrowGeometry = {
      type: "arrow",
      start: { x: 0, y: 0 },
      end: { x: 100, y: 0 },
      headLength: 20,
      headWidth: 30,
      shaftWidth: 10,
    };

    const poly = GeometryFactory.createArrowPolygon(arrow);
    assert.strictEqual(poly.length, 7);
    // La punta debe coincidir con end (100, 0)
    assert.strictEqual(poly[3].x, 100);
    assert.strictEqual(poly[3].y, 0);

    const bounds = GeometryFactory.calculateBounds(arrow);
    assert.strictEqual(bounds.width, 100);
    assert.strictEqual(bounds.height, 30);
  });

  it("sanitizes rounded rectangle radius to not exceed half of minimum dimension", () => {
    const rect: RoundedRectangleGeometry = {
      type: "rounded-rectangle",
      width: 100,
      height: 40,
      radius: 50, // Excede 40/2 = 20
    };

    const sanitized = GeometryFactory.sanitizeRoundedRectangle(rect);
    assert.strictEqual(sanitized.radius, 20);
  });
});
