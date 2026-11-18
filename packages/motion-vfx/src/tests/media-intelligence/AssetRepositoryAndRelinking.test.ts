import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AssetRepository } from "../../media-intelligence/core/AssetRepository.js";
import { Asset } from "../../media-intelligence/types/index.js";

describe("Fase 6 — Asset Repository, Smart Collections & Relinking Tests", () => {
  it("manages asset CRUD, evaluates smart collections and relinks missing assets", () => {
    const repo = new AssetRepository();

    const logoAsset: Asset = {
      id: "logo_01",
      type: "graphic",
      source: { uri: "/assets/logo.svg", checksum: "hash_logo_123" },
      metadata: { filename: "logo.svg", mimeType: "graphic/svg", width: 512, height: 512 },
      status: "available",
      tags: ["brand", "vector", "logo"],
    };

    repo.create(logoAsset);
    assert.strictEqual(repo.size, 1);

    // Smart collection por tag 'brand'
    repo.addSmartCollection({
      id: "col_brand",
      name: "Brand Assets",
      query: { tags: ["brand"] },
    });

    const brandAssets = repo.getSmartCollectionResults("col_brand");
    assert.strictEqual(brandAssets.length, 1);
    assert.strictEqual(brandAssets[0].id, "logo_01");

    // Marcar como missing y relinkear
    logoAsset.status = "missing";
    repo.update(logoAsset);
    assert.strictEqual(repo.get("logo_01")?.status, "missing");

    const relinkSuccess = repo.relink("logo_01", "/new_path/brand_logo.svg");
    assert.strictEqual(relinkSuccess, true);
    assert.strictEqual(repo.get("logo_01")?.status, "available");
    assert.strictEqual(repo.get("logo_01")?.source.uri, "/new_path/brand_logo.svg");
  });
});
