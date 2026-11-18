import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { basic, parallel, sequence } from "../../animation/helpers.js";

describe("Fase 3A — Nested Animation Tree Composition Tests", () => {
  it("evaluates Parallel inside Sequence accurately", () => {
    // Paso 1: Fade In y Scale In simultáneos (1s)
    const entrance = parallel(
      basic({ target: { elementId: "logo", propertyPath: "transform.opacity" }, from: 0, to: 1, duration: 1.0 }),
      basic({ target: { elementId: "logo", propertyPath: "transform.scale" }, from: { x: 0.5, y: 0.5 }, to: { x: 1, y: 1 }, duration: 1.0 })
    );

    // Paso 2: Rotación (1s)
    const rotate = basic({
      target: { elementId: "logo", propertyPath: "transform.rotation" },
      from: 0,
      to: 360,
      duration: 1.0,
    });

    const fullSeq = sequence(entrance, rotate);
    assert.strictEqual(fullSeq.duration, 2.0);

    // En t = 0.5s: dentro del parallel
    const evalAt05 = fullSeq.evaluate(0.5);
    assert.strictEqual(evalAt05.get({ elementId: "logo", propertyPath: "transform.opacity" }), 0.5);
    assert.deepStrictEqual(evalAt05.get({ elementId: "logo", propertyPath: "transform.scale" }), { x: 0.75, y: 0.75 });
    assert.strictEqual(evalAt05.get({ elementId: "logo", propertyPath: "transform.rotation" }), 0);

    // En t = 1.5s: dentro de rotate (entrance ha terminado)
    const evalAt15 = fullSeq.evaluate(1.5);
    assert.strictEqual(evalAt15.get({ elementId: "logo", propertyPath: "transform.opacity" }), 1.0);
    assert.deepStrictEqual(evalAt15.get({ elementId: "logo", propertyPath: "transform.scale" }), { x: 1, y: 1 });
    assert.strictEqual(evalAt15.get({ elementId: "logo", propertyPath: "transform.rotation" }), 180);
  });

  it("evaluates Sequence inside Parallel accurately", () => {
    // Track continuo de opacidad (3s)
    const fade = basic({
      target: { elementId: "header", propertyPath: "transform.opacity" },
      from: 0,
      to: 1,
      duration: 3.0,
    });

    // Secuencia de saltos de posición: step 1 (1.5s) y step 2 (1.5s)
    const step1 = basic({
      target: { elementId: "header", propertyPath: "transform.position" },
      from: { x: 0, y: 0 },
      to: { x: 100, y: 0 },
      duration: 1.5,
    });
    const step2 = basic({
      target: { elementId: "header", propertyPath: "transform.position" },
      from: { x: 100, y: 0 },
      to: { x: 100, y: 200 },
      duration: 1.5,
    });
    const moveSeq = sequence(step1, step2);

    const rootParallel = parallel(fade, moveSeq);
    assert.strictEqual(rootParallel.duration, 3.0);

    const evalAt225 = rootParallel.evaluate(2.25);
    // Opacidad en 2.25/3.0 = 0.75
    assert.strictEqual(evalAt225.get({ elementId: "header", propertyPath: "transform.opacity" }), 0.75);

    // Posición en 2.25s (0.75s dentro de step2 de 1.5s = 50% de step2): (100, 100)
    assert.deepStrictEqual(evalAt225.get({ elementId: "header", propertyPath: "transform.position" }), { x: 100, y: 100 });
  });
});
