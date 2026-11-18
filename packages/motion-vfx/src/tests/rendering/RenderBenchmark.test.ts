import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Compositor, RenderLayerItem } from "../../rendering/compositor/Compositor.js";
import { RenderGraph, RenderNode } from "../../rendering/graph/RenderGraph.js";
import { FrameScheduler } from "../../rendering/scheduler/FrameScheduler.js";

describe("Fase 9 — Render & Export Benchmark Suite", () => {
  it("benchmarks scheduling 1,000 frames, compositing 500 layers and evaluating 1,000 cache lookups", async () => {
    // 1. Benchmark FrameScheduler (1,000 frames)
    const t0 = performance.now();
    let frameCount = 0;
    for await (const _ of FrameScheduler.generateFrames(1000, 30, 1920, 1080)) {
      frameCount++;
    }
    const schedElapsed = performance.now() - t0;
    assert.strictEqual(frameCount, 1000);

    // 2. Benchmark Compositor (500 layer stacks)
    const layers: RenderLayerItem[] = Array.from({ length: 5 }, (_, i) => ({
      id: `l_${i}`,
      frame: { frameNumber: 0, time: 0, width: 1920, height: 1080, channels: 4 },
      opacity: 0.8,
      blendMode: "normal",
    }));

    const ctx = { frame: 0, time: 0, fps: 30, width: 1920, height: 1080, quality: "final" as const };
    const t1 = performance.now();
    for (let i = 0; i < 500; i++) {
      Compositor.composite(layers, ctx);
    }
    const compElapsed = performance.now() - t1;

    // 3. Benchmark RenderGraph Cache (1,000 lookups)
    const graph = new RenderGraph();
    const node: RenderNode = {
      id: "node_01",
      type: "transform",
      inputs: [],
      parameters: { x: 10, y: 20 },
      cacheable: true,
    };
    graph.addNode(node);
    graph.evaluateNode("node_01", ctx); // Primera vez para poblar caché

    const t2 = performance.now();
    for (let i = 0; i < 1000; i++) {
      graph.evaluateNode("node_01", ctx);
    }
    const cacheElapsed = performance.now() - t2;

    // Presupuesto: < 100ms para cada tarea
    assert.ok(schedElapsed < 100, `Scheduling took ${schedElapsed.toFixed(2)}ms (budget: <100ms)`);
    assert.ok(compElapsed < 100, `Compositing took ${compElapsed.toFixed(2)}ms (budget: <100ms)`);
    assert.ok(cacheElapsed < 100, `Cache lookups took ${cacheElapsed.toFixed(2)}ms (budget: <100ms)`);
  });
});
