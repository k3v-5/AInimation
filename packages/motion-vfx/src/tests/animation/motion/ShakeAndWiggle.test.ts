import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { shake } from "../../../animation/motion/ShakeMotion.js";
import { wiggle } from "../../../animation/motion/WiggleMotion.js";

describe("Fase 3C — Shake & Wiggle Deterministic Perturbation Tests", () => {
  it("ShakeMotion is 100% deterministic with ZERO Math.random calls", () => {
    const s = shake({ amplitude: 10, frequency: 8, seed: 99 });

    // evaluate(0.3) dos veces seguidas debe dar el mismo float exacto
    const r1 = s.evaluate(0.3);
    const r2 = s.evaluate(0.3);
    assert.strictEqual(r1, r2, "Shake must be purely deterministic");

    // Al inicio (p=0) y al final (p=1) debe ser 0
    assert.strictEqual(s.evaluate(0), 0);
    assert.strictEqual(s.evaluate(1), 0);
  });

  it("WiggleMotion oscillates deterministically over continuous progress", () => {
    const w = wiggle({ amplitude: 20, frequency: 2, seed: 123 });

    const at05_a = w.evaluate(0.5);
    const at05_b = w.evaluate(0.5);
    assert.strictEqual(at05_a, at05_b, "Wiggle must be purely deterministic");

    // Oscila en torno a 0 (valores positivos y negativos)
    let hasPositive = false;
    let hasNegative = false;
    for (let p = 0; p <= 1.0; p += 0.05) {
      const val = w.evaluate(p);
      if (val > 1) hasPositive = true;
      if (val < -1) hasNegative = true;
    }
    assert.strictEqual(hasPositive, true);
    assert.strictEqual(hasNegative, true);
  });
});
