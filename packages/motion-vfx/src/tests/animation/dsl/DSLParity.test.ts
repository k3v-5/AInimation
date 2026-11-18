import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { compileDSL } from "../../../animation/dsl/index.js";
import { hold, parallel, sequence } from "../../../animation/helpers.js";
import { overshoot } from "../../../animation/motion/OvershootMotion.js";
import { fadeIn, fadeOut } from "../../../animation/primitives/fade.js";
import { scaleIn } from "../../../animation/primitives/scale.js";
import { slideIn, slideOut } from "../../../animation/primitives/slide.js";
import { TextElement } from "../../../elements/TextElement.js";

describe("Fase 3E — DSL Compilation Parity Tests (DSL vs Programmatic Engine)", () => {
  it("DSL compiled tree produces 100% identical evaluations to hand-crafted engine API", () => {
    const text = new TextElement({ id: "parity_title", text: "Parity" });

    // 1. Árbol artesanal mediante API TypeScript directa
    const programmaticTree = sequence(
      parallel(
        slideIn(text, { direction: "up", distance: 100, duration: 0.5 }),
        fadeIn(text, { duration: 0.4 }),
        scaleIn(text, { from: 0.8, duration: 0.5, motion: overshoot({ amount: 1.0 }) })
      ),
      hold(1.5),
      parallel(
        fadeOut(text, { duration: 0.4 }),
        slideOut(text, { direction: "up", distance: 100, duration: 0.5 })
      )
    );

    // 2. Mismo pipeline expresado en el DSL declarativo
    const dslTree = compileDSL({
      version: 1,
      animations: [
        {
          type: "sequence",
          children: [
            {
              type: "parallel",
              children: [
                { type: "slideIn", target: "parity_title", direction: "up", distance: 100, duration: 0.5 },
                { type: "fadeIn", target: "parity_title", duration: 0.4 },
                {
                  type: "scaleIn",
                  target: "parity_title",
                  from: 0.8,
                  duration: 0.5,
                  motion: { type: "overshoot", amount: 1.0 },
                },
              ],
            },
            {
              type: "hold",
              duration: 1.5,
            },
            {
              type: "parallel",
              children: [
                { type: "fadeOut", target: "parity_title", duration: 0.4 },
                { type: "slideOut", target: "parity_title", direction: "up", distance: 100, duration: 0.5 },
              ],
            },
          ],
        },
      ],
    }).rootNodes[0];

    // 3. Comprobar duraciones idénticas
    assert.strictEqual(dslTree.duration, programmaticTree.duration);

    // 4. Comprobar paridad numérica exacta en todos los timestamps
    const timestamps = [0, 0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.25, 2.5];
    for (const t of timestamps) {
      const valProg = programmaticTree.evaluate(t).getAll();
      const valDSL = dslTree.evaluate(t).getAll();
      assert.deepStrictEqual(valDSL, valProg, `Evaluation mismatch at timestamp t=${t}`);
    }
  });
});
