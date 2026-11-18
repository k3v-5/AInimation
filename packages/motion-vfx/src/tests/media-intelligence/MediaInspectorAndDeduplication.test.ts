import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { ChecksumService } from "../../media-intelligence/core/ChecksumService.js";
import { MediaInspector } from "../../media-intelligence/core/MediaInspector.js";

describe("Fase 6 — Media Inspector & Deduplication Tests", () => {
  it("infers asset type and creates default metadata from source URI", () => {
    const metaVideo = MediaInspector.createDefaultMetadata({ uri: "/media/broll_car.mp4" });
    assert.strictEqual(metaVideo.filename, "broll_car.mp4");
    assert.strictEqual(MediaInspector.inferTypeFromFilename("broll_car.mp4"), "video");
    assert.strictEqual(metaVideo.width, 1920);

    const metaAudio = MediaInspector.createDefaultMetadata({ uri: "/audio/voiceover.mp3" });
    assert.strictEqual(MediaInspector.inferTypeFromFilename("voiceover.mp3"), "audio");
    assert.strictEqual(metaAudio.sampleRate, 48000);
  });

  it("computes SHA-256 hash and deduplicates identical files", () => {
    ChecksumService.clear();

    const hash1 = ChecksumService.computeSHA256("video_content_bytes_12345");
    const hash2 = ChecksumService.computeSHA256("video_content_bytes_12345");
    assert.strictEqual(hash1, hash2);

    ChecksumService.registerAsset(hash1, "asset_canonical_1");
    // Registro duplicado no debe sobreescribir el ID canónico
    ChecksumService.registerAsset(hash1, "asset_duplicate_2");

    assert.strictEqual(ChecksumService.findCanonicalAssetId(hash1), "asset_canonical_1");
  });
});
