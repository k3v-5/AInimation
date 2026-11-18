import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { spring } from "../../../animation/motion/SpringMotion.js";

describe("Fase 3C — Analytical Spring Physics Tests", () => {
  it("satisfies boundary conditions: evaluate(0) = 0 and evaluate(1) = 1", () => {
    const s = spring({ preset: "bouncy" });
    assert.strictEqual(s.evaluate(0), 0);
    assert.strictEqual(s.evaluate(1), 1);
  });

  it("underdamped spring oscillates and exceeds 1.0 before settling", () => {
    const under = spring({ mass: 1, stiffness: 180, damping: 8 });
    let maxVal = 0;
    for (let p = 0; p <= 1.0; p += 0.02) {
      const val = under.evaluate(p);
      if (val > maxVal) maxVal = val;
    }
    assert.ok(maxVal > 1.1, `Underdamped spring must overshoot target > 1.1, got ${maxVal}`);
  });

  it("critically damped spring converges smoothly to 1.0 without excessive oscillations", () => {
    // mass = 1, stiffness = 100 -> omega0 = 10. damping = 2 * sqrt(1 * 100) = 20 -> zeta = 1.0
    const crit = spring({ mass: 1, stiffness: 100, damping: 20 });
    assert.strictEqual(crit.evaluate(0), 0);
    assert.strictEqual(crit.evaluate(1), 1);

    // Debe ser monotónicamente creciente hacia 1.0
    let prev = 0;
    for (let p = 0.1; p <= 1.0; p += 0.1) {
      const val = crit.evaluate(p);
      assert.ok(val >= prev, `Critically damped must be monotonically increasing: prev=${prev}, cur=${val}`);
      prev = val;
    }
  });

  it("DETERMINISM: spring evaluation produces 100% exact numerical match across repeated calls", () => {
    const s = spring({ preset: "snappy" });
    const timestamps = [0.1, 0.23, 0.456, 0.789];
    for (const t of timestamps) {
      const r1 = s.evaluate(t);
      const r2 = s.evaluate(t);
      assert.strictEqual(r1, r2, `Spring must be 100% deterministic at t=${t}`);
    }
  });
});
