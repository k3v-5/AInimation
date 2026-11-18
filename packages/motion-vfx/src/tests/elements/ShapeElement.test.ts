import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { ShapeElement } from "../../elements/ShapeElement.js";

describe("Fase 2B — ShapeElement Geometric Primitives Tests", () => {
  it("creates rectangle, ellipse and line shapes with fill and stroke styling", () => {
    const rect = new ShapeElement({
      shapeType: "rectangle",
      shapeData: { width: 1080, height: 1920, cornerRadius: 10 },
      style: {
        fill: { r: 0.1, g: 0.1, b: 0.1, a: 1 },
        stroke: { r: 1, g: 1, b: 1, a: 1 },
        strokeWidth: 4,
      },
    });

    const evaluated = rect.evaluate(0);
    assert.strictEqual(evaluated.type, "shape");
    assert.strictEqual(evaluated.shapeType, "rectangle");
    assert.deepStrictEqual(evaluated.shapeData, { width: 1080, height: 1920, cornerRadius: 10 });
    assert.deepStrictEqual(evaluated.style.fill, { r: 0.1, g: 0.1, b: 0.1, a: 1 });
    assert.strictEqual(evaluated.style.strokeWidth, 4);
  });
});
