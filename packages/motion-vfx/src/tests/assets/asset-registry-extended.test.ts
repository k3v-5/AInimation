import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AssetRegistry } from "../../assets/index.js";
import { ValidationError } from "../../errors/index.js";

describe("Fase 2A — Extended Asset Registry Tests", () => {
  it("filters assets by type using getByType()", () => {
    const reg = new AssetRegistry();
    reg.add({ id: "img1", type: "image", source: { path: "1.png" }, metadata: { mimeType: "image/png" } });
    reg.add({ id: "img2", type: "image", source: { path: "2.jpg" }, metadata: { mimeType: "image/jpeg" } });
    reg.add({ id: "vid1", type: "video", source: { path: "1.mp4" }, metadata: { mimeType: "video/mp4" } });
    reg.add({ id: "aud1", type: "audio", source: { path: "1.mp3" }, metadata: { mimeType: "audio/mpeg" } });

    assert.strictEqual(reg.size, 4);
    assert.strictEqual(reg.getByType("image").length, 2);
    assert.strictEqual(reg.getByType("video").length, 1);
    assert.strictEqual(reg.getByType("audio").length, 1);
  });

  it("validates metadata dimensions and duration ranges strictly", () => {
    const reg = new AssetRegistry();

    // Imagen con ancho negativo debe fallar
    assert.throws(() => {
      reg.add({ id: "bad_img", type: "image", source: { path: "bad.png" }, metadata: { width: -100, height: 200 } });
    }, ValidationError);

    // Video con duración 0 o negativa debe fallar
    assert.throws(() => {
      reg.add({ id: "bad_vid", type: "video", source: { path: "bad.mp4" }, metadata: { width: 1920, height: 1080, duration: 0, fps: 30 } });
    }, ValidationError);

    // Audio con sampleRate negativo debe fallar
    assert.throws(() => {
      reg.add({ id: "bad_aud", type: "audio", source: { path: "bad.mp3" }, metadata: { duration: 10, sampleRate: -44100 } });
    }, ValidationError);
  });
});
