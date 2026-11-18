import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { MaskInterpolator } from "../../masks/core/MaskInterpolator.js";
import { MaskPathGeometry } from "../../masks/core/MaskPathGeometry.js";
import { RotoMask } from "../../masks/types/index.js";

describe("Fase 5G — RotoMask Keyframe Interpolation Tests", () => {
  it("interpolates mask paths smoothly across keyframes at midpoint time", () => {
    const path0 = MaskPathGeometry.createRectanglePath(0, 0, 100, 100);
    const path1 = MaskPathGeometry.createRectanglePath(100, 100, 100, 100);

    const roto: RotoMask = {
      id: "roto_1",
      type: "rectangle",
      mode: "add",
      feather: 0,
      expansion: 0,
      opacity: 1.0,
      frames: [
        { time: 0.0, path: path0 },
        { time: 2.0, path: path1 },
      ],
    };

    // Evaluar en t = 1.0s (punto medio 50%)
    const evaluatedMask = MaskInterpolator.evaluateRotoMask(roto, 1.0);
    assert.strictEqual(evaluatedMask.path.points.length, 4);

    // Primer punto debe estar en x = 50, y = 50
    assert.strictEqual(evaluatedMask.path.points[0].position.x, 50);
    assert.strictEqual(evaluatedMask.path.points[0].position.y, 50);
  });
});
