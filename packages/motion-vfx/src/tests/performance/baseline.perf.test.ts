import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Composition } from "../../core/composition.js";
import { Layer } from "../../core/layer.js";
import { Vector2 } from "../../core/types.js";

describe("Nivel 7 — Performance Baseline Test", () => {
  it("evaluates a heavy scene (100 layers x 10 properties x 20 keyframes) across 1000 timestamps within baseline budget", () => {
    const NUM_LAYERS = 100;
    const NUM_TIMESTAMPS = 1000;
    const DURATION = 30.0;

    const comp = new Composition({
      id: "perf_comp",
      name: "Performance Test Scene",
      width: 1920,
      height: 1080,
      fps: 60,
      duration: DURATION,
    });

    // 1. Construir 100 layers
    for (let l = 0; l < NUM_LAYERS; l++) {
      const layer = new Layer({
        id: `layer_${l}`,
        startTime: (l * 0.1) % 15,
        endTime: ((l * 0.1) % 15) + 15,
      });

      // Añadir 6 propiedades adicionales (más las 4 por defecto = 10 properties)
      for (let p = 0; p < 6; p++) {
        layer.property<number>(`custom_prop_${p}`, 0);
      }

      // Añadir 20 keyframes a cada una de las 10 propiedades
      for (const [, prop] of layer.getProperties().entries()) {
        const pTyped = prop as any;
        for (let k = 0; k < 20; k++) {
          const kTime = k * 1.5;
          const easing = k % 3 === 0 ? "easeOut" : k % 3 === 1 ? "easeInOut" : "linear";
          if (typeof pTyped.getValue() === "number") {
            pTyped.addKeyframe(kTime, k * 10, easing);
          } else {
            pTyped.addKeyframe(kTime, { x: k * 10, y: k * 20 }, easing);
          }
        }
      }

      comp.addLayer(layer);
    }

    // 2. Medir tiempo de evaluación de 1000 timestamps
    const startTime = performance.now();

    for (let t = 0; t < NUM_TIMESTAMPS; t++) {
      const time = (t / NUM_TIMESTAMPS) * DURATION;
      comp.evaluate(time);
    }

    const elapsedMs = performance.now() - startTime;
    console.log(`\n⚡ [Performance Baseline]: 100 layers x 10 props x 20 keyframes (1000 evaluations) completed in ${elapsedMs.toFixed(2)} ms (${(elapsedMs / NUM_TIMESTAMPS).toFixed(3)} ms/eval)`);

    // Budget: 1000 frames evaluated on a 100-layer project should complete under 3500ms in Node.js
    assert.ok(elapsedMs < 3500, `Performance regression detected! Took ${elapsedMs.toFixed(2)} ms (Budget: 3500 ms)`);
  });
});
