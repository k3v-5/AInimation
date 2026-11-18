import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { BasicAnimation } from "../../animation/BasicAnimation.js";

describe("Fase 3A — BasicAnimation Lifecycle, Timing & Interpolation Tests", () => {
  it("manages lifecycle states cleanly: before, active, after", () => {
    const anim = new BasicAnimation({
      target: { elementId: "title", propertyPath: "transform.opacity" },
      from: 0,
      to: 1,
      delay: 1.0,
      duration: 2.0,
    });

    assert.strictEqual(anim.delay, 1.0);
    assert.strictEqual(anim.duration, 2.0);
    assert.strictEqual(anim.totalDuration, 3.0);

    assert.strictEqual(anim.getState(0.5), "before");
    assert.strictEqual(anim.getState(1.0), "active");
    assert.strictEqual(anim.getState(2.0), "active");
    assert.strictEqual(anim.getState(3.0), "active");
    assert.strictEqual(anim.getState(3.001), "after");
  });

  it("evaluates exact progress and clamped boundaries: -1, 0, 0.5, 1, 2", () => {
    const anim = new BasicAnimation({
      target: { elementId: "box", propertyPath: "transform.position" },
      from: { x: 0, y: 0 },
      to: { x: 100, y: 200 },
      duration: 2.0,
      easing: "linear",
    });

    // t <= 0 -> from (0, 0)
    const resNeg = anim.evaluate(-1);
    assert.deepStrictEqual(resNeg.get({ elementId: "box", propertyPath: "transform.position" }), { x: 0, y: 0 });

    const res0 = anim.evaluate(0);
    assert.deepStrictEqual(res0.get({ elementId: "box", propertyPath: "transform.position" }), { x: 0, y: 0 });

    // t = 1.0 (50% de 2.0s) -> (50, 100)
    const resMid = anim.evaluate(1.0);
    assert.deepStrictEqual(resMid.get({ elementId: "box", propertyPath: "transform.position" }), { x: 50, y: 100 });

    // t >= 2.0 -> to (100, 200)
    const resEnd = anim.evaluate(2.0);
    assert.deepStrictEqual(resEnd.get({ elementId: "box", propertyPath: "transform.position" }), { x: 100, y: 200 });

    const resAfter = anim.evaluate(5.0);
    assert.deepStrictEqual(resAfter.get({ elementId: "box", propertyPath: "transform.position" }), { x: 100, y: 200 });
  });

  it("interpolates Color RGBA with easeInOut curve accurately", () => {
    const anim = new BasicAnimation({
      target: { elementId: "shape", propertyPath: "style.fill" },
      from: { r: 0, g: 0, b: 0, a: 1 },
      to: { r: 1, g: 1, b: 1, a: 1 },
      duration: 1.0,
      easing: "easeInOut",
    });

    const resMid = anim.evaluate(0.5);
    const color = resMid.get<any>({ elementId: "shape", propertyPath: "style.fill" });

    // En t = 0.5 con easeInOut, progress = 0.5
    assert.ok(Math.abs(color.r - 0.5) < 1e-6);
    assert.ok(Math.abs(color.g - 0.5) < 1e-6);
    assert.ok(Math.abs(color.b - 0.5) < 1e-6);
    assert.strictEqual(color.a, 1);
  });
});
