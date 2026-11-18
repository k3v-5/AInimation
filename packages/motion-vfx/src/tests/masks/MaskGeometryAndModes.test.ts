import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { MaskPathGeometry } from "../../masks/core/MaskPathGeometry.js";
import { MatteGenerator } from "../../masks/core/MatteGenerator.js";

describe("Fase 5G — Mask Geometry, SDF & Boolean Modes Tests", () => {
  it("creates rectangle and ellipse paths and checks point inclusion", () => {
    const rectPath = MaskPathGeometry.createRectanglePath(100, 100, 200, 100);
    const polygon = rectPath.points.map((p) => p.position);

    // Punto dentro (150, 150)
    assert.strictEqual(MaskPathGeometry.isPointInsidePolygon({ x: 150, y: 150 }, polygon), true);
    // Punto fuera (50, 50)
    assert.strictEqual(MaskPathGeometry.isPointInsidePolygon({ x: 50, y: 50 }, polygon), false);

    // SDF dentro debe ser negativo
    const distInside = MaskPathGeometry.signedDistanceToPolygon({ x: 150, y: 150 }, polygon);
    assert.ok(distInside < 0);

    // SDF fuera debe ser positivo
    const distOutside = MaskPathGeometry.signedDistanceToPolygon({ x: 50, y: 50 }, polygon);
    assert.ok(distOutside > 0);
  });

  it("calculates boolean alpha blending modes accurately (add, subtract, intersect, difference)", () => {
    // Add: 0.5 + 0.5 * (1 - 0.5) = 0.75
    assert.strictEqual(MatteGenerator.blendAlpha(0.5, 0.5, "add"), 0.75);

    // Subtract: 0.8 * (1 - 0.5) = 0.4
    assert.strictEqual(MatteGenerator.blendAlpha(0.8, 0.5, "subtract"), 0.4);

    // Intersect: 0.8 * 0.5 = 0.4
    assert.strictEqual(MatteGenerator.blendAlpha(0.8, 0.5, "intersect"), 0.4);

    // Difference: |0.8 - 0.3| = 0.5
    assert.ok(Math.abs(MatteGenerator.blendAlpha(0.8, 0.3, "difference") - 0.5) < 1e-6);
  });
});
