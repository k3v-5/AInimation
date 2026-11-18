import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { RenderGraph, RenderNode } from "../../rendering/graph/RenderGraph.js";

describe("Fase 9 — Render Graph & Node Cache Tests", () => {
  it("evaluates DAG nodes and reuses cached outputs across duplicate evaluations", () => {
    const graph = new RenderGraph();

    let evalCount = 0;
    const blurNode: RenderNode = {
      id: "blur_01",
      type: "blur",
      inputs: [],
      parameters: { radius: 15 },
      cacheable: true,
      evaluate: (ctx) => {
        evalCount++;
        return {
          frameNumber: ctx.frame,
          time: ctx.time,
          width: ctx.width,
          height: ctx.height,
          channels: 4,
          metadata: { radius: 15 },
        };
      },
    };

    graph.addNode(blurNode);

    const ctx = { frame: 10, time: 0.33, fps: 30, width: 1920, height: 1080, quality: "final" as const };

    // Primera evaluación -> ejecuta evaluate()
    const frame1 = graph.evaluateNode("blur_01", ctx);
    assert.strictEqual(evalCount, 1);
    assert.strictEqual(frame1.frameNumber, 10);

    // Segunda evaluación con el mismo contexto -> debe reutilizar caché
    const frame2 = graph.evaluateNode("blur_01", ctx);
    assert.strictEqual(evalCount, 1); // No incrementa
    assert.strictEqual(graph.cachedEntriesCount, 1);
  });
});
