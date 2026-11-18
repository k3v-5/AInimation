import { z } from "zod";
import { SUPPORTED_LOCALES, SupportedLocale } from "./vlog.constants.js";

export { SupportedLocale };

/** Schema Zod para validación de locales soportados */
export const SupportedLocaleSchema = z.enum(SUPPORTED_LOCALES);

/** Schema Zod para un código de idioma base (ISO 639-1) */
export const LanguageCodeSchema = z.string().min(2).max(5);

/** Configuración de idioma para síntesis y adaptación */
export interface VlogLanguageConfig {
  locale: SupportedLocale;
  voiceId: string;
  speakingRate: number; // [0.80, 1.20], normal = 1.00
  pitch: number; // [0.80, 1.20], normal = 1.00
  enableSubtitles: boolean;
  subtitleMode: "STANDARD" | "WORD_BY_WORD" | "KARAOKE" | "EMPHASIS";
  audioMixOverride?: {
    voiceVolumeDb?: number;
    duckingAmountDb?: number;
  };
}

export const VlogLanguageConfigSchema = z.object({
  locale: SupportedLocaleSchema,
  voiceId: z.string().min(1),
  speakingRate: z.number().min(0.80).max(1.20).default(1.00),
  pitch: z.number().min(0.80).max(1.20).default(1.00),
  enableSubtitles: z.boolean().default(true),
  subtitleMode: z.enum(["STANDARD", "WORD_BY_WORD", "KARAOKE", "EMPHASIS"]).default("WORD_BY_WORD"),
  audioMixOverride: z.object({
    voiceVolumeDb: z.number().optional(),
    duckingAmountDb: z.number().optional(),
  }).optional(),
});

/** Perfil de voz neuronal disponible en el registro offline */
export interface VoiceProfile {
  id: string;
  name: string;
  locale: SupportedLocale;
  gender: "MALE" | "FEMALE" | "NEUTRAL";
  engine: "piper" | "edge-local" | "system-tts" | "mock";
  modelPath?: string;
  sampleRateHz: number;
  quality: "standard" | "high" | "neural";
}

export const VoiceProfileSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  locale: SupportedLocaleSchema,
  gender: z.enum(["MALE", "FEMALE", "NEUTRAL"]),
  engine: z.enum(["piper", "edge-local", "system-tts", "mock"]),
  modelPath: z.string().optional(),
  sampleRateHz: z.number().int().positive().default(44100),
  quality: z.enum(["standard", "high", "neural"]).default("neural"),
});

/** Representación canónica de un idioma en el proyecto */
export interface VlogLanguage {
  code: string; // ej. "es"
  locale: SupportedLocale; // ej. "es-MX"
  displayName: string; // ej. "Español (México)"
  isSourceLanguage: boolean;
  config: VlogLanguageConfig;
  activeVoice: VoiceProfile;
}

export const VlogLanguageSchema = z.object({
  code: z.string().min(2),
  locale: SupportedLocaleSchema,
  displayName: z.string().min(1),
  isSourceLanguage: z.boolean(),
  config: VlogLanguageConfigSchema,
  activeVoice: VoiceProfileSchema,
});
