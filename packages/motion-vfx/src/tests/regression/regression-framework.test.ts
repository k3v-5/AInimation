import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { easeIn, easeInOut, easeOut, linear } from "../../animation/easing.js";
import { Composition } from "../../core/composition.js";
import { Layer } from "../../core/layer.js";
import { Property } from "../../core/property.js";
import { deserializeComposition } from "../../serialization/deserializer.js";
import { serializeComposition } from "../../serialization/serializer.js";

describe("Nivel 7 — Regression Tests: Permanent Bug Defense Suite", () => {
  it("REGRESSION #001: Layer with endTime: Infinity deserializes and evaluates without throwing ValidationError", () => {
    const comp = new Composition({ width: 1920, height: 1080, fps: 30, duration: 10 });
    const layer = new Layer({ id: "infinite_layer" }); // endTime defaults to Infinity
    comp.addLayer(layer);

    const json = serializeComposition(comp);
    assert.doesNotThrow(() => {
      const restored = deserializeComposition(json);
      const snapshot = restored.evaluate(5);
      assert.strictEqual(snapshot.layers[0].active, true);
    });
  });

  it("REGRESSION #002: Unsorted keyframe additions are strictly sorted chronologically", () => {
    const prop = new Property<number>(0);
    prop.addKeyframe(10, 100);
    prop.addKeyframe(2, 20);
    prop.addKeyframe(5, 50);
    prop.addKeyframe(0, 0);

    const kfs = prop.getKeyframes();
    const timestamps = kfs.map((k) => k.time);
    assert.deepStrictEqual(timestamps, [0, 2, 5, 10]);
  });

  it("REGRESSION #003: Duplicate keyframe timestamps replace existing keyframe without creating duplicates", () => {
    const prop = new Property<number>(0);
    prop.addKeyframe(1.0, 10);
    prop.addKeyframe(1.0, 20);
    prop.addKeyframe(1.0, 30);

    assert.strictEqual(prop.getKeyframes().length, 1);
    assert.strictEqual(prop.evaluate(1.0), 30);
  });

  it("REGRESSION #004: Easing boundary guarantees 0.0 at t<=0 and 1.0 at t>=1 with exact float comparisons", () => {
    const fns = [linear, easeIn, easeOut, easeInOut];
    for (const fn of fns) {
      assert.strictEqual(fn(0), 0);
      assert.strictEqual(fn(1), 1);
      assert.strictEqual(fn(-10), 0);
      assert.strictEqual(fn(10), 1);
    }
  });
});
