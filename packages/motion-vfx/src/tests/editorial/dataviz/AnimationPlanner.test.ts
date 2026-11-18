import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { AnimationPlanner } from "../../../editorial/dataviz/animation-planner.js";
import { DataVizAnimation } from "../../../editorial/dataviz/types.js";

describe("Fase 5A — AnimationPlanner Suite", () => {
  it("evaluates LINEAR easing accurately", () => {
    assert.equal(AnimationPlanner.evaluateEasing(0.0, "LINEAR"), 0.0);
    assert.equal(AnimationPlanner.evaluateEasing(0.5, "LINEAR"), 0.5);
    assert.equal(AnimationPlanner.evaluateEasing(1.0, "LINEAR"), 1.0);
  });

  it("evaluates EASE_IN_CUBIC easing accurately", () => {
    assert.equal(AnimationPlanner.evaluateEasing(0.0, "EASE_IN_CUBIC"), 0.0);
    assert.equal(AnimationPlanner.evaluateEasing(0.5, "EASE_IN_CUBIC"), 0.125);
    assert.equal(AnimationPlanner.evaluateEasing(1.0, "EASE_IN_CUBIC"), 1.0);
  });

  it("evaluates EASE_OUT_CUBIC easing accurately", () => {
    assert.equal(AnimationPlanner.evaluateEasing(0.0, "EASE_OUT_CUBIC"), 0.0);
    assert.equal(AnimationPlanner.evaluateEasing(0.5, "EASE_OUT_CUBIC"), 0.875);
    assert.equal(AnimationPlanner.evaluateEasing(1.0, "EASE_OUT_CUBIC"), 1.0);
  });

  it("evaluates EASE_IN_OUT_CUBIC easing accurately", () => {
    assert.equal(AnimationPlanner.evaluateEasing(0.0, "EASE_IN_OUT_CUBIC"), 0.0);
    assert.equal(AnimationPlanner.evaluateEasing(0.5, "EASE_IN_OUT_CUBIC"), 0.5);
    assert.equal(AnimationPlanner.evaluateEasing(1.0, "EASE_IN_OUT_CUBIC"), 1.0);
  });

  it("validates animation bounds and invariants (REQ-025 §45)", () => {
    const validAnim: DataVizAnimation = {
      id: "a1",
      targetId: "t1",
      property: "SCALE",
      startSeconds: 0.2,
      endSeconds: 1.0,
      easing: "EASE_OUT_CUBIC",
      from: 0,
      to: 1,
    };
    assert.equal(AnimationPlanner.validateAnimation(validAnim, 2.0).length, 0);

    // Negative start
    const negAnim = { ...validAnim, startSeconds: -0.5 };
    assert.ok(AnimationPlanner.validateAnimation(negAnim, 2.0).some((i) => i.code === "NEGATIVE_START_TIME"));

    // Inverted duration
    const invAnim = { ...validAnim, startSeconds: 1.5, endSeconds: 1.0 };
    assert.ok(AnimationPlanner.validateAnimation(invAnim, 2.0).some((i) => i.code === "INVALID_DURATION"));

    // Exceeding composition duration
    const outAnim = { ...validAnim, startSeconds: 1.0, endSeconds: 3.5 };
    assert.ok(AnimationPlanner.validateAnimation(outAnim, 2.0).some((i) => i.code === "ANIMATION_OUT_OF_BOUNDS"));
  });

  it("calculates deterministic stagger delays without jitter (REQ-025 §48)", () => {
    assert.equal(AnimationPlanner.computeStaggerDelay(0, 0.05), 0.0);
    assert.equal(AnimationPlanner.computeStaggerDelay(1, 0.05), 0.05);
    assert.equal(AnimationPlanner.computeStaggerDelay(2, 0.05), 0.1);
    assert.equal(AnimationPlanner.computeStaggerDelay(3, 0.05), 0.15);
  });

  it("interpolates scalar and vector values", () => {
    assert.equal(AnimationPlanner.interpolate(0, 100, 0.5), 50);
    assert.deepEqual(AnimationPlanner.interpolate([0, 100], [200, 300], 0.5), [100, 200]);
  });
});
