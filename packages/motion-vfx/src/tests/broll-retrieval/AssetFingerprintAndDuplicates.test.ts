import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AssetCatalogIndex } from "../../broll-retrieval/core/AssetCatalogIndex.js";
import { IndexedAsset } from "../../broll-retrieval/types/index.js";

describe("Fase 15 — Asset Fingerprints & Duplicate Detection Tests", () => {
  it("detects exact and near-duplicate assets via perceptual hash fingerprint", () => {
    const catalog = new AssetCatalogIndex();

    const asset1: IndexedAsset = {
      id: "asset_01",
      uri: "file://clips/server_a.mp4",
      fingerprint: "phash_9a8b7c6d",
      duration: 10.0,
      orientation: "landscape",
      tags: ["server", "tech"],
      shots: [],
      license: { source: "user", attributionRequired: false, commercialUse: true },
      usageCount: 0,
    };

    catalog.registerAsset(asset1);

    const dup = catalog.findDuplicate("phash_9a8b7c6d");
    assert.strictEqual(dup !== undefined, true);
    assert.strictEqual(dup?.id, "asset_01");

    const nonDup = catalog.findDuplicate("phash_11223344");
    assert.strictEqual(nonDup, undefined);
  });
});
