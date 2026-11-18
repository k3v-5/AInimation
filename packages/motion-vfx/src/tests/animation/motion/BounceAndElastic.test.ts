import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { bounce } from "../../../animation/motion/BounceMotion.js";
import { elastic } from "../../../animation/motion/ElasticMotion.js";

describe("Fase 3C — Bounce & Elastic Motion Tests", () => {
  it("BounceMotion satisfies boundary conditions and produces multiple impacts", () => {
    const b = bounce();
    assert.strictEqual(b.evaluate(0), 0);
    assert.strictEqual(b.evaluate(1), 1);

    // En rebotes intermedios desciende antes de impactar de nuevo
    const valEarly = b.evaluate(0.35); // En la primera caída
    const valDrop = b.evaluate(0.45); // En el primer rebote
    assert.ok(valEarly > 0.8);
    assert.ok(valDrop > 0.7);
  });

  it("ElasticMotion produces damped oscillations settling at 1.0", () => {
    const el = elastic({ amplitude: 1.0, period: 0.3 });
    assert.strictEqual(el.evaluate(0), 0);
    assert.strictEqual(el.evaluate(1), 1);

    // Debe exceder 1.0 en su pico oscilatorio
    let maxVal = 0;
    for (let p = 0; p <= 1.0; p += 0.02) {
      const val = el.evaluate(p);
      if (val > maxVal) maxVal = val;
    }
    assert.ok(maxVal > 1.05, `Elastic must oscillate above 1.0, got ${maxVal}`);
  });
});
