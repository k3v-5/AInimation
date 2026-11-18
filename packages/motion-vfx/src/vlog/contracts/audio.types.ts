import { z } from "zod";

/** Tipos de pistas de audio en la jerarquía de mezcla */
export type VlogAudioTrackType = "VOICE" | "CRITICAL_SFX" | "MUSIC" | "AMBIENCE";

export const VlogAudioTrackTypeSchema = z.enum(["VOICE", "CRITICAL_SFX", "MUSIC", "AMBIENCE"]);

/** Keyframe individual de envolvente de ducking */
export interface DuckingKeyframe {
  timeSeconds: number;
  gainDb: number; // dB relativo (0 dB = normal, -10 dB = atenuado)
}

export const DuckingKeyframeSchema = z.object({
  timeSeconds: z.number().min(0),
  gainDb: z.number(),
});

/** Envolvente de atenuación automática (Auto-Ducking) */
export interface DuckingEnvelope {
  targetTrackId: string; // Habitualmente música
  triggerTrackId: string; // Habitualmente voz
  duckAmountDb: number; // Ej. -10.0 dB
  attackSeconds: number; // Ej. 0.12 s
  releaseSeconds: number; // Ej. 0.40 s
  keyframes: DuckingKeyframe[];
}

export const DuckingEnvelopeSchema = z.object({
  targetTrackId: z.string().min(1),
  triggerTrackId: z.string().min(1),
  duckAmountDb: z.number().default(-10.0),
  attackSeconds: z.number().positive().default(0.12),
  releaseSeconds: z.number().positive().default(0.40),
  keyframes: z.array(DuckingKeyframeSchema),
});

/** Configuración maestra de mezcla para un idioma */
export interface AudioMixConfig {
  masterSampleRateHz: number; // 44100 o 48000
  channels: number; // 2 (stereo)
  voiceLevelDb: number; // Default: 0 dB
  musicLevelDb: number; // Default: -14 dB
  sfxLevelDb: number; // Default: -3 dB
  ambienceLevelDb: number; // Default: -18 dB
  duckingDb: number; // Default: -10 dB
  truePeakCeilingDbTP: number; // -1.0 dBTP
  enableLimiter: boolean;
}

export const AudioMixConfigSchema = z.object({
  masterSampleRateHz: z.number().int().default(44100),
  channels: z.number().int().default(2),
  voiceLevelDb: z.number().default(0.0),
  musicLevelDb: z.number().default(-14.0),
  sfxLevelDb: z.number().default(-3.0),
  ambienceLevelDb: z.number().default(-18.0),
  duckingDb: z.number().default(-10.0),
  truePeakCeilingDbTP: z.number().default(-1.0),
  enableLimiter: z.boolean().default(true),
});

/** Definición de una pista de audio en el proyecto */
export interface VlogAudioTrack {
  id: string;
  name: string;
  type: VlogAudioTrackType;
  audioFilePath: string;
  timelineStartSeconds: number;
  timelineEndSeconds: number;
  volumeDb: number;
  isMuted: boolean;
  isSolo: boolean;
  duckingEnvelope?: DuckingEnvelope;
}

export const VlogAudioTrackSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  type: VlogAudioTrackTypeSchema,
  audioFilePath: z.string().min(1),
  timelineStartSeconds: z.number().min(0),
  timelineEndSeconds: z.number().min(0),
  volumeDb: z.number().default(0.0),
  isMuted: z.boolean().default(false),
  isSolo: z.boolean().default(false),
  duckingEnvelope: DuckingEnvelopeSchema.optional(),
});
