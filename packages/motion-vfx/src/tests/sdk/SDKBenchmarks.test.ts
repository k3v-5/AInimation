import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { MotionEngine } from "../../sdk/MotionEngineSDK.js";

describe("Fase 27 — Capa 5: SDK Performance & Benchmarks Suite", () => {
  it("benchmarks creating, exporting and delivering 100 projects via SDK in < 250ms", () => {
    const t0 = performance.now();
    const count = 100;

    for (let i = 0; i < count; i++) {
      const comp = MotionEngine.createComposition({
        id: `comp_bench_${i}`,
        name: `Comp ${i}`,
        width: 1920,
        height: 1080,
        fps: 30,
        duration: 5.0,
      });

      const exp = MotionEngine.exportToAfterEffects(comp);
      assert.ok(exp.jsxContent.length > 0);
    }

    const elapsed = performance.now() - t0;
    assert.ok(elapsed < 250, `SDK benchmark for ${count} operations took ${elapsed.toFixed(2)}ms (budget < 250ms)`);
  });
});
