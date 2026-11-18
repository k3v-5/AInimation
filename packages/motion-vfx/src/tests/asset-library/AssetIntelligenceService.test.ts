import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AssetIntelligenceService } from "../../asset-library/core/AssetIntelligenceService.js";
import { IntelligentAsset } from "../../asset-library/types/index.js";

describe("Fase 10 — Asset Intelligence Service Tests", () => {
  it("provides findBestVisual query, records user corrections and detects duplicates", () => {
    const service = new AssetIntelligenceService();

    const asset1: IntelligentAsset = {
      id: "asset_laptop_01",
      type: "video",
      filename: "laptop_typing.mp4",
      duration: 8.0,
      provenance: {
        source: "local",
        license: "royalty-free",
        importDate: new Date().toISOString(),
        originalPath: "/assets/laptop_typing.mp4",
      },
      tags: ["office", "laptop"],
      userCorrections: {},
      metadata: { sha256: "hash_abc_123" },
      shots: [
        {
          id: "shot_lap_01",
          assetId: "asset_laptop_01",
          start: 0,
          end: 4.0,
          duration: 4.0,
          description: "Person working on a sleek modern laptop",
          analysis: {
            objects: ["laptop", "hands"],
            environment: ["office"],
            action: ["typing"],
            camera: { shot: "medium", movement: "static" },
            qualityScore: 0.96,
          },
        },
      ],
    };

    service.registerAsset(asset1);

    // 1. findBestVisual
    const best = service.findBestVisual({
      concept: "working on laptop",
      duration: 3.0,
    });
    assert.strictEqual(best !== undefined, true);
    assert.strictEqual(best?.shot.id, "shot_lap_01");

    // 2. recordUserCorrection
    service.recordUserCorrection("asset_laptop_01", "office", "home-office");
    const updated = service.getAsset("asset_laptop_01")!;
    assert.strictEqual(updated.tags.includes("home-office"), true);
    assert.strictEqual(updated.userCorrections["office"], "home-office");

    // 3. Duplicate detection
    const assetCopy: IntelligentAsset = {
      ...asset1,
      id: "asset_laptop_copy",
      filename: "laptop_typing_copy.mp4",
    };
    service.registerAsset(assetCopy);
    const duplicates = service.detectDuplicates("asset_laptop_01");
    assert.strictEqual(duplicates.length, 1);
    assert.strictEqual(duplicates[0].duplicateAssetId, "asset_laptop_copy");
  });
});
