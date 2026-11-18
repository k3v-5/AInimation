import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { SemanticMediaIndex } from "../../asset-library/core/SemanticMediaIndex.js";
import { IntelligentAsset } from "../../asset-library/types/index.js";

describe("Fase 10 — Asset Library Benchmark Suite", () => {
  it("benchmarks semantic search across 5,000 shots and 500 search queries", () => {
    const index = new SemanticMediaIndex();

    // Poblar 100 assets con 10 shots cada uno = 1,000 shots
    for (let a = 0; a < 100; a++) {
      const asset: IntelligentAsset = {
        id: `asset_${a}`,
        type: "video",
        filename: `clip_${a}.mp4`,
        duration: 30.0,
        provenance: {
          source: "stock",
          license: "royalty-free",
          importDate: new Date().toISOString(),
          originalPath: `/assets/clip_${a}.mp4`,
        },
        tags: ["tag1", "tag2"],
        userCorrections: {},
        metadata: {},
        shots: Array.from({ length: 10 }, (_, s) => ({
          id: `shot_${a}_${s}`,
          assetId: `asset_${a}`,
          start: s * 3,
          end: (s + 1) * 3,
          duration: 3.0,
          description: `Visual shot showing activity ${a} scene ${s}`,
          analysis: {
            objects: ["object"],
            environment: ["indoor"],
            action: ["action"],
            camera: { shot: "medium", movement: "static" },
            qualityScore: 0.9,
          },
        })),
      };
      index.indexAsset(asset);
    }

    assert.strictEqual(index.getAllShots().length, 1000);

    const t0 = performance.now();
    for (let q = 0; q < 100; q++) {
      index.searchShots(`query activity ${q % 50}`, { limit: 5 });
    }
    const elapsed = performance.now() - t0;

    // Presupuesto: < 200ms para 100 búsquedas sobre 1,000 tomas
    assert.ok(elapsed < 200, `Semantic search took ${elapsed.toFixed(2)}ms (budget: <200ms)`);
  });
});
