import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Property } from "../../core/property.js";
import { Vector2 } from "../../core/types.js";
import { InvalidTimeError } from "../../errors/index.js";

describe("Property<T>", () => {
  it("evaluates static value for any time when no keyframes exist", () => {
    const opacity = new Property<number>(1);
    assert.strictEqual(opacity.evaluate(0), 1);
    assert.strictEqual(opacity.evaluate(1), 1);
    assert.strictEqual(opacity.evaluate(500), 1);
  });

  it("getValue and setValue modify static base value", () => {
    const prop = new Property<number>(50);
    assert.strictEqual(prop.getValue(), 50);
    prop.setValue(100);
    assert.strictEqual(prop.getValue(), 100);
    assert.strictEqual(prop.evaluate(0), 100);
  });

  it("evaluates single keyframe as constant hold value", () => {
    const prop = new Property<number>(0);
    prop.addKeyframe(2.0, 75);
    assert.strictEqual(prop.evaluate(0), 75);
    assert.strictEqual(prop.evaluate(2.0), 75);
    assert.strictEqual(prop.evaluate(10), 75);
  });

  it("evaluates linear interpolation between two keyframes", () => {
    const opacity = new Property<number>(0);
    opacity.addKeyframe(0, 0);
    opacity.addKeyframe(1, 1);

    assert.strictEqual(opacity.evaluate(0), 0);
    assert.strictEqual(opacity.evaluate(0.25), 0.25);
    assert.strictEqual(opacity.evaluate(0.5), 0.5);
    assert.strictEqual(opacity.evaluate(0.75), 0.75);
    assert.strictEqual(opacity.evaluate(1), 1);
  });

  it("evaluates hold behavior before first and after last keyframe", () => {
    const prop = new Property<number>(0);
    prop.addKeyframe(1.0, 100);
    prop.addKeyframe(2.0, 200);

    // Before first keyframe
    assert.strictEqual(prop.evaluate(0), 100);
    assert.strictEqual(prop.evaluate(0.5), 100);
    assert.strictEqual(prop.evaluate(1.0), 100);

    // In between
    assert.strictEqual(prop.evaluate(1.5), 150);

    // After last keyframe
    assert.strictEqual(prop.evaluate(2.0), 200);
    assert.strictEqual(prop.evaluate(3.0), 200);
    assert.strictEqual(prop.evaluate(100), 200);
  });

  it("evaluates multiple segments with distinct easings", () => {
    const prop = new Property<number>(0);
    prop.addKeyframe(0, 0, "easeOut");
    prop.addKeyframe(1, 100, "linear");
    prop.addKeyframe(2, 200);

    // Segment 1 (0 -> 1 with easeOut): easeOut(0.5) = 0.875 -> 87.5
    assert.strictEqual(prop.evaluate(0.5), 87.5);

    // Exact keyframe at 1.0
    assert.strictEqual(prop.evaluate(1.0), 100);

    // Segment 2 (1 -> 2 with linear): 1.5 -> 150
    assert.strictEqual(prop.evaluate(1.5), 150);
    assert.strictEqual(prop.evaluate(2.0), 200);
  });

  it("replaces existing keyframe on duplicate timestamp", () => {
    const prop = new Property<number>(0);
    prop.addKeyframe(1.0, 100);
    assert.strictEqual(prop.getKeyframes().length, 1);
    assert.strictEqual(prop.evaluate(1.0), 100);

    // Duplicate timestamp -> replace
    prop.addKeyframe(1.0, 200);
    assert.strictEqual(prop.getKeyframes().length, 1);
    assert.strictEqual(prop.evaluate(1.0), 200);
  });

  it("maintains keyframes sorted chronologically regardless of insertion order", () => {
    const prop = new Property<number>(0);
    prop.addKeyframe(2.0, 200);
    prop.addKeyframe(0.0, 0);
    prop.addKeyframe(1.0, 100);

    const kfs = prop.getKeyframes();
    assert.strictEqual(kfs.length, 3);
    assert.strictEqual(kfs[0].time, 0.0);
    assert.strictEqual(kfs[1].time, 1.0);
    assert.strictEqual(kfs[2].time, 2.0);
  });

  it("removes keyframe by timestamp and clears all keyframes", () => {
    const prop = new Property<number>(0);
    prop.addKeyframe(0, 0);
    prop.addKeyframe(1, 100);
    prop.addKeyframe(2, 200);

    assert.strictEqual(prop.removeKeyframe(1), true);
    assert.strictEqual(prop.removeKeyframe(999), false);
    assert.strictEqual(prop.getKeyframes().length, 2);

    prop.clearKeyframes();
    assert.strictEqual(prop.getKeyframes().length, 0);
    assert.strictEqual(prop.evaluate(1), 0);
  });

  it("interpolates Vector2 property", () => {
    const pos = new Property<Vector2>({ x: 0, y: 0 });
    pos.addKeyframe(0, { x: 100, y: 200 }, "linear");
    pos.addKeyframe(2, { x: 300, y: 600 });

    const mid = pos.evaluate(1);
    assert.deepStrictEqual(mid, { x: 200, y: 400 });
  });

  it("rejects invalid timestamps", () => {
    const prop = new Property<number>(0);
    assert.throws(() => prop.evaluate(-1), InvalidTimeError);
    assert.throws(() => prop.evaluate(NaN), InvalidTimeError);
    assert.throws(() => prop.evaluate(Infinity), InvalidTimeError);
    assert.throws(() => prop.addKeyframe(-5, 100), InvalidTimeError);
  });
});
