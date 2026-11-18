import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AssetCatalogIndex } from "../../broll-retrieval/core/AssetCatalogIndex.js";
import { IndexedAsset } from "../../broll-retrieval/types/index.js";

describe("Fase 15 — Multimodal Index & Candidate Search Tests", () => {
  it("filters asset candidates matching intent and avoids blacklisted asset IDs", () => {
    const catalog = new AssetCatalogIndex();

    const serverAsset: IndexedAsset = {
      id: "asset_server",
      uri: "file://clips/server.mp4",
      fingerprint: "hash_server",
      duration: 6.0,
      orientation: "landscape",
      tags: ["server", "datacenter"],
      shots: [],
      license: { source: "stock", attributionRequired: false, commercialUse: true },
      usageCount: 0,
    };

    const natureAsset: IndexedAsset = {
      id: "asset_nature",
      uri: "file://clips/nature.mp4",
      fingerprint: "hash_nature",
      duration: 5.0,
      orientation: "landscape",
      tags: ["forest", "trees"],
      shots: [],
      license: { source: "stock", attributionRequired: false, commercialUse: true },
      usageCount: 0,
    };

    catalog.registerAsset(serverAsset);
    catalog.registerAsset(natureAsset);

    // 1. Buscar servidor
    const candidates = catalog.filterCandidates({
      intent: "server room",
      targetDuration: 3.0,
    });
    assert.strictEqual(candidates.length, 1);
    assert.strictEqual(candidates[0].id, "asset_server");

    // 2. Buscar servidor evitando asset_server
    const emptyCandidates = catalog.filterCandidates({
      intent: "server room",
      targetDuration: 3.0,
      avoidAssetIds: ["asset_server"],
    });
    assert.strictEqual(emptyCandidates.length, 0);
  });
});
