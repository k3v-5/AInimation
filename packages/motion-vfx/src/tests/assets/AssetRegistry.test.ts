import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AssetRegistry } from "../../assets/AssetRegistry.js";
import { AssetNotFoundError, ValidationError } from "../../errors/index.js";

describe("Fase 2A — AssetRegistry Operations Tests", () => {
  it("adds, gets, requires, checks presence and lists assets", () => {
    const reg = new AssetRegistry();

    const videoAsset = {
      id: "main_video",
      type: "video" as const,
      source: { path: "assets/video.mp4" },
      metadata: { width: 1920, height: 1080, duration: 60, fps: 30 },
    };

    reg.add(videoAsset);

    assert.strictEqual(reg.has("main_video"), true);
    assert.strictEqual(reg.has("non_existent"), false);

    const got = reg.get("main_video");
    assert.deepStrictEqual(got, videoAsset);

    const req = reg.require("main_video");
    assert.deepStrictEqual(req, videoAsset);

    assert.strictEqual(reg.list().length, 1);
  });

  it("require() throws AssetNotFoundError when ID is not in registry", () => {
    const reg = new AssetRegistry();

    assert.throws(() => {
      reg.require("missing_asset_id");
    }, AssetNotFoundError);
  });

  it("rejects duplicate asset IDs with ValidationError", () => {
    const reg = new AssetRegistry();
    const asset1 = { id: "logo", type: "image" as const, source: { path: "logo.png" } };
    const asset2 = { id: "logo", type: "image" as const, source: { path: "other_logo.png" } };

    reg.add(asset1);

    assert.throws(() => {
      reg.add(asset2);
    }, ValidationError);
  });

  it("removes assets and clears registry cleanly", () => {
    const reg = new AssetRegistry();
    reg.add({ id: "a1", type: "image" as const, source: { path: "a1.png" } });
    reg.add({ id: "a2", type: "audio" as const, source: { path: "a2.mp3" } });

    assert.strictEqual(reg.size, 2);
    assert.strictEqual(reg.remove("a1"), true);
    assert.strictEqual(reg.size, 1);

    reg.clear();
    assert.strictEqual(reg.size, 0);
  });
});
