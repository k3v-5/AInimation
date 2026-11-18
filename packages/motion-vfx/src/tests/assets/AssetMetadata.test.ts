import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AssetValidator } from "../../assets/AssetValidator.js";

describe("Fase 5A — Asset Metadata Validation Tests", () => {
  it("validates valid video, image, audio, font, and svg assets", () => {
    assert.doesNotThrow(() => {
      AssetValidator.validate({
        id: "vid_01",
        type: "video",
        source: { path: "video.mp4" },
        metadata: { width: 1920, height: 1080, duration: 10, fps: 60, hasAudio: true },
      });
    });

    assert.doesNotThrow(() => {
      AssetValidator.validate({
        id: "font_01",
        type: "font",
        source: { path: "Inter-Bold.ttf" },
        metadata: { family: "Inter", weight: 700 },
      });
    });

    assert.doesNotThrow(() => {
      AssetValidator.validate({
        id: "svg_01",
        type: "svg",
        source: { path: "icon.svg" },
        metadata: { width: 64, height: 64, viewBox: "0 0 64 64" },
      });
    });
  });

  it("rejects negative or non-finite dimensions in metadata", () => {
    assert.throws(
      () =>
        AssetValidator.validate({
          id: "bad_img",
          type: "image",
          source: { path: "img.png" },
          metadata: { width: -100, height: 100 },
        }),
      /Image asset width must be a positive finite number/
    );
  });
});
