import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { RotoMaskEngine } from "../../tracking-rotoscopy/core/RotoMaskEngine.js";
import { SemanticTargetResolver } from "../../tracking-rotoscopy/core/SemanticTargetResolver.js";
import { TrackProcessor } from "../../tracking-rotoscopy/core/TrackProcessor.js";
import { RotoMask, Track } from "../../tracking-rotoscopy/types/index.js";

describe("Fase 12 — Tracking & Rotoscopy Benchmark Suite", () => {
  it("benchmarks 10,000 position evaluations, 1,000 mask alpha evaluations and 500 semantic resolutions", () => {
    const track: Track = {
      id: "track_bench",
      targetType: "object",
      semanticClass: "bench_target",
      start: 0,
      end: 10.0,
      confidence: 0.99,
      state: "active",
      samples: Array.from({ length: 100 }, (_, i) => ({
        time: i * 0.1,
        position: { x: i * 10, y: i * 5 },
        confidence: 0.99,
      })),
    };

    // 1. Benchmark 10,000 position interpolations
    const t0 = performance.now();
    for (let i = 0; i < 10000; i++) {
      TrackProcessor.evaluatePosition(track, (i % 100) * 0.1);
    }
    const posElapsed = performance.now() - t0;

    // 2. Benchmark 1,000 mask alpha evaluations
    const mask: RotoMask = { id: "m1", trackId: "track_bench", feather: 15, opacity: 1.0, invert: false };
    const t1 = performance.now();
    for (let i = 0; i < 1000; i++) {
      RotoMaskEngine.evaluateMaskAlpha(mask, (i % 50) - 25);
    }
    const maskElapsed = performance.now() - t1;

    // 3. Benchmark 500 semantic target resolutions
    const trackPool: Track[] = Array.from({ length: 50 }, (_, i) => ({
      id: `track_${i}`,
      targetType: "object",
      semanticClass: i % 2 === 0 ? "laptop" : "person",
      role: i === 10 ? "main_subject" : "secondary_subject",
      start: 0,
      end: 5.0,
      confidence: 0.9,
      state: "active",
      samples: [],
    }));

    const t2 = performance.now();
    for (let i = 0; i < 500; i++) {
      SemanticTargetResolver.resolveTarget(trackPool, { semanticClass: "laptop" });
    }
    const resElapsed = performance.now() - t2;

    // Presupuestos: < 100ms para cada tarea
    assert.ok(posElapsed < 100, `Track position eval took ${posElapsed.toFixed(2)}ms (budget: <100ms)`);
    assert.ok(maskElapsed < 100, `Mask alpha eval took ${maskElapsed.toFixed(2)}ms (budget: <100ms)`);
    assert.ok(resElapsed < 100, `Target resolve took ${resElapsed.toFixed(2)}ms (budget: <100ms)`);
  });
});
