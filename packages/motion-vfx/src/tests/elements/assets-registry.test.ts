import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AssetRegistry } from "../../assets/index.js";
import { ElementFactory } from "../../elements/index.js";
import { ValidationError } from "../../errors/index.js";

describe("Fase 2A — AssetRegistry & Validation Tests", () => {
  it("registers, retrieves, lists and removes assets", () => {
    const reg = new AssetRegistry();
    reg.add({ id: "img_1", type: "image", source: { path: "assets/1.png" } });
    reg.add({ id: "vid_1", type: "video", source: { path: "assets/1.mp4" }, metadata: { width: 1920, height: 1080, duration: 10, fps: 30 } });

    assert.strictEqual(reg.has("img_1"), true);
    assert.strictEqual(reg.has("vid_1"), true);
    assert.strictEqual(reg.list().length, 2);

    const retrieved = reg.get("vid_1");
    assert.strictEqual(retrieved?.id, "vid_1");
    assert.strictEqual(retrieved?.type, "video");
    assert.strictEqual((retrieved?.metadata as any)?.duration, 10);

    reg.remove("img_1");
    assert.strictEqual(reg.has("img_1"), false);
    assert.strictEqual(reg.list().length, 1);
  });

  it("throws ValidationError on duplicate asset ID or invalid type", () => {
    const reg = new AssetRegistry();
    reg.add({ id: "logo", type: "image", source: { path: "logo.png" } });

    assert.throws(() => {
      reg.add({ id: "logo", type: "image", source: { path: "logo.png" } });
    }, ValidationError);

    assert.throws(() => {
      reg.add({ id: "bad_type", type: "unknown" as any, source: { path: "bad.png" } });
    }, ValidationError);
  });

  it("ElementFactory throws ValidationError when referencing an unknown asset ID", () => {
    const reg = new AssetRegistry();
    const rawImageElement = {
      id: "img_elem",
      type: "image",
      source: { assetId: "missing_asset_id" },
    };

    assert.throws(() => {
      ElementFactory.fromJSON(rawImageElement, reg);
    }, ValidationError);
  });
});
