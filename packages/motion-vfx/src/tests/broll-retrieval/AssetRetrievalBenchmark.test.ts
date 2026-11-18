import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AssetCatalogIndex } from "../../broll-retrieval/core/AssetCatalogIndex.js";
import { AssetRankingEngine } from "../../broll-retrieval/core/AssetRankingEngine.js";
import { SubclipOptimizer } from "../../broll-retrieval/core/SubclipOptimizer.js";
import { IndexedAsset } from "../../broll-retrieval/types/index.js";

describe("Fase 15 — Asset Retrieval Benchmark Suite", () => {
  it("benchmarks 1,000 queries, 500 subclip optimizations and 500 duplicate checks", () => {
    const catalog = new AssetCatalogIndex();
    for (let i = 0; i < 50; i++) {
      catalog.registerAsset({
        id: `asset_${i}`,
        uri: `file://clips/clip_${i}.mp4`,
        fingerprint: `hash_${i}`,
        duration: 10.0 + i,
        orientation: i % 2 === 0 ? "landscape" : "portrait",
        tags: ["tech", "server", "code", `tag_${i}`],
        shots: [{ id: `s_${i}`, start: 0, end: 5.0, objects: [], hasFace: false, textSafeSide: "left", quality: 0.9, energy: 0.8 }],
        license: { source: "stock", attributionRequired: false, commercialUse: true },
        usageCount: i % 3,
      });
    }

    const testAsset = catalog.getAsset("asset_0")!;

    // 1. Benchmark 1,000 Asset Scoring Computations
    const t0 = performance.now();
    for (let i = 0; i < 1000; i++) {
      AssetRankingEngine.scoreAsset(testAsset, { intent: "server code", targetDuration: 3.0, textSafeSide: "left" });
    }
    const scoreElapsed = performance.now() - t0;

    // 2. Benchmark 500 Subclip Optimizations
    const t1 = performance.now();
    for (let i = 0; i < 500; i++) {
      SubclipOptimizer.findBestSubclip(testAsset, 2.5);
    }
    const subclipElapsed = performance.now() - t1;

    // 3. Benchmark 500 Duplicate Checks
    const t2 = performance.now();
    for (let i = 0; i < 500; i++) {
      catalog.findDuplicate(`hash_${i % 50}`);
    }
    const dupElapsed = performance.now() - t2;

    // Presupuestos: < 100ms para cada tarea
    assert.ok(scoreElapsed < 100, `Asset scoring took ${scoreElapsed.toFixed(2)}ms (budget: <100ms)`);
    assert.ok(subclipElapsed < 100, `Subclip optimizer took ${subclipElapsed.toFixed(2)}ms (budget: <100ms)`);
    assert.ok(dupElapsed < 100, `Duplicate check took ${dupElapsed.toFixed(2)}ms (budget: <100ms)`);
  });
});
