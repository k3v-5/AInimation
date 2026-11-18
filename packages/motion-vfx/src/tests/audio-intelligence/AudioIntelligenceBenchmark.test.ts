import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AudioEventStore } from "../../audio-intelligence/core/AudioEventStore.js";
import { AudioReactiveEngine } from "../../audio-intelligence/core/AudioReactiveEngine.js";
import { AudioSignal } from "../../audio-intelligence/core/AudioSignal.js";
import { Quantizer } from "../../audio-intelligence/core/Quantizer.js";
import { AudioBinding, BeatGrid } from "../../audio-intelligence/types/index.js";

describe("Fase 5I — Audio Intelligence Benchmark Suite", () => {
  it("benchmarks querying 5,000 events, evaluating 1,000 audio bindings and 1,000 quantizations", () => {
    // 1. Benchmark AudioEventStore con 5,000 eventos
    const store = new AudioEventStore();
    for (let i = 0; i < 5000; i++) {
      store.addEvent({
        id: `ev_${i}`,
        type: i % 2 === 0 ? "beat" : "word",
        time: i * 0.05,
        strength: (i % 10) / 10,
      });
    }

    const t0 = performance.now();
    for (let q = 0; q < 500; q++) {
      store.getBetween(q * 0.5, q * 0.5 + 2.0);
    }
    const queryElapsed = performance.now() - t0;

    // 2. Benchmark AudioSignal & Binding con 1,000 muestras
    const signal = new AudioSignal("bench_sig");
    for (let i = 0; i < 1000; i++) {
      signal.addSample(i * 0.033, Math.sin(i * 0.1) * 0.5 + 0.5);
    }

    const binding: AudioBinding = {
      id: "b_bench",
      signalName: "bench_sig",
      targetLayerId: "layer_1",
      targetProperty: "scale",
      mapping: {
        mode: "linear",
        inputRange: [0, 1],
        outputRange: [1, 2],
      },
      envelope: {
        attackTime: 0.05,
        releaseTime: 0.15,
      },
    };

    const t1 = performance.now();
    for (let f = 0; f < 500; f++) {
      AudioReactiveEngine.evaluateBinding(binding, signal, (f / 500) * 30.0);
    }
    const bindingElapsed = performance.now() - t1;

    // 3. Benchmark Quantizer con 1,000 puntos
    const grid: BeatGrid = { bpm: 128, offset: 0.1, subdivision: 4 };
    const t2 = performance.now();
    for (let p = 0; p < 1000; p++) {
      Quantizer.snap(p * 0.033, grid, "subdivision");
    }
    const snapElapsed = performance.now() - t2;

    assert.strictEqual(store.size, 5000);

    // Presupuesto: < 100ms para cada benchmark
    assert.ok(queryElapsed < 100, `Event querying took ${queryElapsed.toFixed(2)}ms (budget: <100ms)`);
    assert.ok(bindingElapsed < 100, `Binding evaluation took ${bindingElapsed.toFixed(2)}ms (budget: <100ms)`);
    assert.ok(snapElapsed < 100, `Quantization took ${snapElapsed.toFixed(2)}ms (budget: <100ms)`);
  });
});
