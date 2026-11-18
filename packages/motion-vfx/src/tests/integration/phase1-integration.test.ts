import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Composition } from "../../core/composition.js";
import { Layer } from "../../core/layer.js";
import { Vector2 } from "../../core/types.js";
import { deserializeComposition } from "../../serialization/deserializer.js";
import { serializeComposition } from "../../serialization/serializer.js";

describe("Phase 1 Integration Test - Core Temporal Motion Engine", () => {
  it("executes the fundamental motion graphics animation and evaluation pipeline", () => {
    // 1. Crear composición
    const composition = new Composition({
      width: 1080,
      height: 1920,
      fps: 30,
      duration: 5,
    });

    // 2. Crear layer
    const title = new Layer({
      id: "title",
      name: "Main Title",
      startTime: 0,
      endTime: 5,
    });

    // 3. Animar Opacity: 0s -> 0 (easeOut), 0.5s -> 1
    title.property<number>("opacity").addKeyframe(0, 0, "easeOut");
    title.property<number>("opacity").addKeyframe(0.5, 1);

    // 4. Animar Scale: 0s -> {0.5, 0.5} (easeOut), 0.5s -> {1, 1}
    title.property<Vector2>("scale").addKeyframe(0, { x: 0.5, y: 0.5 }, "easeOut");
    title.property<Vector2>("scale").addKeyframe(0.5, { x: 1, y: 1 });

    composition.addLayer(title);

    // 5. Evaluar en t = 0.25 (la mitad del segmento de 0.5s)
    // progreso = 0.25 / 0.5 = 0.5
    // easeOut(0.5) = 1 - (1 - 0.5)^3 = 1 - 0.125 = 0.875
    // Opacity esperada: 0 + (1 - 0) * 0.875 = 0.875
    // Scale esperada: 0.5 + (1 - 0.5) * 0.875 = 0.5 + 0.4375 = 0.9375
    const state = composition.evaluate(0.25);

    assert.strictEqual(state.time, 0.25);
    assert.strictEqual(state.layers.length, 1);
    assert.strictEqual(state.layers[0].id, "title");
    assert.strictEqual(state.layers[0].active, true);

    const props = state.layers[0].properties!;
    assert.strictEqual(props.opacity, 0.875);
    assert.deepStrictEqual(props.scale, { x: 0.9375, y: 0.9375 });
    assert.strictEqual(props.rotation, 0);
    assert.deepStrictEqual(props.position, { x: 0, y: 0 });

    // 6. Prueba de Determinismo Absoluto: 100 evaluaciones idénticas
    for (let i = 0; i < 100; i++) {
      const repeatedState = composition.evaluate(0.25);
      assert.deepStrictEqual(repeatedState, state);
    }

    // 7. Prueba de ciclo completo de Serialización -> Deserialización -> Re-evaluación
    const json = serializeComposition(composition);
    const reloadedComposition = deserializeComposition(json);
    const reloadedState = reloadedComposition.evaluate(0.25);

    assert.deepStrictEqual(reloadedState, state);
  });
});
