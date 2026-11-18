import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AssetRegistry } from "../../assets/index.js";
import { ElementFactory } from "../../elements/ElementFactory.js";
import { ValidationError } from "../../errors/index.js";

describe("Fase 2B — ElementFactory Helper & Polymorphic fromJSON Tests", () => {
  it("creates concrete elements using factory helper methods", () => {
    const text = ElementFactory.createText({ text: "Hello" });
    const img = ElementFactory.createImage({ assetId: "img1" });
    const vid = ElementFactory.createVideo({ assetId: "vid1" });
    const aud = ElementFactory.createAudio({ assetId: "aud1" });
    const shape = ElementFactory.createShape({ shapeType: "rectangle" });
    const group = ElementFactory.createGroup();

    assert.strictEqual(text.type, "text");
    assert.strictEqual(img.type, "image");
    assert.strictEqual(vid.type, "video");
    assert.strictEqual(aud.type, "audio");
    assert.strictEqual(shape.type, "shape");
    assert.strictEqual(group.type, "group");
  });

  it("reconstructs elements polymorphically from JSON with asset validation", () => {
    const reg = new AssetRegistry();
    reg.add({ id: "valid_asset", type: "image", source: { path: "img.png" } });

    const rawImage = {
      id: "img_node",
      name: "Image Node",
      type: "image",
      startTime: 1,
      duration: 5,
      assetId: "valid_asset",
    };

    const element = ElementFactory.fromJSON(rawImage, reg);
    assert.strictEqual(element.id, "img_node");
    assert.strictEqual(element.type, "image");
    assert.strictEqual((element as any).assetId, "valid_asset");

    const rawInvalidAsset = {
      id: "bad_node",
      type: "image",
      assetId: "unknown_asset_id",
    };

    assert.throws(() => {
      ElementFactory.fromJSON(rawInvalidAsset, reg);
    }, ValidationError);
  });
});
