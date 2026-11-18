import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { resetIdGenerators } from "../../core/id.js";
import { Composition } from "../../core/composition.js";
import { Layer } from "../../core/layer.js";
import { Vector2 } from "../../core/types.js";
import { SerializationError } from "../../errors/index.js";
import { deserializeComposition } from "../../serialization/deserializer.js";
import { serializeComposition } from "../../serialization/serializer.js";

describe("Serialization & Deserialization", () => {
  it("serializes and deserializes composition preserving all properties, keyframes and easings", () => {
    const comp = new Composition({
      id: "comp_test",
      name: "Test Composition",
      width: 1080,
      height: 1920,
      fps: 60,
      duration: 15,
    });

    const layer = new Layer({
      id: "layer_title",
      name: "Title",
      startTime: 1,
      endTime: 8,
    });

    layer.property<Vector2>("position").addKeyframe(1, { x: 100, y: 200 }, "easeOut");
    layer.property<Vector2>("position").addKeyframe(3, { x: 500, y: 800 });

    layer.property<number>("opacity").addKeyframe(1, 0, "easeInOut");
    layer.property<number>("opacity").addKeyframe(2, 1);

    comp.addLayer(layer);

    // 1. Serializar
    const serialized = serializeComposition(comp);
    assert.strictEqual(serialized.schemaVersion, "0.1.0");
    assert.strictEqual(serialized.composition.id, "comp_test");
    assert.strictEqual(serialized.composition.layers?.length, 1);

    // 2. Deserializar
    const restored = deserializeComposition(serialized);
    assert.strictEqual(restored.id, comp.id);
    assert.strictEqual(restored.name, comp.name);
    assert.strictEqual(restored.width, comp.width);
    assert.strictEqual(restored.height, comp.height);
    assert.strictEqual(restored.fps, comp.fps);
    assert.strictEqual(restored.duration, comp.duration);

    const restoredLayer = restored.getLayer("layer_title");
    assert.ok(restoredLayer);
    assert.strictEqual(restoredLayer.startTime, 1);
    assert.strictEqual(restoredLayer.endTime, 8);

    // 3. Comparar evaluación idéntica
    for (let t = 0; t <= 10; t += 0.5) {
      const origEval = comp.evaluate(t);
      const restEval = restored.evaluate(t);
      assert.deepStrictEqual(restEval, origEval, `Mismatch at time t=${t}`);
    }
  });

  it("preserves spatial metadata (tangents and spatialInterpolation) across serialization", () => {
    const comp = new Composition({ id: "comp_spatial", width: 1920, height: 1080, fps: 30, duration: 10 });
    const layer = new Layer({ id: "layer_motion" });

    layer.property<Vector2>("position").addKeyframe({
      time: 0,
      value: { x: 100, y: 100 },
      easing: "easeOut",
      spatialIn: { x: 0, y: 0 },
      spatialOut: { x: 50, y: -20 },
      spatialInterpolation: "bezier",
    });

    layer.property<Vector2>("position").addKeyframe({
      time: 2,
      value: { x: 800, y: 500 },
      spatialIn: { x: -30, y: 40 },
      spatialOut: { x: 0, y: 0 },
      spatialInterpolation: "bezier",
    });

    comp.addLayer(layer);

    const json = serializeComposition(comp);
    const restored = deserializeComposition(json);
    const restoredKeyframes = restored.getLayer("layer_motion")!.property<Vector2>("position").getKeyframes();

    assert.strictEqual(restoredKeyframes.length, 2);
    assert.deepStrictEqual(restoredKeyframes[0].spatialOut, { x: 50, y: -20 });
    assert.strictEqual(restoredKeyframes[0].spatialInterpolation, "bezier");
    assert.deepStrictEqual(restoredKeyframes[1].spatialIn, { x: -30, y: 40 });
  });

  it("generates deterministic IDs and respects resetIdGenerators()", () => {
    resetIdGenerators();

    const c1 = new Composition({ width: 1920, height: 1080, fps: 30, duration: 5 });
    const l1 = new Layer();
    const l2 = new Layer();

    assert.strictEqual(c1.id, "comp_1");
    assert.strictEqual(l1.id, "layer_1");
    assert.strictEqual(l2.id, "layer_2");

    // Resetting produces the exact same sequence for reproducibility
    resetIdGenerators();
    const c2 = new Composition({ width: 1920, height: 1080, fps: 30, duration: 5 });
    const l3 = new Layer();

    assert.strictEqual(c2.id, "comp_1");
    assert.strictEqual(l3.id, "layer_1");
  });

  it("throws SerializationError on invalid or missing schemaVersion", () => {
    assert.throws(() => {
      deserializeComposition({ schemaVersion: "9.9.9", composition: {} });
    }, SerializationError);

    assert.throws(() => {
      deserializeComposition({ composition: {} });
    }, SerializationError);
  });
});
