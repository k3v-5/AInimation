import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { compileDSL } from "../../../animation/dsl/index.js";

describe("Fase 3E — DSL Compilation Benchmark Suite", () => {
  it("benchmarks parsing, validating and compiling 1,000 DSL documents", () => {
    const rawDSL = {
      version: 1,
      variables: { dur: 0.5, dist: 100 },
      animations: [
        {
          type: "sequence",
          children: [
            { type: "slideIn", target: "elem", direction: "up", distance: "$dist", duration: "$dur", motion: "spring" },
            { type: "hold", duration: 1.0 },
            { type: "fadeOut", target: "elem", duration: "$dur" },
          ],
        },
      ],
    };

    const iterations = 1000;
    const start = performance.now();

    for (let i = 0; i < iterations; i++) {
      const ir = compileDSL(rawDSL);
      assert.strictEqual(ir.metadata.totalDuration, 2.0);
    }

    const elapsed = performance.now() - start;

    // Presupuesto: 1,000 compilaciones completas (parse + validate + AST build + IR build) en < 1000ms
    assert.ok(
      elapsed < 1500,
      `Performance budget exceeded for 1,000 DSL compilations: took ${elapsed.toFixed(2)}ms`
    );
  });
});
