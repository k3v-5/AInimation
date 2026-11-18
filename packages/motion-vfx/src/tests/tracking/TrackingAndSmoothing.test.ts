import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Tracker } from "../../tracking/core/Tracker.js";
import { TrackingSmoothing } from "../../tracking/core/TrackingSmoothing.js";
import { TrackingData } from "../../tracking/types/index.js";

describe("Fase 5G — Motion Tracker & Smoothing Tests", () => {
  it("interpolates continuous transforms between tracking samples", () => {
    const tracker = new Tracker("tr_person");
    tracker.addSample({
      time: 0.0,
      transform: { position: { x: 100, y: 200 }, scale: { x: 1, y: 1 }, rotation: 0 },
    });
    tracker.addSample({
      time: 2.0,
      transform: { position: { x: 300, y: 400 }, scale: { x: 2, y: 2 }, rotation: 90 },
    });

    // En t = 1.0s (50%) -> pos=(200, 300), scale=(1.5, 1.5), rot=45
    const tf = tracker.evaluateAt(1.0);
    assert.strictEqual(tf.position.x, 200);
    assert.strictEqual(tf.position.y, 300);
    assert.strictEqual(tf.scale.x, 1.5);
    assert.strictEqual(tf.rotation, 45);
  });

  it("reduces jitter using moving-average and exponential smoothing", () => {
    // Datos con fluctuación de jitter: 100 -> 110 -> 90 -> 110 -> 100
    const rawData: TrackingData = {
      samples: [
        { time: 0, transform: { position: { x: 100, y: 0 }, scale: { x: 1, y: 1 }, rotation: 0 } },
        { time: 1, transform: { position: { x: 110, y: 0 }, scale: { x: 1, y: 1 }, rotation: 0 } },
        { time: 2, transform: { position: { x: 90, y: 0 }, scale: { x: 1, y: 1 }, rotation: 0 } },
        { time: 3, transform: { position: { x: 110, y: 0 }, scale: { x: 1, y: 1 }, rotation: 0 } },
        { time: 4, transform: { position: { x: 100, y: 0 }, scale: { x: 1, y: 1 }, rotation: 0 } },
      ],
    };

    const smoothedMA = TrackingSmoothing.smooth(rawData, { mode: "moving-average", windowSize: 3 });
    // En índice 2 (original = 90), media de [110, 90, 110] = 103.33
    assert.ok(smoothedMA.samples[2].transform.position.x > 90);

    const smoothedExp = TrackingSmoothing.smooth(rawData, { mode: "exponential", alpha: 0.5 });
    assert.strictEqual(smoothedExp.samples.length, 5);
  });
});
