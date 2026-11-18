import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { describe, it } from "node:test";
import fc from "fast-check";
import {
  DeterministicMockTTSProvider,
  LocalPiperTTSProvider,
  MultilingualVoiceoverEngine,
  SUPPORTED_LOCALES,
  SupportedLocale,
  TTSModelMissingError,
  TTSProviderRegistry,
  UnsupportedLocaleError,
  VoiceCatalog,
  VoiceNotAvailableError,
  VoiceoverCache,
  WavValidator,
} from "../../../vlog/index.js";

describe("Milestone 4 — Multilingual Voiceover & Offline TTS Engine Suite", () => {
  it("resolves providers and validates unsupported locales", () => {
    const registry = TTSProviderRegistry.getInstance();
    const mockProvider = new DeterministicMockTTSProvider();
    registry.registerProvider(mockProvider);

    const resolved = registry.resolveProvider("es-MX");
    assert.equal(resolved.id, "mock-deterministic-tts");

    // Locale no soportado por el sistema debe lanzar UnsupportedLocaleError
    assert.throws(
      // @ts-expect-error probando locale inválido deliberadamente
      () => registry.resolveProvider("it-IT"),
      UnsupportedLocaleError
    );
  });

  it("provides valid voice catalog for all 7 official locales", () => {
    for (const loc of SUPPORTED_LOCALES) {
      const voices = VoiceCatalog.getVoicesForLocale(loc);
      assert.ok(voices.length >= 2, `Expected at least 2 voices for locale '${loc}'`);

      const defaultVoice = VoiceCatalog.getDefaultVoice(loc);
      assert.ok(defaultVoice !== undefined);
      assert.equal(defaultVoice.locale, loc);
      assert.equal(defaultVoice.isDefault, true);
    }

    assert.throws(
      () => VoiceCatalog.getVoiceById("non_existent_voice_999", "es-MX"),
      VoiceNotAvailableError
    );
  });

  it("verifies LocalPiperTTSProvider enforces offline policy and checks local model", async () => {
    const piperProvider = new LocalPiperTTSProvider({
      modelsDirectory: path.join(os.tmpdir(), "non_existent_piper_models_dir"),
    });

    // Si el modelo local no existe, debe lanzar TTSModelMissingError
    await assert.rejects(
      async () =>
        piperProvider.synthesize({
          id: "req_test",
          displayText: "Prueba",
          speechText: "Prueba",
          locale: "es-MX",
          voiceId: "es_MX-ald-medium",
        }),
      TTSModelMissingError
    );
  });

  it("guarantees 100% deterministic synthesis with DeterministicMockTTSProvider", async () => {
    const mock = new DeterministicMockTTSProvider();

    const req = {
      id: "req_det_01",
      text: "Bienvenidos a Guadalajara, Jalisco.",
      speechText: "Bienvenidos a Guadalajara, Jalisco.",
      locale: "es-MX" as SupportedLocale,
      voiceId: "es_MX-ald-medium",
    };

    const res1 = await mock.synthesize(req);
    const res2 = await mock.synthesize(req);

    // Mismo texto + misma voz => hash y bytes exactamente idénticos
    assert.equal(res1.checksumSha256, res2.checksumSha256);
    assert.equal(res1.durationSeconds, res2.durationSeconds);
    assert.equal(res1.wordTimings.length, res2.wordTimings.length);
    assert.deepEqual(res1.audioBuffer, res2.audioBuffer);

    // Validar el WAV generado
    const wavMeta = WavValidator.validateBuffer(res1.audioBuffer, true);
    assert.equal(wavMeta.sampleRate, 44100);
    assert.equal(wavMeta.channels, 1);
  });

  it("verifies VoiceoverCache deterministic keys and hit/miss behavior", async () => {
    const tmpCacheDir = fs.mkdtempSync(path.join(os.tmpdir(), "vo_cache_test_"));

    try {
      const cache = new VoiceoverCache(tmpCacheDir);

      const keyParams1 = {
        providerId: "mock",
        locale: "es-MX" as SupportedLocale,
        voiceId: "voice1",
        normalizedText: "texto de prueba",
      };

      const keyParams2 = { ...keyParams1, locale: "en-US" as SupportedLocale };

      const key1 = VoiceoverCache.computeKey(keyParams1);
      const key2 = VoiceoverCache.computeKey(keyParams2);

      // Misma solicitud => misma clave
      assert.equal(key1, VoiceoverCache.computeKey(keyParams1));
      // Diferente locale => diferente clave
      assert.notEqual(key1, key2);

      // Cache miss inicial
      const miss = await cache.get(key1);
      assert.equal(miss, null);

      // Sintetizar y guardar
      const mock = new DeterministicMockTTSProvider();
      const synthesized = await mock.synthesize({
        id: "req_cache",
        displayText: "texto",
        speechText: "texto de prueba",
        locale: "es-MX",
        voiceId: "es_MX-ald-medium",
      });

      await cache.set(key1, synthesized);

      // Cache hit
      const hit = await cache.get(key1);
      assert.ok(hit !== null);
      assert.equal(hit.checksumSha256, synthesized.checksumSha256);
      assert.equal(hit.durationSeconds, synthesized.durationSeconds);
    } finally {
      fs.rmSync(tmpCacheDir, { recursive: true, force: true, maxRetries: 5, retryDelay: 100 });
    }
  });

  it("runs full MultilingualVoiceoverEngine pipeline across all 7 official locales", async () => {
    const tmpCacheDir = fs.mkdtempSync(path.join(os.tmpdir(), "vo_engine_test_"));

    try {
      const engine = new MultilingualVoiceoverEngine({ cacheDirectory: tmpCacheDir });

      const testPhrases: Record<SupportedLocale, string> = {
        "es-MX": "Bienvenidos a Guadalajara. El precio del recorrido es de $1,250.50 pesos.",
        "es-ES": "Bienvenidos a Madrid. El precio del recorrido es de €1,250.50.",
        "en-US": "Welcome to New York City. The tour price is $1,250.50.",
        "en-GB": "Welcome to London. The tour price is £1,250.50.",
        "pt-BR": "Bem-vindos a São Paulo. O preço do passeio é R$ 1,250.50.",
        "fr-FR": "Bienvenue à Paris. Le prix de la visite est de €1,250.50.",
        "de-DE": "Willkommen in Berlin. Der Preis der Tour beträgt €1,250.50.",
      };

      for (const loc of SUPPORTED_LOCALES) {
        const text = testPhrases[loc];
        const projectId = `proj_test_${loc}`;

        const { track, manifest } = await engine.generateVoiceover(projectId, text, loc);

        // Verificaciones de la pista
        assert.equal(track.locale, loc);
        assert.ok(track.durationSeconds > 0);
        assert.ok(track.segments.length >= 1);
        assert.equal(track.format.sampleRateHz, 44100);
        assert.equal(track.format.channels, 1);
        assert.equal(track.format.bitDepth, 16);

        // Verificaciones del manifiesto
        assert.equal(manifest.projectId, projectId);
        assert.equal(manifest.sourceLocale, loc);
        assert.ok(manifest.tracks[loc] !== undefined);
        assert.ok(manifest.tracks[loc].checksumSha256.length === 64);

        // Invariante de sincronización de palabras: w.start <= w.end
        for (const seg of track.segments) {
          for (let i = 0; i < seg.words.length; i++) {
            const wt = seg.words[i];
            assert.ok(wt.startSeconds <= wt.endSeconds, `Word '${wt.word}' start > end`);
            if (i > 0) {
              assert.ok(wt.startSeconds >= seg.words[i - 1].startSeconds);
            }
          }
        }
      }
    } finally {
      fs.rmSync(tmpCacheDir, { recursive: true, force: true, maxRetries: 5, retryDelay: 100 });
    }
  });

  it("PBT: synthesized word timings are strictly monotonic with non-negative durations", async () => {
    const mock = new DeterministicMockTTSProvider();

    await fc.assert(
      fc.asyncProperty(
        fc.array(fc.stringMatching(/^[a-zA-Z]{3,8}$/), { minLength: 2, maxLength: 8 }),
        fc.double({ min: 0.8, max: 1.2, noNaN: true }),
        async (words, rate) => {
          const phrase = words.join(" ");
          const res = await mock.synthesize({
            id: "req_pbt",
            displayText: phrase,
            speechText: phrase,
            locale: "es-MX",
            voiceId: "es_MX-ald-medium",
            speakingRate: rate,
          });

          assert.ok(res.durationSeconds > 0.0);
          for (let i = 0; i < res.wordTimings.length; i++) {
            const w = res.wordTimings[i];
            assert.ok(w.startSeconds < w.endSeconds);
            if (i > 0) {
              assert.ok(w.startSeconds >= res.wordTimings[i - 1].endSeconds);
            }
          }
        }
      )
    );
  });
});
