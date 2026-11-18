import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Transform } from "../../transform/Transform.js";

describe("Fase 2A — Transform Class & Keyframes Tests", () => {
  it("initializes with default motion graphics values", () => {
    const t = new Transform();

    assert.deepStrictEqual(t.position.getValue(), { x: 0, y: 0 });
    assert.deepStrictEqual(t.scale.getValue(), { x: 1, y: 1 });
    assert.strictEqual(t.rotation.getValue(), 0);
    assert.strictEqual(t.opacity.getValue(), 1);
    assert.deepStrictEqual(t.anchorPoint.getValue(), { x: 0.5, y: 0.5 });
  });

  it("animates position, scale, rotation and opacity using Property<T>", () => {
    const t = new Transform();
    t.position.addKeyframe(0, { x: 0, y: 0 }, "easeOut");
    t.position.addKeyframe(1, { x: 100, y: 200 });

    t.scale.addKeyframe(0, { x: 0.5, y: 0.5 }, "easeInOut");
    t.scale.addKeyframe(1, { x: 1.5, y: 1.5 });

    t.rotation.addKeyframe(0, 0, "linear");
    t.rotation.addKeyframe(2, 360);

    t.opacity.addKeyframe(0, 0, "linear");
    t.opacity.addKeyframe(0.5, 1);

    const evaluated = t.evaluate(0.5);

    // Opacity reaches 1 at 0.5s
    assert.strictEqual(evaluated.opacity, 1);

    // Rotation at 0.5s in [0, 2] with linear: 0 + 360 * 0.25 = 90 deg
    assert.strictEqual(t.rotation.evaluate(0.5), 90);

    // Scale at 0.5s with easeInOut: 0.5 + 1.0 * 0.5 = 1.0
    assert.deepStrictEqual(t.scale.evaluate(0.5), { x: 1, y: 1 });
  });
});
