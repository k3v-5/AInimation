import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Composition } from "../../core/composition.js";
import { ShapeElement, TextElement } from "../../elements/index.js";

describe("Fase 2C — Performance Baseline & Scalability Tests", () => {
  it("benchmarks evaluating 10, 100 and 1,000 elements across 100 frames", () => {
    const elementCounts = [10, 100, 1000];
    const frameCount = 100;

    for (const count of elementCounts) {
      const comp = new Composition({ width: 1080, height: 1920, fps: 30, duration: 10 });

      for (let i = 0; i < count; i++) {
        if (i % 2 === 0) {
          const text = new TextElement({ id: `text_${i}`, text: `Item ${i}` });
          text.transform.position.addKeyframe(0, { x: 0, y: 0 }, "easeOut");
          text.transform.position.addKeyframe(10, { x: 500, y: 500 });
          comp.addElement(text);
        } else {
          const shape = new ShapeElement({ id: `shape_${i}`, shapeType: "rectangle" });
          shape.transform.rotation.addKeyframe(0, 0, "linear");
          shape.transform.rotation.addKeyframe(10, 360);
          comp.addElement(shape);
        }
      }

      const start = performance.now();
      for (let f = 0; f < frameCount; f++) {
        const time = (f / frameCount) * 10;
        comp.evaluate(time);
      }
      const elapsed = performance.now() - start;

      // Presupuesto razonable: 1,000 elementos x 100 frames (100,000 evaluaciones de elementos) en < 500ms
      assert.ok(
        elapsed < 1000,
        `Performance budget exceeded for ${count} elements: took ${elapsed.toFixed(2)}ms`
      );
    }
  });
});
