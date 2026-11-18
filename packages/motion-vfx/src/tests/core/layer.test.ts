import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Layer } from "../../core/layer.js";
import { Property } from "../../core/property.js";
import { Vector2 } from "../../core/types.js";

describe("Layer", () => {
  it("initializes with default transformation properties", () => {
    const layer = new Layer({ id: "title", name: "Title Layer", startTime: 0, endTime: 5 });
    assert.strictEqual(layer.id, "title");
    assert.strictEqual(layer.name, "Title Layer");

    const pos = layer.property<Vector2>("position");
    const scale = layer.property<Vector2>("scale");
    const rot = layer.property<number>("rotation");
    const opacity = layer.property<number>("opacity");

    assert.ok(pos instanceof Property);
    assert.deepStrictEqual(pos.getValue(), { x: 0, y: 0 });
    assert.deepStrictEqual(scale.getValue(), { x: 1, y: 1 });
    assert.strictEqual(rot.getValue(), 0);
    assert.strictEqual(opacity.getValue(), 1);
  });

  it("checks active status in range [startTime, endTime)", () => {
    const layer = new Layer({ id: "l1", startTime: 2, endTime: 5 });
    assert.strictEqual(layer.isActive(1), false);
    assert.strictEqual(layer.isActive(1.999), false);
    assert.strictEqual(layer.isActive(2), true);
    assert.strictEqual(layer.isActive(4.999), true);
    assert.strictEqual(layer.isActive(5), false);
    assert.strictEqual(layer.isActive(6), false);
  });

  it("evaluates active and inactive layer snapshots", () => {
    const layer = new Layer({ id: "l1", name: "Layer 1", startTime: 2, endTime: 5 });
    layer.property<number>("opacity").addKeyframe(2, 0);
    layer.property<number>("opacity").addKeyframe(4, 1);

    // Inactive snapshot
    const inactive = layer.evaluate(1);
    assert.strictEqual(inactive.id, "l1");
    assert.strictEqual(inactive.active, false);
    assert.strictEqual(inactive.properties, undefined);

    // Active snapshot
    const active = layer.evaluate(3);
    assert.strictEqual(active.id, "l1");
    assert.strictEqual(active.active, true);
    assert.ok(active.properties);
    assert.strictEqual(active.properties.opacity, 0.5);
    assert.deepStrictEqual(active.properties.scale, { x: 1, y: 1 });
  });

  it("snapshot is immutable and decoupled from layer properties", () => {
    const layer = new Layer({ id: "l1", startTime: 0, endTime: 5 });
    const snapshot = layer.evaluate(2);
    assert.ok(snapshot.properties);

    // Mutating snapshot should not affect layer
    (snapshot.properties.scale as Record<string, unknown>).x = 999;
    assert.deepStrictEqual(layer.property<Vector2>("scale").getValue(), { x: 1, y: 1 });
  });
});
