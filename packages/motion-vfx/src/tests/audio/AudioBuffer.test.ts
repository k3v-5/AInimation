import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AudioBuffer } from "../../audio/core/AudioBuffer.js";

describe("Fase 5D — AudioBuffer Slicing, Gain & Resampling Tests", () => {
  it("creates, clones, slices, and scales gain on AudioBuffer", () => {
    const buffer = AudioBuffer.create(2, 48000, 48000); // 1 second stereo
    buffer.data[0].fill(0.5);
    buffer.data[1].fill(0.5);

    assert.strictEqual(buffer.duration, 1.0);
    assert.strictEqual(buffer.frames, 48000);

    // Aplicar ganancia 2.0 -> 1.0
    buffer.applyGain(2.0);
    assert.strictEqual(buffer.data[0][0], 1.0);

    // Slicing de 0.5s
    const sliced = buffer.slice(0, 24000);
    assert.strictEqual(sliced.duration, 0.5);
    assert.strictEqual(sliced.frames, 24000);
  });

  it("resamples buffer from 44100 Hz to 48000 Hz preserving duration", () => {
    const src = AudioBuffer.create(1, 44100, 44100); // 1 second
    src.data[0].fill(0.75);

    const resampled = src.resample(48000);
    assert.strictEqual(resampled.sampleRate, 48000);
    assert.strictEqual(resampled.frames, 48000);
    assert.strictEqual(resampled.duration, 1.0);
    assert.ok(Math.abs(resampled.data[0][1000] - 0.75) < 1e-4);
  });
});
