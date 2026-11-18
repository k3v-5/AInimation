import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { ShotDetector } from "../../media-intelligence/core/ShotDetector.js";

describe("Fase 6 — Shot Detection & Keyframe Extraction Tests", () => {
  it("segments continuous media into shots and extracts 5 canonical keyframes", () => {
    const cuts = [3.0, 7.0]; // Cortes en 3s y 7s para video de 10s -> 3 tomas: [0-3], [3-7], [7-10]
    const shots = ShotDetector.createShotsFromCuts("video_01", cuts, 10.0);

    assert.strictEqual(shots.length, 3);
    assert.strictEqual(shots[0].start, 0.0);
    assert.strictEqual(shots[0].end, 3.0);
    assert.strictEqual(shots[0].keyframes.length, 5);

    // Keyframes de la toma [0, 3]: 0, 0.75, 1.5, 2.25, 3.0
    assert.strictEqual(shots[0].keyframes[0], 0.0);
    assert.strictEqual(shots[0].keyframes[2], 1.5);
    assert.strictEqual(shots[0].keyframes[4], 3.0);
  });
});
