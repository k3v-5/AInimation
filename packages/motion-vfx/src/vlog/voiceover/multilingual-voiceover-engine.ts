import crypto from "node:crypto";
import {
  UnsupportedLocaleError,
  VoiceoverAlignmentError,
  VoiceoverSynthesisError,
} from "../contracts/errors.js";
import { SupportedLocale } from "../contracts/language.types.js";
import {
  TTSProvider,
  TTSRequest,
  TTSResult,
  VoiceoverManifest,
  VoiceoverManifestSchema,
  VoiceoverSegment,
  VoiceoverTrack,
  VoiceWordTiming,
} from "../contracts/voiceover.types.js";
import { AUDIO_SPECS, SUPPORTED_LOCALES } from "../contracts/vlog.constants.js";
import { DeterministicMockTTSProvider } from "./deterministic-mock-tts-provider.js";
import { TextNormalizationOptions, TextNormalizer } from "./text-normalizer.js";
import { TextSegmenter } from "./text-segmenter.js";
import { TTSProviderRegistry } from "./tts-provider-registry.js";
import { VoiceCatalog } from "./voice-catalog.js";
import { VoiceoverCache } from "./voiceover-cache.js";
import { WavValidator } from "./wav-validator.js";

/** Opciones de generación para MultilingualVoiceoverEngine */
export interface VoiceoverEngineOptions {
  preferredProviderId?: string;
  voiceId?: string;
  speakingRate?: number;
  pitch?: number;
  normalizationOptions?: TextNormalizationOptions;
  cacheDirectory?: string;
}

/**
 * Motor Central de Locución Multilingüe Offline (Milestone 4-09).
 * Orquesta la validación de locale, normalización de texto, segmentación,
 * resolución de proveedores TTS, validación binaria de audio y emisión de manifiestos.
 */
export class MultilingualVoiceoverEngine {
  private cache: VoiceoverCache;
  private registry: TTSProviderRegistry;

  constructor(options: { cacheDirectory?: string } = {}) {
    this.cache = new VoiceoverCache(options.cacheDirectory);
    this.registry = TTSProviderRegistry.getInstance();

    // Asegurar que el proveedor mock determinista está registrado por defecto
    if (!this.registry.getProvider("mock-deterministic-tts")) {
      this.registry.registerProvider(new DeterministicMockTTSProvider());
    }
  }

  /**
   * Sintetiza un texto completo generando la pista de voz y su manifiesto reproducible.
   */
  public async generateVoiceover(
    projectId: string,
    rawText: string,
    targetLocale: SupportedLocale,
    options: VoiceoverEngineOptions = {}
  ): Promise<{ track: VoiceoverTrack; manifest: VoiceoverManifest }> {
    // 1. Validación de Locale
    if (!SUPPORTED_LOCALES.includes(targetLocale)) {
      throw new UnsupportedLocaleError(targetLocale, SUPPORTED_LOCALES);
    }

    // 2. Normalización de Texto
    const normResult = TextNormalizer.normalize(rawText, targetLocale, options.normalizationOptions);

    // 3. Segmentación Lingüística
    const textSegments = TextSegmenter.segment(normResult.normalizedText, targetLocale);
    if (textSegments.length === 0) {
      throw new VoiceoverSynthesisError("Input text contains no valid words after normalization");
    }

    // 4. Resolución de Proveedor y Voz
    const provider: TTSProvider = this.registry.resolveProvider(targetLocale, options.preferredProviderId);
    const voiceEntry = options.voiceId
      ? VoiceCatalog.getVoiceById(options.voiceId, targetLocale)
      : VoiceCatalog.getDefaultVoice(targetLocale);

    // 5. Síntesis secuencial determinista de segmentos
    const voiceoverSegments: VoiceoverSegment[] = [];
    const pcmSampleBuffers: Int16Array[] = [];
    let currentTimelineStart = 0.0;

    for (const seg of textSegments) {
      const cacheKey = VoiceoverCache.computeKey({
        providerId: provider.id,
        locale: targetLocale,
        voiceId: voiceEntry.id,
        normalizedText: seg.normalizedText,
        speakingRate: options.speakingRate ?? 1.0,
        pitch: options.pitch ?? 0,
      });

      // Consultar caché
      let ttsResult = await this.cache.get(cacheKey, `req_${seg.segmentIndex}`, targetLocale);

      if (!ttsResult) {
        const request: TTSRequest = {
          id: `req_${seg.segmentIndex + 1}`,
          locale: targetLocale,
          voiceId: voiceEntry.id,
          speechText: seg.normalizedText,
          displayText: seg.sourceText,
          speakingRate: options.speakingRate ?? 1.0,
          pitch: options.pitch ?? 0,
        };

        ttsResult = await provider.synthesize(request);

        // Validar buffer WAV antes de guardar en caché
        WavValidator.validateBuffer(ttsResult.audioBuffer, true);
        await this.cache.set(cacheKey, ttsResult);
      }

      // Validar y ajustar word timings del segmento
      const segmentDuration = ttsResult.durationSeconds;
      const segmentEnd = Number((currentTimelineStart + segmentDuration).toFixed(4));

      const adjustedWordTimings: VoiceWordTiming[] = [];
      for (const wt of ttsResult.wordTimings) {
        if (wt.startSeconds > wt.endSeconds) {
          throw new VoiceoverAlignmentError(`Monotonicity violation: word '${wt.word}' start (${wt.startSeconds}) > end (${wt.endSeconds})`);
        }

        adjustedWordTimings.push({
          word: wt.word,
          startSeconds: Number((currentTimelineStart + wt.startSeconds).toFixed(4)),
          endSeconds: Number((currentTimelineStart + wt.endSeconds).toFixed(4)),
          confidence: wt.confidence,
        });
      }

      voiceoverSegments.push({
        narrativeSegmentId: `seg_${seg.segmentIndex + 1}`,
        speechText: seg.normalizedText,
        displayText: seg.sourceText,
        startSeconds: Number(currentTimelineStart.toFixed(4)),
        endSeconds: segmentEnd,
        durationSeconds: segmentDuration,
        words: adjustedWordTimings,
      });

      // Extraer muestras PCM (descartando encabezado WAV de 44 bytes)
      const dataOffset = 44;
      const pcmBytes = ttsResult.audioBuffer.subarray(dataOffset);
      const int16Samples = new Int16Array(
        pcmBytes.buffer,
        pcmBytes.byteOffset,
        Math.floor(pcmBytes.length / 2)
      );
      pcmSampleBuffers.push(int16Samples);

      currentTimelineStart = segmentEnd;
    }

    // 6. Concatenar muestras PCM de todos los segmentos en un WAV canónico único
    const totalSamplesCount = pcmSampleBuffers.reduce((sum, b) => sum + b.length, 0);
    const combinedPcm = new Int16Array(totalSamplesCount);
    let sampleOffset = 0;
    for (const buf of pcmSampleBuffers) {
      combinedPcm.set(buf, sampleOffset);
      sampleOffset += buf.length;
    }

    const finalWavBuffer = WavValidator.createCanonicalWav(combinedPcm);
    const finalChecksumSha256 = crypto.createHash("sha256").update(finalWavBuffer).digest("hex");
    const totalDurationSeconds = Number(currentTimelineStart.toFixed(4));

    // 7. Construir VoiceoverTrack
    const track: VoiceoverTrack = {
      id: `vo_${targetLocale}_${projectId}`,
      locale: targetLocale,
      voiceId: voiceEntry.id,
      audioWavPath: `audio/voiceover_${targetLocale}.wav`,
      durationSeconds: totalDurationSeconds,
      segments: voiceoverSegments,
      checksumSha256: finalChecksumSha256,
      format: {
        sampleRateHz: AUDIO_SPECS.VOICEOVER.sampleRate,
        bitDepth: AUDIO_SPECS.VOICEOVER.bitDepth,
        channels: AUDIO_SPECS.VOICEOVER.channels,
      },
    };

    // 8. Construir Manifiesto de auditoría completa
    const tracksRecord: Record<SupportedLocale, VoiceoverTrack> = {
      [targetLocale]: track,
    } as Record<SupportedLocale, VoiceoverTrack>;

    const manifest: VoiceoverManifest = {
      projectId,
      sourceLocale: targetLocale,
      targetLocales: [targetLocale],
      tracks: tracksRecord,
      generatedAtTimestamp: 1700000000,
    };

    // Validar esquema Zod formal del manifiesto
    VoiceoverManifestSchema.parse(manifest);

    return { track, manifest };
  }
}
