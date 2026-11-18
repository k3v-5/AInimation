import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { CameraMatrix } from "../../camera/core/CameraMatrix.js";
import { CameraShakeModifier } from "../../camera/modifiers/CameraModifiers.js";
import { Camera } from "../../camera/types/index.js";
import { RenderGraph } from "../../graph/core/RenderGraph.js";
import { RenderContext } from "../../graph/types/index.js";
import { Layer } from "../../scene/core/Layer.js";
import { Scene } from "../../scene/core/Scene.js";

describe("Fase 5H — Scene, Camera & RenderGraph Benchmark Suite", () => {
  it("benchmarks evaluating scene with 100 layers, camera projections and 50 DAG render nodes", () => {
    // 1. Scene con 100 layers
    const scene = new Scene({ duration: 30.0, width: 1080, height: 1920 });
    for (let i = 0; i < 100; i++) {
      scene.addLayer(new Layer({ id: `l_${i}`, type: "image", start: i * 0.2, duration: 5.0 }));
    }

    const t0 = performance.now();
    for (let f = 0; f < 1000; f++) {
      scene.getActiveLayers((f / 1000) * 30.0);
    }
    const sceneElapsed = performance.now() - t0;

    // 2. Camera Matrix projection & Shake para 1,000 frames
    const cam: Camera = { position: { x: 0, y: 0, z: 0 }, rotation: { x: 0, y: 0, z: 0 }, zoom: 1.0 };
    const shake = new CameraShakeModifier(15, 5, 42);

    const t1 = performance.now();
    for (let f = 0; f < 1000; f++) {
      const shakenCam = shake.evaluate(f * 0.033, cam);
      CameraMatrix.projectPoint({ x: 500, y: 500 }, shakenCam, 1080, 1920);
    }
    const camElapsed = performance.now() - t1;

    // 3. RenderGraph con 50 nodos encadenados
    const graph = new RenderGraph();
    graph.addNode({ id: "n_0", type: "src", inputs: [], evaluate: () => 1 });
    for (let i = 1; i < 50; i++) {
      graph.addNode({
        id: `n_${i}`,
        type: "op",
        inputs: [`n_${i - 1}`],
        evaluate: (_ctx, inputs) => inputs.get(`n_${i - 1}`) + 1,
      });
    }

    const ctx: RenderContext = {
      time: 0,
      frame: 0,
      width: 1080,
      height: 1920,
      quality: { resolutionScale: 1.0, effectsQuality: 1.0, motionBlur: false, antialiasing: true },
    };

    const t2 = performance.now();
    const results = graph.execute(ctx);
    const graphElapsed = performance.now() - t2;

    assert.strictEqual(results.get("n_49"), 50);

    // Presupuesto: < 100ms para cada etapa
    assert.ok(sceneElapsed < 100, `Scene layer query took ${sceneElapsed.toFixed(2)}ms (budget: <100ms)`);
    assert.ok(camElapsed < 100, `Camera projections took ${camElapsed.toFixed(2)}ms (budget: <100ms)`);
    assert.ok(graphElapsed < 100, `Graph execution took ${graphElapsed.toFixed(2)}ms (budget: <100ms)`);
  });
});
