import { z } from "zod";
import { SupportedLocaleSchema } from "./language.types.js";
import { SupportedLocale } from "./vlog.constants.js";

/** Timestamp palabra por palabra emitido por el motor TTS o alineador forzado */
export interface VoiceWordTiming {
  word: string;
  startSeconds: number;
  endSeconds: number;
  confidence: number;
}

export const VoiceWordTimingSchema = z.object({
  word: z.string().min(1),
  startSeconds: z.number().min(0),
  endSeconds: z.number().min(0),
  confidence: z.number().min(0).max(1),
}).refine((w) => w.endSeconds >= w.startSeconds, {
  message: "endSeconds must be >= startSeconds",
});

/** Solicitud de síntesis vocal para un segmento narrativo */
export interface TTSRequest {
  id: string;
  locale: SupportedLocale;
  voiceId: string;
  speechText: string; // Texto fonéticamente normalizado para pronunciación
  displayText?: string; // Texto original para render visual
  speakingRate?: number; // [0.80, 1.20]
  pitch?: number;
  targetDurationSeconds?: number;
}

export const TTSRequestSchema = z.object({
  id: z.string().min(1),
  locale: SupportedLocaleSchema,
  voiceId: z.string().min(1),
  speechText: z.string().min(1),
  displayText: z.string().optional(),
  speakingRate: z.number().min(0.80).max(1.20).optional(),
  pitch: z.number().min(0.80).max(1.20).optional(),
  targetDurationSeconds: z.number().positive().optional(),
});

/** Resultado de síntesis vocal generada */
export interface TTSResult {
  requestId: string;
  locale: SupportedLocale;
  audioBuffer: Buffer | Uint8Array;
  audioWavPath?: string;
  durationSeconds: number;
  wordTimings: VoiceWordTiming[];
  sampleRateHz: number; // 44100 Hz
  channels: number; // 1 (mono)
  checksumSha256: string;
}

/** Interfaz abstracta para proveedores TTS locales (EXPLICIT_REQUIREMENT - Master Spec Sec 20) */
export interface TTSProvider {
  readonly id: string;
  readonly name: string;
  isAvailable(): Promise<boolean>;
  synthesize(request: TTSRequest): Promise<TTSResult>;
  getSupportedLocales(): SupportedLocale[];
}

/** Segmento individual de locución dentro de una pista de idioma */
export interface VoiceoverSegment {
  narrativeSegmentId: string;
  startSeconds: number;
  endSeconds: number;
  durationSeconds: number;
  speechText: string;
  displayText: string;
  words: VoiceWordTiming[];
}

export const VoiceoverSegmentSchema = z.object({
  narrativeSegmentId: z.string().min(1),
  startSeconds: z.number().min(0),
  endSeconds: z.number().min(0),
  durationSeconds: z.number().min(0),
  speechText: z.string(),
  displayText: z.string(),
  words: z.array(VoiceWordTimingSchema),
});

/** Pista completa de locución para un idioma específico */
export interface VoiceoverTrack {
  id: string;
  locale: SupportedLocale;
  voiceId: string;
  audioWavPath: string;
  durationSeconds: number;
  segments: VoiceoverSegment[];
  checksumSha256: string;
  format: {
    sampleRateHz: number; // 44100
    bitDepth: number; // 16
    channels: number; // 1
  };
}

export const VoiceoverTrackSchema = z.object({
  id: z.string().min(1),
  locale: SupportedLocaleSchema,
  voiceId: z.string().min(1),
  audioWavPath: z.string().min(1),
  durationSeconds: z.number().min(0),
  segments: z.array(VoiceoverSegmentSchema),
  checksumSha256: z.string().min(64).max(64),
  format: z.object({
    sampleRateHz: z.number().int().default(44100),
    bitDepth: z.number().int().default(16),
    channels: z.number().int().default(1),
  }),
});

/** Manifiesto del paquete de locuciones para todos los idiomas de un proyecto */
export interface VoiceoverManifest {
  projectId: string;
  sourceLocale: SupportedLocale;
  targetLocales: SupportedLocale[];
  tracks: Record<SupportedLocale, VoiceoverTrack>;
  generatedAtTimestamp: number;
}

export const VoiceoverManifestSchema = z.object({
  projectId: z.string().min(1),
  sourceLocale: SupportedLocaleSchema,
  targetLocales: z.array(SupportedLocaleSchema),
  tracks: z.record(VoiceoverTrackSchema),
  generatedAtTimestamp: z.number(),
});
