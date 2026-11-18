import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { MaskPathGeometry } from "../../masks/core/MaskPathGeometry.js";
import { MaskStack } from "../../masks/core/MaskStack.js";
import { Mask } from "../../masks/types/index.js";
import { Tracker } from "../../tracking/core/Tracker.js";
import { TrackingSmoothing } from "../../tracking/core/TrackingSmoothing.js";

describe("Fase 5G — Masks, Rotoscoping & Tracking Benchmark Suite", () => {
  it("benchmarks evaluating 20 combined masks into a composite matte and smoothing 1,000 tracking samples", () => {
    // 1. Benchmark MaskStack con 20 máscaras
    const masks: Mask[] = [];
    for (let i = 0; i < 20; i++) {
      masks.push({
        id: `mask_${i}`,
        type: "rectangle",
        path: MaskPathGeometry.createRectanglePath(i * 10, i * 10, 50, 50),
        mode: i % 2 === 0 ? "add" : "intersect",
        feather: 2.0,
        expansion: 0.0,
        opacity: 1.0,
      });
    }

    const stack = new MaskStack(masks);
    const t0 = performance.now();
    const matte = stack.evaluateMatte(200, 200);
    const maskElapsed = performance.now() - t0;

    assert.strictEqual(matte.width, 200);
    assert.strictEqual(matte.height, 200);

    // 2. Benchmark Tracker con 1,000 muestras
    const tracker = new Tracker("bench_tr");
    for (let i = 0; i < 1000; i++) {
      tracker.addSample({
        time: i * 0.033,
        transform: {
          position: { x: 100 + Math.sin(i) * 5, y: 200 + Math.cos(i) * 5 },
          scale: { x: 1, y: 1 },
          rotation: i * 0.1,
        },
      });
    }

    const t1 = performance.now();
    const smoothed = TrackingSmoothing.smooth(tracker.data, { mode: "moving-average", windowSize: 5 });
    for (let f = 0; f < 500; f++) {
      tracker.evaluateAt((f / 500) * 30.0);
    }
    const trackElapsed = performance.now() - t1;

    assert.strictEqual(smoothed.samples.length, 1000);

    // Presupuesto: < 300ms para generación de matte y < 100ms para tracking
    assert.ok(maskElapsed < 300, `Matte generation took ${maskElapsed.toFixed(2)}ms (budget: <300ms)`);
    assert.ok(trackElapsed < 100, `Tracking smoothing & eval took ${trackElapsed.toFixed(2)}ms (budget: <100ms)`);
  });
});
