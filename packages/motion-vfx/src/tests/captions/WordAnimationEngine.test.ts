import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { WordAnimationEngine } from "../../captions/animations/WordAnimationEngine.js";

describe("Fase 16 — Word Animation Engine Mathematical Tests", () => {
  it("evaluates PopScale with correct boundaries, overshoot and clamping", () => {
    const start = 1.0;
    const end = 2.0;

    // Antes del intervalo
    assert.equal(WordAnimationEngine.evaluatePopScale(0.5, start, end), 1.0);
    assert.equal(WordAnimationEngine.evaluatePopScale(start, start, end), 1.0);

    // En el punto de máximo overshoot (alrededor de tau ~ 0.25 - 0.35)
    const peakScale = WordAnimationEngine.evaluatePopScale(1.3, start, end, { type: "popScale", intensity: 1.0 });
    assert.ok(peakScale > 1.15, `Peak scale should overshoot > 1.15, got ${peakScale}`);

    // Al final y después del intervalo
    assert.equal(WordAnimationEngine.evaluatePopScale(2.0, start, end), 1.0);
    assert.equal(WordAnimationEngine.evaluatePopScale(2.5, start, end), 1.0);

    // Con intensidad 0 o duración <= 0
    assert.equal(WordAnimationEngine.evaluatePopScale(1.3, start, end, { type: "popScale", intensity: 0 }), 1.0);
    assert.equal(WordAnimationEngine.evaluatePopScale(1.0, 1.0, 1.0), 1.0);
  });

  it("evaluates GlowPulse with sinusoidal decay and boundary safety", () => {
    const start = 2.0;
    const end = 3.0;

    const before = WordAnimationEngine.evaluateGlowPulse(1.5, start, end);
    assert.equal(before.active, false);
    assert.equal(before.intensity, 0);

    const mid = WordAnimationEngine.evaluateGlowPulse(2.5, start, end, { type: "glowPulse", intensity: 0.9 });
    assert.equal(mid.active, true);
    assert.ok(mid.intensity > 0.8);
    assert.ok(mid.radius > 15);

    const after = WordAnimationEngine.evaluateGlowPulse(3.5, start, end);
    assert.equal(after.active, false);
    assert.equal(after.intensity, 0);
  });

  it("evaluates ColorHighlight smoothly across inactive, active and completed states", () => {
    const start = 0.0;
    const end = 1.0;
    const inactive = { r: 0.5, g: 0.5, b: 0.5, a: 1 };
    const highlight = { r: 1, g: 1, b: 0, a: 1 }; // Amarillo
    const completed = { r: 1, g: 1, b: 1, a: 1 }; // Blanco

    const cBefore = WordAnimationEngine.evaluateColorHighlight(-0.5, start, end, inactive, highlight, completed);
    assert.deepEqual(cBefore, inactive);

    const cMid = WordAnimationEngine.evaluateColorHighlight(0.5, start, end, inactive, highlight, completed);
    assert.ok(cMid.r > 0.7);
    assert.ok(cMid.g > 0.7);

    const cAfter = WordAnimationEngine.evaluateColorHighlight(1.5, start, end, inactive, highlight, completed);
    assert.deepEqual(cAfter, completed);
  });

  it("evaluates Shake deterministically with seed reproducibility", () => {
    const start = 1.0;
    const end = 2.0;
    const config1 = { type: "shake" as const, seed: 12345, intensity: 1.0 };
    const config2 = { type: "shake" as const, seed: 12345, intensity: 1.0 };
    const configDiff = { type: "shake" as const, seed: 99999, intensity: 1.0 };

    // Repetibilidad determinista: misma semilla y mismo timestamp produce exactamente el mismo offset
    const shakeA = WordAnimationEngine.evaluateShake(1.4, start, end, config1);
    const shakeB = WordAnimationEngine.evaluateShake(1.4, start, end, config2);
    assert.deepEqual(shakeA, shakeB);

    // Semilla diferente produce valor distinto
    const shakeC = WordAnimationEngine.evaluateShake(1.4, start, end, configDiff);
    assert.notDeepEqual(shakeA, shakeC);

    // Fuera de rango devuelve offset nulo (0, 0)
    assert.deepEqual(WordAnimationEngine.evaluateShake(0.5, start, end, config1), { x: 0, y: 0 });
    assert.deepEqual(WordAnimationEngine.evaluateShake(2.5, start, end, config1), { x: 0, y: 0 });
  });
});
