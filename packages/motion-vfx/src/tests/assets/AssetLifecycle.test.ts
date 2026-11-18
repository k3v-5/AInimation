import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AssetImporter } from "../../assets/importer/AssetImporter.js";
import { AssetRegistry } from "../../assets/AssetRegistry.js";

describe("Fase 5A — Asset Lifecycle & Importer Tests", () => {
  it("imports and detects asset types correctly from extensions", () => {
    const vid = AssetImporter.importFromPath("media/intro.mp4");
    assert.strictEqual(vid.type, "video");
    assert.strictEqual((vid.metadata as any).fps, 30);

    const img = AssetImporter.importFromPath("assets/photo.jpg");
    assert.strictEqual(img.type, "image");

    const aud = AssetImporter.importFromPath("audio/music.mp3");
    assert.strictEqual(aud.type, "audio");

    const font = AssetImporter.importFromPath("fonts/Roboto.ttf");
    assert.strictEqual(font.type, "font");

    const svg = AssetImporter.importFromPath("graphics/logo.svg");
    assert.strictEqual(svg.type, "svg");
  });

  it("handles missing assets lifecycle transitions gracefully", () => {
    const registry = new AssetRegistry();
    const asset = AssetImporter.importFromPath("missing_file.mp4");
    asset.status = "missing";

    registry.register(asset);
    assert.strictEqual(registry.require(asset.id).status, "missing");

    // Relink back to ready
    registry.relink(asset.id, "found_file.mp4");
    assert.strictEqual(registry.require(asset.id).status, "ready");
    assert.strictEqual(registry.require(asset.id).source.path, "found_file.mp4");
  });
});
