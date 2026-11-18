import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { TrackProcessor } from "../../tracking-rotoscopy/core/TrackProcessor.js";
import { Track } from "../../tracking-rotoscopy/types/index.js";

describe("Fase 12 — Track Processor & Smoothing Tests", () => {
  it("interpolates position accurately between discrete track keyframes", () => {
    const track: Track = {
      id: "track_laptop",
      targetType: "object",
      semanticClass: "laptop",
      start: 0,
      end: 2.0,
      confidence: 0.95,
      state: "active",
      samples: [
        { time: 0, position: { x: 100, y: 200 }, confidence: 0.95 },
        { time: 1.0, position: { x: 200, y: 400 }, confidence: 0.95 },
        { time: 2.0, position: { x: 300, y: 600 }, confidence: 0.95 },
      ],
    };

    // t=0.5 -> x=150, y=300
    const pos = TrackProcessor.evaluatePosition(track, 0.5);
    assert.strictEqual(pos !== undefined, true);
    assert.strictEqual(pos?.x, 150);
    assert.strictEqual(pos?.y, 300);
  });

  it("smooths noisy samples reducing jitter variance", () => {
    const noisySamples = [
      { time: 0, position: { x: 100, y: 100 }, confidence: 0.9 },
      { time: 0.1, position: { x: 120, y: 100 }, confidence: 0.9 }, // Jitter pico
      { time: 0.2, position: { x: 105, y: 100 }, confidence: 0.9 },
    ];

    const smoothed = TrackProcessor.smoothSamples(noisySamples, 0.5);
    assert.strictEqual(smoothed.length, 3);
    assert.strictEqual(smoothed[0].position?.x, 100);
    // (0.5 * 120 + 0.5 * 100) = 110 (menor que el pico 120)
    assert.strictEqual(smoothed[1].position?.x, 110);
  });
});
