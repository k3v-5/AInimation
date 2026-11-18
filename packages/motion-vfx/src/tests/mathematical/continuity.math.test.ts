import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Property } from "../../core/property.js";
import { Vector2 } from "../../core/types.js";

describe("Nivel 4 — Mathematical Tests: Keyframe Continuity", () => {
  it("guarantees exact continuity at keyframe boundaries for scalar properties", () => {
    const prop = new Property<number>(0);
    prop.addKeyframe(0, 0, "easeIn");
    prop.addKeyframe(1, 100, "easeOut");
    prop.addKeyframe(2, 200);

    // Exact keyframe timestamps must return exact values without any floating point decay
    assert.strictEqual(prop.evaluate(0), 0);
    assert.strictEqual(prop.evaluate(1), 100);
    assert.strictEqual(prop.evaluate(2), 200);
  });

  it("guarantees exact continuity at keyframe boundaries for Vector2 properties", () => {
    const pos = new Property<Vector2>({ x: 0, y: 0 });
    pos.addKeyframe(0.5, { x: 123.456, y: 789.012 }, "easeInOut");
    pos.addKeyframe(1.5, { x: 500.5, y: 600.6 });

    assert.deepStrictEqual(pos.evaluate(0.5), { x: 123.456, y: 789.012 });
    assert.deepStrictEqual(pos.evaluate(1.5), { x: 500.5, y: 600.6 });
  });

  it("evaluates multiple independent segments with respective easings", () => {
    const prop = new Property<number>(0);
    // 0 -> 1 using easeOut
    prop.addKeyframe(0, 0, "easeOut");
    // 1 -> 2 using easeIn
    prop.addKeyframe(1, 100, "easeIn");
    // 2s end
    prop.addKeyframe(2, 0);

    // Segment 1 midpoint: 0.5s with easeOut: 1 - (1 - 0.5)^3 = 0.875 -> 87.5
    assert.strictEqual(prop.evaluate(0.5), 87.5);

    // Keyframe boundary at 1.0s
    assert.strictEqual(prop.evaluate(1.0), 100);

    // Segment 2 midpoint: 1.5s (progress 0.5 in [1, 2]) with easeIn: 0.5^3 = 0.125 -> 100 + (0 - 100) * 0.125 = 87.5
    assert.strictEqual(prop.evaluate(1.5), 87.5);

    // Keyframe boundary at 2.0s
    assert.strictEqual(prop.evaluate(2.0), 0);
  });
});
