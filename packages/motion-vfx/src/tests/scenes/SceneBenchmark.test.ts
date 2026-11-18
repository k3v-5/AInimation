import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Scene } from "../../scenes/core/Scene.js";
import { SceneSequence } from "../../scenes/core/SceneSequence.js";
import { registerBuiltinTransitions } from "../../transitions/builtins/index.js";

describe("Fase 5C — Scene & Transition Performance Benchmark Suite", () => {
  registerBuiltinTransitions();

  it("benchmarks evaluating sequence of 50 scenes with transitions", () => {
    const sequence = new SceneSequence();
    const count = 50;

    for (let i = 0; i < count; i++) {
      const scene = new Scene({ id: `sc_${i}`, duration: 4.0 });
      sequence.addScene(scene, i < count - 1 ? { type: "zoom", duration: 0.5 } : undefined);
    }

    assert.strictEqual(sequence.size, 50);

    const totalDur = sequence.getTotalDuration();
    const iterations = 1000;
    const t0 = performance.now();

    for (let i = 0; i < iterations; i++) {
      const t = (i / iterations) * totalDur;
      const state = sequence.evaluate(t);
      assert.ok(state.activeScenes.length >= 1);
    }

    const elapsed = performance.now() - t0;

    // Presupuesto: 1,000 evaluaciones temporales de 50 escenas en < 500ms
    assert.ok(
      elapsed < 500,
      `1,000 scene sequence evaluations took ${elapsed.toFixed(2)}ms (budget: <500ms)`
    );
  });
});
