import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Composition } from "../../core/composition.js";
import { Layer } from "../../core/layer.js";
import { DuplicateLayerError, LayerNotFoundError, ValidationError } from "../../errors/index.js";

describe("Composition", () => {
  it("initializes with valid options", () => {
    const comp = new Composition({
      id: "comp1",
      name: "Main",
      width: 1920,
      height: 1080,
      fps: 30,
      duration: 10,
    });

    assert.strictEqual(comp.id, "comp1");
    assert.strictEqual(comp.name, "Main");
    assert.strictEqual(comp.width, 1920);
    assert.strictEqual(comp.height, 1080);
    assert.strictEqual(comp.fps, 30);
    assert.strictEqual(comp.duration, 10);
  });

  it("validates constructor parameters", () => {
    assert.throws(() => new Composition({ width: 0, height: 1080, fps: 30, duration: 10 }), ValidationError);
    assert.throws(() => new Composition({ width: 1920, height: -100, fps: 30, duration: 10 }), ValidationError);
    assert.throws(() => new Composition({ width: 1920, height: 1080, fps: 0, duration: 10 }), ValidationError);
    assert.throws(() => new Composition({ width: 1920, height: 1080, fps: 30, duration: -1 }), ValidationError);
  });

  it("manages layers: add, get, remove, duplicate prevention", () => {
    const comp = new Composition({ width: 1920, height: 1080, fps: 30, duration: 10 });
    const layer1 = new Layer({ id: "bg", name: "Background" });
    const layer2 = new Layer({ id: "fg", name: "Foreground" });

    comp.addLayer(layer1);
    comp.addLayer(layer2);

    assert.strictEqual(comp.getLayers().length, 2);
    assert.strictEqual(comp.getLayer("bg"), layer1);
    assert.strictEqual(comp.getLayer("fg"), layer2);
    assert.strictEqual(comp.getLayer("nonexistent"), undefined);

    // Duplicate ID throws
    assert.throws(() => comp.addLayer(new Layer({ id: "bg" })), DuplicateLayerError);

    // Remove layer
    assert.strictEqual(comp.removeLayer("bg"), true);
    assert.strictEqual(comp.removeLayer("bg"), false);
    assert.strictEqual(comp.getLayers().length, 1);
  });

  it("moves layer in stacking order", () => {
    const comp = new Composition({ width: 1920, height: 1080, fps: 30, duration: 10 });
    const l1 = new Layer({ id: "l1" });
    const l2 = new Layer({ id: "l2" });
    const l3 = new Layer({ id: "l3" });

    comp.addLayer(l1);
    comp.addLayer(l2);
    comp.addLayer(l3);

    // Initial order: l1, l2, l3
    assert.deepStrictEqual(comp.getLayers().map((l) => l.id), ["l1", "l2", "l3"]);

    // Move l3 to index 0: l3, l1, l2
    comp.moveLayer("l3", 0);
    assert.deepStrictEqual(comp.getLayers().map((l) => l.id), ["l3", "l1", "l2"]);

    // Move non-existent throws
    assert.throws(() => comp.moveLayer("unknown", 0), LayerNotFoundError);
  });

  it("evaluates composition snapshot for a given time", () => {
    const comp = new Composition({ width: 1920, height: 1080, fps: 30, duration: 10 });
    const bg = new Layer({ id: "bg", startTime: 0, endTime: 10 });
    const title = new Layer({ id: "title", startTime: 2, endTime: 6 });

    title.property<number>("opacity").addKeyframe(2, 0);
    title.property<number>("opacity").addKeyframe(4, 1);

    comp.addLayer(bg);
    comp.addLayer(title);

    const snapshot = comp.evaluate(3);
    assert.strictEqual(snapshot.time, 3);
    assert.strictEqual(snapshot.duration, 10);
    assert.strictEqual(snapshot.width, 1920);
    assert.strictEqual(snapshot.height, 1080);
    assert.strictEqual(snapshot.fps, 30);
    assert.strictEqual(snapshot.layers.length, 2);

    assert.strictEqual(snapshot.layers[0].id, "bg");
    assert.strictEqual(snapshot.layers[0].active, true);

    assert.strictEqual(snapshot.layers[1].id, "title");
    assert.strictEqual(snapshot.layers[1].active, true);
    assert.strictEqual(snapshot.layers[1].properties?.opacity, 0.5);
  });
});
