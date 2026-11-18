import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { MaskPathGeometry } from "../../masks/core/MaskPathGeometry.js";
import { MaskStack } from "../../masks/core/MaskStack.js";
import { MatteGenerator } from "../../masks/core/MatteGenerator.js";
import { Mask } from "../../masks/types/index.js";

describe("Fase 5G — Matte Generation, Feather & Expansion Tests", () => {
  it("generates single mask matte with feather edge transition", () => {
    const mask: Mask = {
      id: "m_rect",
      type: "rectangle",
      path: MaskPathGeometry.createRectanglePath(10, 10, 20, 20),
      mode: "add",
      feather: 4.0,
      expansion: 0.0,
      opacity: 1.0,
    };

    const matte = MatteGenerator.generateSingleMaskMatte(mask, 40, 40);
    assert.strictEqual(matte.width, 40);
    assert.strictEqual(matte.height, 40);

    // Centro (20, 20) -> dentro -> alfa = 1.0
    const centerIdx = 20 * 40 + 20;
    assert.strictEqual(matte.alpha[centerIdx], 1.0);

    // Borde exterior lejano (0, 0) -> alfa = 0.0
    assert.strictEqual(matte.alpha[0], 0.0);
  });

  it("evaluates mask stack with multiple masks combined", () => {
    const mask1: Mask = {
      id: "m1",
      type: "rectangle",
      path: MaskPathGeometry.createRectanglePath(0, 0, 50, 50),
      mode: "add",
      feather: 0,
      expansion: 0,
      opacity: 1.0,
    };

    const mask2: Mask = {
      id: "m2",
      type: "rectangle",
      path: MaskPathGeometry.createRectanglePath(20, 20, 20, 20),
      mode: "subtract", // Restar agujero en el centro
      feather: 0,
      expansion: 0,
      opacity: 1.0,
    };

    const stack = new MaskStack([mask1, mask2]);
    const matte = stack.evaluateMatte(100, 100);

    // En (10, 10) -> dentro de mask1 y fuera de mask2 -> alfa = 1.0
    const idx1 = 10 * 100 + 10;
    assert.strictEqual(matte.alpha[idx1], 1.0);

    // En (30, 30) -> dentro de mask2 restada -> alfa = 0.0
    const idxCenter = 30 * 100 + 30;
    assert.strictEqual(matte.alpha[idxCenter], 0.0);
  });
});
