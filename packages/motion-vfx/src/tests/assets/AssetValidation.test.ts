import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AssetValidator } from "../../assets/AssetValidator.js";
import { ValidationError } from "../../errors/index.js";

describe("Fase 2A — AssetValidator Strict Schema Tests", () => {
  it("validates valid image, video and audio assets", () => {
    assert.doesNotThrow(() => {
      AssetValidator.validate({
        id: "img_valid",
        type: "image",
        source: { path: "img.png" },
        metadata: { width: 100, height: 100 },
      });
    });

    assert.doesNotThrow(() => {
      AssetValidator.validate({
        id: "vid_valid",
        type: "video",
        source: { path: "vid.mp4" },
        metadata: { width: 1920, height: 1080, duration: 10, fps: 60 },
      });
    });

    assert.doesNotThrow(() => {
      AssetValidator.validate({
        id: "aud_valid",
        type: "audio",
        source: { path: "aud.mp3" },
        metadata: { duration: 120, sampleRate: 48000, channels: 2 },
      });
    });
  });

  it("rejects invalid or empty IDs and invalid types", () => {
    assert.throws(() => {
      AssetValidator.validate({
        id: "",
        type: "image",
        source: { path: "img.png" },
      });
    }, ValidationError);

    assert.throws(() => {
      AssetValidator.validate({
        id: "valid_id",
        type: "unsupported_type" as any,
        source: { path: "img.png" },
      });
    }, ValidationError);
  });

  it("rejects missing or empty source path", () => {
    assert.throws(() => {
      AssetValidator.validate({
        id: "no_source_path",
        type: "image",
        source: { path: "" },
      });
    }, ValidationError);
  });

  it("rejects non-positive dimensions, durations or framerates", () => {
    // Image width <= 0
    assert.throws(() => {
      AssetValidator.validate({
        id: "bad_img_w",
        type: "image",
        source: { path: "img.png" },
        metadata: { width: 0, height: 100 },
      });
    }, ValidationError);

    // Video fps <= 0
    assert.throws(() => {
      AssetValidator.validate({
        id: "bad_vid_fps",
        type: "video",
        source: { path: "vid.mp4" },
        metadata: { width: 1920, height: 1080, duration: 10, fps: 0 },
      });
    }, ValidationError);

    // Audio duration <= 0
    assert.throws(() => {
      AssetValidator.validate({
        id: "bad_aud_dur",
        type: "audio",
        source: { path: "aud.mp3" },
        metadata: { duration: -5 },
      });
    }, ValidationError);
  });
});
