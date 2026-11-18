import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AssetRepository } from "../../media-intelligence/core/AssetRepository.js";
import { Asset } from "../../media-intelligence/types/index.js";

describe("Fase 6 — Speech Search & Transcript Integration Tests", () => {
  it("searches assets by spoken words in transcript", () => {
    const repo = new AssetRepository();

    const assetVoice: Asset = {
      id: "voice_01",
      type: "audio",
      source: { uri: "/media/voice.mp3" },
      metadata: { filename: "voice.mp3", mimeType: "audio/mp3", duration: 15.0 },
      status: "available",
      transcript: {
        segments: [
          {
            start: 0.0,
            end: 5.0,
            text: "Hoy vamos a hablar de Inteligencia Artificial",
            words: [{ text: "Inteligencia", start: 2.0, end: 2.8 }],
          },
        ],
      },
    };

    repo.create(assetVoice);

    const searchResults = repo.search({ text: "Inteligencia Artificial" });
    assert.strictEqual(searchResults.length, 1);
    assert.strictEqual(searchResults[0].id, "voice_01");
  });
});
