import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { applyPreset } from "../../presets/index.js";

describe("Fase 4A — Preset Resolution Benchmark Tests", () => {
  it("benchmarks resolving 1,000 preset expansions", () => {
    const target = { id: "perf_node", type: "text" as const };
    const iterations = 1000;

    const start = performance.now();
    for (let i = 0; i < iterations; i++) {
      const anim = applyPreset("popIn", target, { duration: 0.5, intensity: 0.8 });
      assert.strictEqual(anim.duration, 0.5);
    }
    const elapsed = performance.now() - start;

    // Presupuesto: 1,000 resoluciones y expansiones completas en < 500ms
    assert.ok(
      elapsed < 500,
      `Performance budget exceeded for 1,000 preset resolutions: took ${elapsed.toFixed(2)}ms`
    );
  });
});
