import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { BasicAnimation } from "../../animation/BasicAnimation.js";
import { ParallelAnimation } from "../../animation/ParallelAnimation.js";

describe("Fase 3A — ParallelAnimation Concurrent Composition Tests", () => {
  it("calculates totalDuration as max(child.delay + child.duration)", () => {
    const anim1 = new BasicAnimation({
      target: { elementId: "t1", propertyPath: "transform.opacity" },
      from: 0,
      to: 1,
      duration: 1.5,
    });

    const anim2 = new BasicAnimation({
      target: { elementId: "t1", propertyPath: "transform.scale" },
      from: { x: 0.5, y: 0.5 },
      to: { x: 1, y: 1 },
      delay: 0.5,
      duration: 2.0,
    });

    const parallel = new ParallelAnimation({ delay: 0.5, children: [anim1, anim2] });

    // anim1 total = 1.5
    // anim2 total = 0.5 + 2.0 = 2.5
    // parallel duration = 2.5
    // parallel totalDuration = 0.5 (delay) + 2.5 = 3.0
    assert.strictEqual(parallel.duration, 2.5);
    assert.strictEqual(parallel.totalDuration, 3.0);
  });

  it("merges results from multiple children into a single AnimationResult", () => {
    const posAnim = new BasicAnimation({
      target: { elementId: "card", propertyPath: "transform.position" },
      from: { x: 0, y: 0 },
      to: { x: 200, y: 0 },
      duration: 1.0,
      easing: "linear",
    });

    const opacityAnim = new BasicAnimation({
      target: { elementId: "card", propertyPath: "transform.opacity" },
      from: 0,
      to: 1,
      duration: 1.0,
      easing: "linear",
    });

    const parallel = new ParallelAnimation({ children: [posAnim, opacityAnim] });
    const result = parallel.evaluate(0.5);

    assert.deepStrictEqual(result.get({ elementId: "card", propertyPath: "transform.position" }), { x: 100, y: 0 });
    assert.strictEqual(result.get({ elementId: "card", propertyPath: "transform.opacity" }), 0.5);
  });

  it("resolves target conflicts in favor of higher priority child", () => {
    const baseAnim = new BasicAnimation({
      target: { elementId: "box", propertyPath: "transform.rotation" },
      from: 0,
      to: 90,
      duration: 1.0,
      priority: 0,
    });

    const overrideAnim = new BasicAnimation({
      target: { elementId: "box", propertyPath: "transform.rotation" },
      from: 180,
      to: 360,
      duration: 1.0,
      priority: 100,
    });

    const parallel = new ParallelAnimation({ children: [baseAnim, overrideAnim] });
    const result = parallel.evaluate(0.5);

    // Override (priority 100) debe ganar: 180 + 180 * 0.5 = 270
    assert.strictEqual(result.get({ elementId: "box", propertyPath: "transform.rotation" }), 270);
  });
});
