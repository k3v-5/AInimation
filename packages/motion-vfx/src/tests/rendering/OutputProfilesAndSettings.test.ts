import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { BuiltinOutputProfiles } from "../../rendering/profiles/OutputProfiles.js";

describe("Fase 9 — Output Profiles & Render Settings Tests", () => {
  it("provides standard profiles for TikTok (9:16), YouTube (16:9), 4K and ProRes Master", () => {
    const tiktok = BuiltinOutputProfiles["tiktok-1080x1920"];
    assert.strictEqual(tiktok.width, 1080);
    assert.strictEqual(tiktok.height, 1920);
    assert.strictEqual(tiktok.codec, "H.264");
    assert.strictEqual(tiktok.container, "mp4");

    const prores = BuiltinOutputProfiles["master-prores"];
    assert.strictEqual(prores.width, 3840);
    assert.strictEqual(prores.height, 2160);
    assert.strictEqual(prores.codec, "ProRes");
    assert.strictEqual(prores.container, "mov");
  });
});
