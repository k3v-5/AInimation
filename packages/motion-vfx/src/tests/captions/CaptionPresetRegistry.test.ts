import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { CaptionPresetRegistry } from "../../captions/presets/CaptionPresetRegistry.js";

describe("Fase 5E — Caption Preset Registry Tests", () => {
  it("registers and retrieves standard caption presets (clean, viral-tiktok, karaoke, cinematic)", () => {
    assert.strictEqual(CaptionPresetRegistry.has("clean"), true);
    assert.strictEqual(CaptionPresetRegistry.has("viral-tiktok"), true);
    assert.strictEqual(CaptionPresetRegistry.has("karaoke"), true);
    assert.strictEqual(CaptionPresetRegistry.has("cinematic"), true);

    const viral = CaptionPresetRegistry.get("viral-tiktok");
    assert.strictEqual(viral.style.fontWeight, 900);
    assert.strictEqual(viral.activeWordOverride?.scale, 1.15);
  });

  it("throws ValidationError on duplicate preset ID", () => {
    assert.throws(
      () =>
        CaptionPresetRegistry.register({
          id: "clean",
          name: "Dup Clean",
          description: "dup",
          style: {} as any,
          layoutMode: "static",
          position: "bottom-center",
        }),
      /DUPLICATE_CAPTION_PRESET/
    );
  });
});
