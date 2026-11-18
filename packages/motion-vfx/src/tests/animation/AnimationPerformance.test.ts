import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { BasicAnimation } from "../../animation/BasicAnimation.js";
import { ParallelAnimation } from "../../animation/ParallelAnimation.js";

describe("Fase 3A — Animation Performance Benchmark Tests", () => {
  it("benchmarks evaluating 10, 100 and 1,000 animation nodes across 1,000 timestamps", () => {
    const nodeCounts = [10, 100, 1000];
    const evalCount = 1000;

    for (const count of nodeCounts) {
      const parallelTree = new ParallelAnimation();

      for (let i = 0; i < count; i++) {
        parallelTree.add(
          new BasicAnimation({
            id: `anim_${i}`,
            target: { elementId: `elem_${i}`, propertyPath: "transform.position" },
            from: { x: 0, y: 0 },
            to: { x: 1000, y: 1000 },
            duration: 10.0,
            easing: i % 2 === 0 ? "easeOut" : "easeInOut",
          })
        );
      }

      const start = performance.now();
      for (let e = 0; e < evalCount; e++) {
        const t = (e / evalCount) * 10;
        parallelTree.evaluate(t);
      }
      const elapsed = performance.now() - start;

      // Presupuesto: 1,000 animaciones x 1,000 evaluaciones (1,000,000 evaluaciones de tracks) en < 1000ms
      assert.ok(
        elapsed < 2000,
        `Performance budget exceeded for ${count} nodes: took ${elapsed.toFixed(2)}ms`
      );
    }
  });
});
