import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { BasicAnimation } from "../../animation/BasicAnimation.js";
import { SequenceAnimation } from "../../animation/SequenceAnimation.js";

describe("Fase 3A — SequenceAnimation Sequential Composition Tests", () => {
  it("calculates totalDuration as sum(child.delay + child.duration)", () => {
    const step1 = new BasicAnimation({
      target: { elementId: "dot", propertyPath: "transform.position" },
      from: { x: 0, y: 0 },
      to: { x: 100, y: 0 },
      duration: 1.0,
    });

    const step2 = new BasicAnimation({
      target: { elementId: "dot", propertyPath: "transform.position" },
      from: { x: 100, y: 0 },
      to: { x: 100, y: 100 },
      duration: 2.0,
    });

    const sequence = new SequenceAnimation({ delay: 0.5, children: [step1, step2] });

    // step1 = 1.0, step2 = 2.0 -> duration = 3.0
    // totalDuration = 0.5 + 3.0 = 3.5
    assert.strictEqual(sequence.duration, 3.0);
    assert.strictEqual(sequence.totalDuration, 3.5);
  });

  it("evaluates active sequence step and maintains previous step end states", () => {
    const stepA = new BasicAnimation({
      target: { elementId: "title", propertyPath: "transform.opacity" },
      from: 0,
      to: 1,
      duration: 1.0,
      easing: "linear",
    });

    const stepB = new BasicAnimation({
      target: { elementId: "title", propertyPath: "transform.scale" },
      from: { x: 1, y: 1 },
      to: { x: 1.5, y: 1.5 },
      duration: 2.0,
      easing: "linear",
    });

    const sequence = new SequenceAnimation({ children: [stepA, stepB] });

    // En t = 0.5s:
    // stepA está en 50% -> opacity = 0.5
    // stepB aún no empieza -> scale = from (1, 1)
    const resAt05 = sequence.evaluate(0.5);
    assert.strictEqual(resAt05.get({ elementId: "title", propertyPath: "transform.opacity" }), 0.5);
    assert.deepStrictEqual(resAt05.get({ elementId: "title", propertyPath: "transform.scale" }), { x: 1, y: 1 });

    // En t = 2.0s (1.0s después de iniciar stepB de 2.0s = 50% de stepB):
    // stepA ha terminado -> opacity = 1.0 (mantiene final)
    // stepB está en 50% -> scale = (1.25, 1.25)
    const resAt20 = sequence.evaluate(2.0);
    assert.strictEqual(resAt20.get({ elementId: "title", propertyPath: "transform.opacity" }), 1.0);
    assert.deepStrictEqual(resAt20.get({ elementId: "title", propertyPath: "transform.scale" }), { x: 1.25, y: 1.25 });

    // En t = 4.0s (después del final de la secuencia = 3.0s):
    // ambos pasos mantienen sus valores finales
    const resAt40 = sequence.evaluate(4.0);
    assert.strictEqual(resAt40.get({ elementId: "title", propertyPath: "transform.opacity" }), 1.0);
    assert.deepStrictEqual(resAt40.get({ elementId: "title", propertyPath: "transform.scale" }), { x: 1.5, y: 1.5 });
  });
});
