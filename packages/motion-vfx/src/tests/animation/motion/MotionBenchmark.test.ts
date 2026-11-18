import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { bounce } from "../../../animation/motion/BounceMotion.js";
import { elastic } from "../../../animation/motion/ElasticMotion.js";
import { overshoot } from "../../../animation/motion/OvershootMotion.js";
import { shake } from "../../../animation/motion/ShakeMotion.js";
import { spring } from "../../../animation/motion/SpringMotion.js";
import { wiggle } from "../../../animation/motion/WiggleMotion.js";

describe("Fase 3C — Motion Functions Benchmark Tests", () => {
  it("benchmarks 100,000 evaluations across all 6 motion functions", () => {
    const motions = [
      overshoot({ amount: 1.0 }),
      spring({ preset: "snappy" }),
      bounce(),
      elastic(),
      shake(),
      wiggle(),
    ];

    const iterations = 100000;

    for (const m of motions) {
      const start = performance.now();
      let sum = 0;
      for (let i = 0; i < iterations; i++) {
        const p = (i % 1000) / 1000;
        sum += m.evaluate(p);
      }
      const elapsed = performance.now() - start;

      // 100,000 evaluaciones matemáticas en < 500ms
      assert.ok(
        elapsed < 500,
        `Performance budget exceeded for motion ${m.type}: 100k evals took ${elapsed.toFixed(2)}ms`
      );
      assert.ok(typeof sum === "number");
    }
  });
});
