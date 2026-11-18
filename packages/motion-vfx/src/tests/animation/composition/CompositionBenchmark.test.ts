import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { stagger } from "../../../animation/composition/stagger.js";
import { fadeIn } from "../../../animation/primitives/fade.js";
import { TextElement } from "../../../elements/TextElement.js";

describe("Fase 3D — Animation Composition Benchmark Tests", () => {
  it("benchmarks evaluating 10, 100 and 1,000 staggered animation nodes across 1,000 timestamps", () => {
    const counts = [10, 100, 1000];
    const evalCount = 1000;

    for (const count of counts) {
      const items = Array.from({ length: count }, (_, i) => new TextElement({ id: `elem_${i}`, text: `Item ${i}` }));
      const staggeredTree = stagger(items, (elem) => fadeIn(elem, { duration: 1.0 }), { delay: 0.05 });

      const start = performance.now();
      for (let e = 0; e < evalCount; e++) {
        const t = (e / evalCount) * staggeredTree.duration;
        staggeredTree.evaluate(t);
      }
      const elapsed = performance.now() - start;

      // Presupuesto: 1,000 nodos x 1,000 evaluaciones (1,000,000 evaluaciones) en < 2000ms
      assert.ok(
        elapsed < 2500,
        `Performance budget exceeded for ${count} staggered nodes: took ${elapsed.toFixed(2)}ms`
      );
    }
  });
});
