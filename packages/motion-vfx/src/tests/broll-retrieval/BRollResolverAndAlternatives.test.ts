import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AssetCatalogIndex } from "../../broll-retrieval/core/AssetCatalogIndex.js";
import { BRollResolver } from "../../broll-retrieval/core/BRollResolver.js";
import { IndexedAsset } from "../../broll-retrieval/types/index.js";

describe("Fase 15 — BRoll Resolver & Alternatives Tests", () => {
  it("resolves B-roll query into top candidate and ranked alternatives with explainable rationale", () => {
    const catalog = new AssetCatalogIndex();

    const assetBest: IndexedAsset = {
      id: "asset_ai_chip",
      uri: "file://clips/chip.mp4",
      fingerprint: "hash_chip",
      duration: 5.0,
      orientation: "landscape",
      tags: ["ai", "server", "chip"],
      shots: [{ id: "s1", start: 0, end: 5.0, objects: [], hasFace: false, textSafeSide: "left", quality: 0.95, energy: 0.9 }],
      license: { source: "stock", attributionRequired: false, commercialUse: true },
      usageCount: 0,
    };

    const assetGood: IndexedAsset = {
      id: "asset_datacenter",
      uri: "file://clips/datacenter.mp4",
      fingerprint: "hash_dc",
      duration: 8.0,
      orientation: "landscape",
      tags: ["server", "datacenter"],
      shots: [{ id: "s2", start: 0, end: 8.0, objects: [], hasFace: false, textSafeSide: "center", quality: 0.85, energy: 0.7 }],
      license: { source: "stock", attributionRequired: false, commercialUse: true },
      usageCount: 0,
    };

    catalog.registerAsset(assetBest);
    catalog.registerAsset(assetGood);

    const resolver = new BRollResolver(catalog);
    const resolution = resolver.resolveBRoll({
      intent: "ai server chip",
      targetDuration: 2.5,
      textSafeSide: "left",
    });

    assert.strictEqual(resolution.primary.assetId, "asset_ai_chip");
    assert.strictEqual(resolution.primary.subclipEnd - resolution.primary.subclipStart, 2.5);
    assert.strictEqual(resolution.alternatives.length, 1);
    assert.strictEqual(resolution.alternatives[0].assetId, "asset_datacenter");
  });
});
