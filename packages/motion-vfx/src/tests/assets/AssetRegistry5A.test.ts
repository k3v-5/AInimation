import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AssetRegistry } from "../../assets/AssetRegistry.js";

describe("Fase 5A — Asset Registry & Operations Tests", () => {
  it("registers, retrieves, finds by name, and removes assets", () => {
    const registry = new AssetRegistry();

    registry.register({
      id: "asset_vid_01",
      type: "video",
      name: "dog.mp4",
      source: { path: "/media/dog.mp4" },
      metadata: { width: 1920, height: 1080, duration: 15, fps: 30 },
    });

    assert.strictEqual(registry.has("asset_vid_01"), true);
    assert.strictEqual(registry.get("asset_vid_01")?.name, "dog.mp4");

    const found = registry.findByName("dog.mp4");
    assert.strictEqual(found.length, 1);
    assert.strictEqual(found[0].id, "asset_vid_01");

    assert.strictEqual(registry.remove("asset_vid_01"), true);
    assert.strictEqual(registry.has("asset_vid_01"), false);
  });

  it("relinks asset path without mutating its assetId", () => {
    const registry = new AssetRegistry();
    registry.register({
      id: "asset_img_01",
      type: "image",
      name: "logo.png",
      source: { path: "/old/path/logo.png" },
      metadata: { width: 500, height: 500 },
    });

    registry.relink("asset_img_01", "/new/assets/brand_logo.png");

    const updated = registry.require("asset_img_01");
    assert.strictEqual(updated.id, "asset_img_01");
    assert.strictEqual(updated.source.path, "/new/assets/brand_logo.png");
  });

  it("accurately verifies if an asset is referenced by active elements", () => {
    const registry = new AssetRegistry();
    registry.register({
      id: "asset_bg",
      type: "image",
      source: { path: "/img/bg.png" },
    });

    const elements = [
      { id: "el_1", assetId: "asset_bg" },
      { id: "el_2", assetId: "other_asset" },
    ];

    assert.strictEqual(registry.isAssetReferenced("asset_bg", elements), true);
    assert.strictEqual(registry.isAssetReferenced("asset_unused", elements), false);
  });
});
