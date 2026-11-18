import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { LoudnessNormalizer } from "../../delivery/audio/LoudnessNormalizer.js";
import { TruePeakLimiter } from "../../delivery/audio/TruePeakLimiter.js";

describe("Fase 25 — Capa 4: Platform Audio Compliance & True Peak Tests", () => {
  it("normalizes audio samples to target LUFS for TikTok (-16 LUFS) and YouTube (-14 LUFS)", () => {
    // Generar 2000 muestras sinusoidales
    const samples = new Float32Array(2000);
    for (let i = 0; i < samples.length; i++) {
      samples[i] = Math.sin(i * 0.05) * 0.05; // señal de nivel bajo
    }

    const initialLufs = LoudnessNormalizer.measureLufs(samples);
    assert.ok(initialLufs < -20); // señal baja

    // Normalizar para TikTok (-16 LUFS)
    const normTikTok = LoudnessNormalizer.normalize(samples, "tiktok");
    assert.equal(normTikTok.report.targetLufs, -16.0);
    assert.ok(Math.abs(normTikTok.report.finalLufs - -16.0) <= 1.0);
    assert.equal(normTikTok.report.compliant, true);

    // Normalizar para YouTube (-14 LUFS)
    const normYT = LoudnessNormalizer.normalize(samples, "youtube_horizontal");
    assert.equal(normYT.report.targetLufs, -14.0);
    assert.ok(Math.abs(normYT.report.finalLufs - -14.0) <= 1.0);
    assert.equal(normYT.report.compliant, true);
  });

  it("TruePeakLimiter clamps loud signals exceeding -1.0 dBTP (0.891)", () => {
    const loudSamples = new Float32Array([1.5, -1.2, 0.5, -0.2, 2.0]);
    const { limitedSamples, peakReduced } = TruePeakLimiter.limit(loudSamples, -1.0);

    assert.equal(peakReduced, true);
    const maxLinear = Math.pow(10, -1.0 / 20); // ~0.89125

    for (let i = 0; i < limitedSamples.length; i++) {
      assert.ok(Math.abs(limitedSamples[i]) <= maxLinear + 0.0001);
    }
  });
});
