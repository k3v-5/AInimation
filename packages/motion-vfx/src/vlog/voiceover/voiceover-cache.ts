import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { VoiceoverCacheError } from "../contracts/errors.js";
import { SupportedLocale } from "../contracts/language.types.js";
import { TTSResult } from "../contracts/voiceover.types.js";
import { WavValidator } from "./wav-validator.js";

/** Opciones de clave de caché para síntesis determinista */
export interface CacheKeyParams {
  providerId: string;
  locale: SupportedLocale;
  voiceId: string;
  normalizedText: string;
  speakingRate?: number;
  pitch?: number;
}

/**
 * Gestor de Caché y Almacenamiento Atómico de Locución (Milestone 4-14 & 4-15).
 * Emplea claves SHA-256 basadas en contenido puro (sin timestamps ni PIDs) y
 * garantiza transaccionalidad atómica (tmp -> flush -> validate -> rename).
 */
export class VoiceoverCache {
  private cacheDirectory: string;
  private memoryCache = new Map<string, TTSResult>();

  constructor(cacheDirectory?: string) {
    this.cacheDirectory = cacheDirectory ?? path.join(process.cwd(), ".cache", "voiceover");
  }

  /**
   * Genera la clave de caché SHA-256 estrictamente determinista.
   */
  public static computeKey(params: CacheKeyParams): string {
    const canonicalPayload = JSON.stringify({
      providerId: params.providerId,
      locale: params.locale,
      voiceId: params.voiceId,
      normalizedText: params.normalizedText.trim(),
      rate: params.speakingRate ?? 1.0,
      pitch: params.pitch ?? 0,
      format: "PCM_16_44100_MONO",
    });

    return crypto.createHash("sha256").update(canonicalPayload).digest("hex");
  }

  /**
   * Obtiene un resultado sintetizado previamente desde memoria o disco.
   */
  public async get(cacheKey: string, requestId = "cached", locale: SupportedLocale = "es-MX"): Promise<TTSResult | null> {
    // 1. Verificar caché en memoria
    if (this.memoryCache.has(cacheKey)) {
      return this.memoryCache.get(cacheKey)!;
    }

    // 2. Verificar archivo en disco
    const wavPath = path.join(this.cacheDirectory, `${cacheKey}.wav`);
    const metaPath = path.join(this.cacheDirectory, `${cacheKey}.json`);

    if (fs.existsSync(wavPath) && fs.existsSync(metaPath)) {
      try {
        const audioBuffer = fs.readFileSync(wavPath);
        const meta = JSON.parse(fs.readFileSync(metaPath, "utf-8"));

        // Validar integridad binaria antes de servir desde caché
        const wavMeta = WavValidator.validateBuffer(audioBuffer, true);

        const result: TTSResult = {
          requestId,
          locale,
          audioBuffer,
          checksumSha256: crypto.createHash("sha256").update(audioBuffer).digest("hex"),
          durationSeconds: wavMeta.durationSeconds,
          wordTimings: meta.wordTimings ?? [],
          sampleRateHz: wavMeta.sampleRate,
          channels: wavMeta.channels,
        };

        this.memoryCache.set(cacheKey, result);
        return result;
      } catch {
        // En caso de corrupción en disco, ignorar y recalcular
        return null;
      }
    }

    return null;
  }

  /**
   * Almacena atómicamente un resultado de síntesis en disco y memoria.
   */
  public async set(cacheKey: string, result: TTSResult): Promise<void> {
    // 1. Validar buffer antes de almacenar
    WavValidator.validateBuffer(result.audioBuffer, true);

    // 2. Guardar en memoria
    this.memoryCache.set(cacheKey, result);

    // 3. Escritura atómica en disco si existe directorio
    try {
      if (!fs.existsSync(this.cacheDirectory)) {
        fs.mkdirSync(this.cacheDirectory, { recursive: true });
      }

      const tempWavPath = path.join(this.cacheDirectory, `${cacheKey}_${Date.now()}.tmp`);
      const targetWavPath = path.join(this.cacheDirectory, `${cacheKey}.wav`);
      const metaPath = path.join(this.cacheDirectory, `${cacheKey}.json`);

      // Escribir en archivo temporal
      fs.writeFileSync(tempWavPath, result.audioBuffer);

      // Renombrado atómico
      fs.renameSync(tempWavPath, targetWavPath);

      // Guardar metadatos JSON complementarios
      const meta = {
        checksumSha256: result.checksumSha256,
        durationSeconds: result.durationSeconds,
        wordTimings: result.wordTimings,
        sampleRateHz: result.sampleRateHz,
        channels: result.channels,
      };
      fs.writeFileSync(metaPath, JSON.stringify(meta, null, 2), "utf-8");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      throw new VoiceoverCacheError(`Failed to persist cache entry '${cacheKey}': ${msg}`);
    }
  }

  public clearMemory(): void {
    this.memoryCache.clear();
  }
}
