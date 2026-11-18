import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AnalysisCache } from "../../audio-intelligence/core/AnalysisCache.js";
import { AudioAnalysis } from "../../audio-intelligence/types/index.js";

describe("Fase 5I — Analysis Cache & Versioning Tests", () => {
  it("caches and retrieves audio analysis by version, settings hash and source hash", () => {
    AnalysisCache.clear();

    const analysis: AudioAnalysis = {
      sourceId: "audio_track_1",
      duration: 180.0,
      metadata: {
        analyzerVersion: "1.0.0",
        settingsHash: "fft_512_hop_128",
        sourceHash: "sha256_abcdef123456",
      },
      beats: {
        bpm: 128,
        beats: [{ time: 0.0, strength: 1.0 }],
      },
    };

    AnalysisCache.set(analysis);
    assert.strictEqual(AnalysisCache.size, 1);

    const retrieved = AnalysisCache.get(analysis.metadata!);
    assert.strictEqual(retrieved?.beats?.bpm, 128);

    // Cache miss con settings distintas
    const miss = AnalysisCache.get({
      analyzerVersion: "1.0.0",
      settingsHash: "fft_1024_hop_256",
      sourceHash: "sha256_abcdef123456",
    });
    assert.strictEqual(miss, undefined);
  });
});
