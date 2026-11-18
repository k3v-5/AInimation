import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AudioMath } from "../../audio/core/AudioMath.js";

describe("Fase 5D — Audio Math & Acoustic Conversions Tests", () => {
  it("converts between decibels and linear gain precisely", () => {
    // 0 dB -> 1.0
    assert.strictEqual(AudioMath.dbToGain(0), 1.0);
    assert.strictEqual(AudioMath.gainToDb(1.0), 0.0);

    // -6 dB -> ~0.501187
    assert.ok(Math.abs(AudioMath.dbToGain(-6) - 0.501187) < 1e-5);
    // +6 dB -> ~1.995262
    assert.ok(Math.abs(AudioMath.dbToGain(6) - 1.995262) < 1e-5);

    // 0 gain -> -120 dB practical floor
    assert.strictEqual(AudioMath.gainToDb(0), -120);
  });

  it("calculates stereo equal-power pan coefficients", () => {
    // Center pan (0) -> left = right = sqrt(2)/2 ~= 0.7071
    const center = AudioMath.calculateStereoPan(0);
    assert.ok(Math.abs(center.left - Math.SQRT1_2) < 1e-6);
    assert.ok(Math.abs(center.right - Math.SQRT1_2) < 1e-6);

    // Hard Left (-1) -> left = 1, right = 0
    const left = AudioMath.calculateStereoPan(-1);
    assert.ok(Math.abs(left.left - 1.0) < 1e-6);
    assert.ok(Math.abs(left.right - 0.0) < 1e-6);

    // Hard Right (+1) -> left = 0, right = 1
    const right = AudioMath.calculateStereoPan(1);
    assert.ok(Math.abs(right.left - 0.0) < 1e-6);
    assert.ok(Math.abs(right.right - 1.0) < 1e-6);
  });

  it("applies soft limiter to compress excessive amplitudes", () => {
    // Under threshold -> unaltered
    assert.strictEqual(AudioMath.softLimit(0.5, 0.95), 0.5);
    // Over threshold -> smoothly compressed without exceeding 1.0
    const limited = AudioMath.softLimit(1.5, 0.95);
    assert.ok(limited <= 1.0);
    assert.ok(limited >= 0.95);
  });
});
