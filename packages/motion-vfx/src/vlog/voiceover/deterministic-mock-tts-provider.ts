import crypto from "node:crypto";
import { TTSInvalidRequestError } from "../contracts/errors.js";
import { SupportedLocale, VoiceProfile } from "../contracts/language.types.js";
import {
  TTSProvider,
  TTSRequest,
  TTSResult,
  VoiceWordTiming,
} from "../contracts/voiceover.types.js";
import { AUDIO_SPECS, SUPPORTED_LOCALES } from "../contracts/vlog.constants.js";
import { VoiceCatalog } from "./voice-catalog.js";
import { WavValidator } from "./wav-validator.js";

/**
 * Proveedor TTS Mock Determinista y Offline (Milestone 4-04).
 * Genera buffers de audio WAV reales y canónicos (PCM 16-bit 44.1kHz Mono) con
 * timings de palabras sintéticos sin aleatoriedad, sin timestamps de sistema y sin red.
 */
export class DeterministicMockTTSProvider implements TTSProvider {
  public readonly id = "mock-deterministic-tts";
  public readonly name = "Deterministic Mock TTS";
  public readonly isOfflineOnly = true;

  public async isAvailable(): Promise<boolean> {
    return true;
  }

  public getSupportedLocales(): SupportedLocale[] {
    return [...SUPPORTED_LOCALES];
  }

  public async getAvailableVoices(locale?: SupportedLocale): Promise<VoiceProfile[]> {
    if (locale) {
      return VoiceCatalog.getVoicesForLocale(locale);
    }
    return VoiceCatalog.getAllVoices();
  }

  public validateRequest(request: TTSRequest): void {
    if (!request) {
      throw new TTSInvalidRequestError("Request cannot be null or undefined");
    }
    if (!request.speechText || request.speechText.trim().length === 0) {
      throw new TTSInvalidRequestError("speechText cannot be empty");
    }
    if (!SUPPORTED_LOCALES.includes(request.locale)) {
      throw new TTSInvalidRequestError(`Unsupported locale '${request.locale}'`);
    }
  }

  public async synthesize(request: TTSRequest): Promise<TTSResult> {
    this.validateRequest(request);

    const words = request.speechText.trim().split(/\s+/).filter((w) => w.length > 0);
    const rateMultiplier = request.speakingRate ?? 1.0;
    const baseWordDuration = 0.35 / rateMultiplier;
    const wordPause = 0.05 / rateMultiplier;

    // 1. Generar word timings deterministas
    const wordTimings: VoiceWordTiming[] = [];
    let currentTime = 0.0;

    for (let i = 0; i < words.length; i++) {
      const word = words[i];
      const start = Number(currentTime.toFixed(4));
      const end = Number((currentTime + baseWordDuration).toFixed(4));

      wordTimings.push({
        word,
        startSeconds: start,
        endSeconds: end,
        confidence: 0.99,
      });

      currentTime += baseWordDuration + wordPause;
    }

    const totalDurationSeconds = Number(currentTime.toFixed(4));

    // 2. Sintetizar muestras PCM 16-bit 44.1kHz mono deterministas
    const sampleRate = AUDIO_SPECS.VOICEOVER.sampleRate;
    const totalSamples = Math.floor(totalDurationSeconds * sampleRate);
    const pcmSamples = new Int16Array(totalSamples);

    // Generar forma de onda armónica sintética determinista basada en el texto
    const textHash = crypto.createHash("sha256").update(request.speechText).digest();
    const baseFreq = 180 + (textHash[0] % 120); // 180 a 300 Hz según contenido

    for (let i = 0; i < totalSamples; i++) {
      const t = i / sampleRate;
      // Generar tono sinusoidal con envolvente suave
      const envelope = Math.sin(Math.PI * (i / totalSamples)); // fade-in/fade-out
      const tone = Math.sin(2 * Math.PI * baseFreq * t);
      const harmonic = 0.3 * Math.sin(4 * Math.PI * baseFreq * t);
      const sampleVal = Math.floor((tone + harmonic) * envelope * 8000); // amplitud moderada

      pcmSamples[i] = Math.max(-32768, Math.min(32767, sampleVal));
    }

    // 3. Crear buffer WAV canónico verificado
    const audioBuffer = WavValidator.createCanonicalWav(pcmSamples);
    const checksumSha256 = crypto.createHash("sha256").update(audioBuffer).digest("hex");

    return {
      requestId: request.id,
      locale: request.locale,
      audioBuffer,
      checksumSha256,
      durationSeconds: totalDurationSeconds,
      wordTimings,
      sampleRateHz: sampleRate,
      channels: AUDIO_SPECS.VOICEOVER.channels,
    };
  }
}
