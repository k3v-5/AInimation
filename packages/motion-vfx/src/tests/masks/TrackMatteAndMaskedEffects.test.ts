import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { TrackMatte } from "../../masks/core/TrackMatte.js";

describe("Fase 5G — Track Matte (Alpha & Alpha-Inverted) Tests", () => {
  it("applies alpha and alpha-inverted track matte compositing accurately", () => {
    const srcAlpha = new Float32Array([1.0, 1.0, 0.5, 0.0]);
    const matteAlpha = new Float32Array([1.0, 0.0, 0.5, 1.0]);

    // Alpha mode: src * matte
    const resultAlpha = TrackMatte.applyTrackMatte(srcAlpha, matteAlpha, "alpha");
    assert.strictEqual(resultAlpha[0], 1.0); // 1.0 * 1.0 = 1.0
    assert.strictEqual(resultAlpha[1], 0.0); // 1.0 * 0.0 = 0.0
    assert.strictEqual(resultAlpha[2], 0.25); // 0.5 * 0.5 = 0.25
    assert.strictEqual(resultAlpha[3], 0.0); // 0.0 * 1.0 = 0.0

    // Alpha-inverted mode: src * (1 - matte)
    const resultInverted = TrackMatte.applyTrackMatte(srcAlpha, matteAlpha, "alpha-inverted");
    assert.strictEqual(resultInverted[0], 0.0); // 1.0 * (1 - 1.0) = 0.0
    assert.strictEqual(resultInverted[1], 1.0); // 1.0 * (1 - 0.0) = 1.0
    assert.strictEqual(resultInverted[2], 0.25); // 0.5 * (1 - 0.5) = 0.25
  });
});
