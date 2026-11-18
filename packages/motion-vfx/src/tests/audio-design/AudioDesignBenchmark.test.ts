import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { SemanticSFXLibrary } from "../../audio-design/core/SemanticSFXLibrary.js";
import { SmartDuckingEngine } from "../../audio-design/core/SmartDuckingEngine.js";
import { SyncEventGraph } from "../../audio-design/core/SyncEventGraph.js";
import { DuckingRule, SpeechRegion } from "../../audio-design/types/index.js";

describe("Fase 13 — Audio & Sound Design Benchmark Suite", () => {
  it("benchmarks 10,000 ducking evaluations, 1,000 SFX queries and 500 sync group queries", () => {
    const rule: DuckingRule = {
      voiceTrackId: "v",
      musicTrackId: "m",
      duckedVolume: 0.2,
      normalVolume: 1.0,
      attackDuration: 0.2,
      releaseDuration: 0.4,
    };
    const speechRegions: SpeechRegion[] = [
      { start: 1.0, end: 3.0, confidence: 0.9 },
      { start: 5.0, end: 8.0, confidence: 0.9 },
    ];

    // 1. Benchmark 10,000 Ducking Envelope Calculations
    const t0 = performance.now();
    for (let i = 0; i < 10000; i++) {
      SmartDuckingEngine.evaluateDuckingGain(speechRegions, rule, (i % 100) * 0.1);
    }
    const duckElapsed = performance.now() - t0;

    // 2. Benchmark 1,000 SFX Queries
    const t1 = performance.now();
    for (let i = 0; i < 1000; i++) {
      SemanticSFXLibrary.findSFX({ intent: "punch", category: "impact" });
    }
    const sfxElapsed = performance.now() - t1;

    // 3. Benchmark 500 Sync Group Queries
    const graph = new SyncEventGraph();
    for (let i = 0; i < 50; i++) {
      graph.createSyncGroup(`g_${i}`, i * 0.5, "Event", [
        { time: i * 0.5, type: "impact", strength: 0.9, source: "audio" },
      ]);
    }

    const t2 = performance.now();
    for (let i = 0; i < 500; i++) {
      graph.getEventsAt((i % 50) * 0.5);
    }
    const syncElapsed = performance.now() - t2;

    // Presupuestos: < 100ms para cada tarea
    assert.ok(duckElapsed < 100, `Ducking eval took ${duckElapsed.toFixed(2)}ms (budget: <100ms)`);
    assert.ok(sfxElapsed < 100, `SFX query took ${sfxElapsed.toFixed(2)}ms (budget: <100ms)`);
    assert.ok(syncElapsed < 100, `Sync group eval took ${syncElapsed.toFixed(2)}ms (budget: <100ms)`);
  });
});
