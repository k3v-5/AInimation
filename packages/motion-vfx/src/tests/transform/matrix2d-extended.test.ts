import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Matrix2D } from "../../math/matrix2d.js";

describe("Fase 2A — Extended Matrix2D & Transform Math Tests", () => {
  it("composes matrix with normalized anchor point and element dimensions", () => {
    // Caja de 200x100 centrada en (500, 500) con rotación 0 y escala 1x
    // Anchor center (0.5, 0.5) -> offset (100, 50)
    const m = Matrix2D.composeWithNormalizedAnchor(
      { x: 500, y: 500 },
      { x: 1, y: 1 },
      0,
      { x: 0.5, y: 0.5 },
      { width: 200, height: 100 }
    );

    // La esquina top-left local (0, 0) debe proyectarse a (400, 450)
    const topLeft = Matrix2D.transformPoint(m, { x: 0, y: 0 });
    assert.strictEqual(topLeft.x, 400);
    assert.strictEqual(topLeft.y, 450);

    // El centro geométrico local (100, 50) debe proyectarse exactamente a la posición de anclaje (500, 500)
    const center = Matrix2D.transformPoint(m, { x: 100, y: 50 });
    assert.strictEqual(center.x, 500);
    assert.strictEqual(center.y, 500);
  });

  it("projects points back and forth with inverseTransformPoint", () => {
    const m = Matrix2D.compose({ x: 350, y: 720 }, { x: 1.5, y: 2.0 }, 45);
    const localPoint = { x: 42, y: 99 };

    const worldPoint = Matrix2D.transformPoint(m, localPoint);
    const reconstructedLocal = Matrix2D.inverseTransformPoint(m, worldPoint);

    assert.ok(Math.abs(reconstructedLocal.x - localPoint.x) < 1e-10);
    assert.ok(Math.abs(reconstructedLocal.y - localPoint.y) < 1e-10);
  });

  it("decomposes matrix accurately into position, scale, and degrees", () => {
    const originalPos = { x: 150, y: 250 };
    const originalScale = { x: 2.5, y: 1.5 };
    const originalRot = 60; // 60 grados

    const m = Matrix2D.compose(originalPos, originalScale, originalRot);
    const dec = Matrix2D.decompose(m);

    assert.ok(Math.abs(dec.position.x - originalPos.x) < 1e-10);
    assert.ok(Math.abs(dec.position.y - originalPos.y) < 1e-10);
    assert.ok(Math.abs(dec.scale.x - originalScale.x) < 1e-10);
    assert.ok(Math.abs(dec.scale.y - originalScale.y) < 1e-10);
    assert.ok(Math.abs(dec.rotationDeg - originalRot) < 1e-10);
  });

  it("transforms bounding boxes accurately under rotation and translation", () => {
    const m = Matrix2D.compose({ x: 100, y: 100 }, { x: 1, y: 1 }, 90);
    const box = { x: 0, y: 0, width: 50, height: 100 };

    const transformedBox = Matrix2D.transformBounds(m, box);
    assert.strictEqual(transformedBox.x, 0);
    assert.strictEqual(transformedBox.y, 100);
    assert.strictEqual(transformedBox.width, 100);
    assert.strictEqual(transformedBox.height, 50);
  });
});
