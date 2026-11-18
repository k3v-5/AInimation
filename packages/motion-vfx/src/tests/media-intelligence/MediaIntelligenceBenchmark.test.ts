import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AssetRepository } from "../../media-intelligence/core/AssetRepository.js";
import { BrollRanker } from "../../media-intelligence/core/BrollRanker.js";
import { EmbeddingService } from "../../media-intelligence/core/EmbeddingService.js";
import { Asset } from "../../media-intelligence/types/index.js";

describe("Fase 6 — Media Intelligence Benchmark Suite", () => {
  it("benchmarks importing 1,000 assets, 5,000 vector similarity checks and 500 B-roll rank queries", () => {
    // 1. Benchmark 1,000 assets en AssetRepository
    const repo = new AssetRepository();
    const t0 = performance.now();
    for (let i = 0; i < 1000; i++) {
      const asset: Asset = {
        id: `asset_${i}`,
        type: i % 2 === 0 ? "video" : "image",
        source: { uri: `/media/clip_${i}.mp4` },
        metadata: { filename: `clip_${i}.mp4`, mimeType: "video/mp4", duration: 10.0 },
        status: "available",
        tags: [`tag_${i % 10}`, "broll"],
        shots: [
          {
            id: `shot_${i}_0`,
            start: 0,
            end: 5,
            keyframes: [0, 1.25, 2.5, 3.75, 5],
            analysis: {
              objects: [{ label: i % 2 === 0 ? "person" : "car", bbox: { x: 0, y: 0, width: 50, height: 50 }, confidence: 0.9 }],
              quality: { sharpness: 0.9, exposure: 0.9, stability: 0.9, resolutionScore: 1, overall: 0.9 },
            },
          },
        ],
      };
      repo.create(asset);
    }
    const importElapsed = performance.now() - t0;

    // 2. Benchmark 5,000 cosine similarity evaluations
    const vA = EmbeddingService.generateDeterministicMockVector("apple");
    const vB = EmbeddingService.generateDeterministicMockVector("banana");
    const t1 = performance.now();
    for (let i = 0; i < 5000; i++) {
      EmbeddingService.cosineSimilarity(vA, vB);
    }
    const simElapsed = performance.now() - t1;

    // 3. Benchmark 500 B-roll rank queries
    const assetsSubset = repo.search({ type: "video" }).slice(0, 50);
    const t2 = performance.now();
    for (let i = 0; i < 500; i++) {
      BrollRanker.rankCandidates(assetsSubset, undefined, ["person"]);
    }
    const rankElapsed = performance.now() - t2;

    assert.strictEqual(repo.size, 1000);

    // Presupuesto: < 100ms para cada tarea
    assert.ok(importElapsed < 100, `Asset import took ${importElapsed.toFixed(2)}ms (budget: <100ms)`);
    assert.ok(simElapsed < 100, `Vector similarity took ${simElapsed.toFixed(2)}ms (budget: <100ms)`);
    assert.ok(rankElapsed < 100, `B-roll ranking took ${rankElapsed.toFixed(2)}ms (budget: <100ms)`);
  });
});
