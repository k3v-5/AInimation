import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { LayoutEngine } from "../../graphics/layout/LayoutEngine.js";

describe("Fase 5J — Layout & Responsive Positioning Tests", () => {
  it("calculates canonical anchor positions with safe area offsets accurately", () => {
    const containerW = 1000;
    const containerH = 2000;
    const elW = 200;
    const elH = 100;

    const insets = { top: 100, bottom: 200, left: 50, right: 50 };

    // Center position
    const centerPos = LayoutEngine.calculateAnchorPosition("center", elW, elH, containerW, containerH, insets);
    // usableW = 900 -> x = 50 + (900 - 200)/2 = 400
    // usableH = 1700 -> y = 100 + (1700 - 100)/2 = 900
    assert.strictEqual(centerPos.x, 400);
    assert.strictEqual(centerPos.y, 900);

    // Top-left
    const tlPos = LayoutEngine.calculateAnchorPosition("top-left", elW, elH, containerW, containerH, insets);
    assert.strictEqual(tlPos.x, 50);
    assert.strictEqual(tlPos.y, 100);

    // Bottom-right
    const brPos = LayoutEngine.calculateAnchorPosition("bottom-right", elW, elH, containerW, containerH, insets);
    assert.strictEqual(brPos.x, 750); // 950 - 200 = 750
    assert.strictEqual(brPos.y, 1700); // 1800 - 100 = 1700
  });

  it("arranges elements in horizontal and vertical stack layouts with gap spacing", () => {
    const elements = [
      { width: 100, height: 50 },
      { width: 150, height: 50 },
      { width: 80, height: 50 },
    ];

    const hPositions = LayoutEngine.layoutStack(elements, { direction: "horizontal", gap: 10, alignment: "start" });
    assert.strictEqual(hPositions[0].x, 0);
    assert.strictEqual(hPositions[1].x, 110); // 100 + 10
    assert.strictEqual(hPositions[2].x, 270); // 110 + 150 + 10

    const vPositions = LayoutEngine.layoutStack(elements, { direction: "vertical", gap: 20, alignment: "start" });
    assert.strictEqual(vPositions[0].y, 0);
    assert.strictEqual(vPositions[1].y, 70); // 50 + 20
    assert.strictEqual(vPositions[2].y, 140); // 70 + 50 + 20
  });
});
