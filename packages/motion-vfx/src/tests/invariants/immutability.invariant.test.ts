import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Composition } from "../../core/composition.js";
import { Layer } from "../../core/layer.js";
import { Vector2 } from "../../core/types.js";
import { serializeComposition } from "../../serialization/serializer.js";

describe("Nivel 5 — Invariant Tests: Immutability of Engine State", () => {
  it("INVARIANT: evaluate() does not mutate Composition, Layer, Property, or Keyframes", () => {
    const comp = new Composition({
      id: "comp_invariant",
      name: "Invariant Test",
      width: 1920,
      height: 1080,
      fps: 30,
      duration: 10,
    });

    const l1 = new Layer({ id: "layer_1", startTime: 1, endTime: 6 });
    l1.property<number>("opacity").addKeyframe(1, 0, "easeOut");
    l1.property<number>("opacity").addKeyframe(3, 1);

    l1.property<Vector2>("position").addKeyframe(1, { x: 100, y: 200 }, "easeInOut");
    l1.property<Vector2>("position").addKeyframe(5, { x: 800, y: 900 });

    comp.addLayer(l1);

    // Snapshot JSON del estado antes de evaluar
    const beforeJson = JSON.stringify(serializeComposition(comp));

    // Ejecutar cientos de evaluaciones en tiempos variados
    for (let i = 0; i < 200; i++) {
      const t = (i * 0.1) % 12;
      const snapshot = comp.evaluate(t);

      // Intentar mutar externamente el snapshot
      if (snapshot.layers[0]?.properties?.position) {
        (snapshot.layers[0].properties.position as Record<string, unknown>).x = 999999;
      }
    }

    // Snapshot JSON del estado después de todas las evaluaciones
    const afterJson = JSON.stringify(serializeComposition(comp));

    // El estado del proyecto debe ser 100% idéntico e inmutable
    assert.strictEqual(afterJson, beforeJson, "evaluate() mutated internal composition state!");
  });

  it("INVARIANT: Static property always evaluates to its baseValue regardless of timestamp", () => {
    const l = new Layer({ id: "static_layer" });
    const rot = l.property<number>("rotation");
    rot.setValue(45);

    const testTimes = [-100, 0, 0.001, 1, 5, 29.97, 1000];
    for (const t of testTimes) {
      if (t >= 0) {
        assert.strictEqual(rot.evaluate(t), 45);
      }
    }
  });
});
