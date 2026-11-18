import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { ProceduralMotion } from "../../graphics/motion/ProceduralMotion.js";

describe("Fase 5J — Procedural Motion, Trim Paths & Springs Tests", () => {
  it("calculates trim paths parametric span correctly", () => {
    const trim = { start: 0.1, end: 0.9, offset: 0.0 };
    // En progreso 0.5 (50%), span = (0.9 - 0.1) * 0.5 = 0.4 -> visibleStart = 0.1, visibleEnd = 0.5
    const res = ProceduralMotion.evaluateTrimPaths(0.5, trim);
    assert.strictEqual(Math.round(res.visibleStart * 100) / 100, 0.1);
    assert.strictEqual(Math.round(res.visibleEnd * 100) / 100, 0.5);
  });

  it("evaluates deterministic procedural noise and spring bounce", () => {
    const noise1 = ProceduralMotion.evaluateNoise(1.5, 999);
    const noise2 = ProceduralMotion.evaluateNoise(1.5, 999);
    assert.strictEqual(noise1, noise2);

    // Spring bounce at t=1.0 reaches 1.0
    const bounceEnd = ProceduralMotion.evaluateSpringBounce(1.0);
    assert.strictEqual(bounceEnd, 1.0);
  });
});
