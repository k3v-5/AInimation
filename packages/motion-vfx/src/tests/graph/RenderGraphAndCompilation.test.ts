import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { RenderGraph } from "../../graph/core/RenderGraph.js";
import { RenderContext } from "../../graph/types/index.js";

describe("Fase 5H — RenderGraph DAG Compilation & Execution Tests", () => {
  it("compiles and executes DAG in topological order passing data between nodes", () => {
    const graph = new RenderGraph();

    // Node A: Source Generator -> returns 10
    graph.addNode({
      id: "node_src",
      type: "source",
      inputs: [],
      evaluate: () => 10,
    });

    // Node B: Multiplier -> takes node_src and multiplies by 2
    graph.addNode({
      id: "node_mult",
      type: "effect",
      inputs: ["node_src"],
      evaluate: (_ctx, inputs) => inputs.get("node_src") * 2,
    });

    // Node C: Adder -> takes node_mult and adds 5
    graph.addNode({
      id: "node_add",
      type: "composite",
      inputs: ["node_mult"],
      evaluate: (_ctx, inputs) => inputs.get("node_mult") + 5,
    });

    const ctx: RenderContext = {
      time: 0,
      frame: 0,
      width: 1080,
      height: 1920,
      quality: { resolutionScale: 1.0, effectsQuality: 1.0, motionBlur: false, antialiasing: true },
    };

    const results = graph.execute(ctx);
    assert.strictEqual(results.get("node_src"), 10);
    assert.strictEqual(results.get("node_mult"), 20);
    assert.strictEqual(results.get("node_add"), 25);
  });

  it("detects cyclic dependency and throws ValidationError with GRAPH_CYCLE_DETECTED", () => {
    const graph = new RenderGraph();

    // Ciclo A -> B -> A
    graph.addNode({
      id: "node_a",
      type: "t",
      inputs: ["node_b"],
      evaluate: () => 0,
    });

    graph.addNode({
      id: "node_b",
      type: "t",
      inputs: ["node_a"],
      evaluate: () => 0,
    });

    assert.throws(() => graph.compile(), /GRAPH_CYCLE_DETECTED/);
  });
});
