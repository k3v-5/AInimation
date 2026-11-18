import { z } from "zod";

/** Palabra transcrita individual con timestamps precisos en segundos */
export interface VlogTranscriptWord {
  word: string;
  startSeconds: number;
  endSeconds: number;
  confidence: number; // [0.0, 1.0]
  punctuated?: string;
}

export const VlogTranscriptWordSchema = z.object({
  word: z.string().min(1),
  startSeconds: z.number().min(0),
  endSeconds: z.number().min(0),
  confidence: z.number().min(0).max(1),
  punctuated: z.string().optional(),
}).refine((w) => w.endSeconds >= w.startSeconds, {
  message: "endSeconds must be greater than or equal to startSeconds",
});

/** Segmento de transcripción (frase u oración completa) */
export interface VlogTranscriptSegment {
  id: string;
  startSeconds: number;
  endSeconds: number;
  text: string;
  confidence: number;
  words: VlogTranscriptWord[];
  speakerId?: string;
}

export const VlogTranscriptSegmentSchema = z.object({
  id: z.string().min(1),
  startSeconds: z.number().min(0),
  endSeconds: z.number().min(0),
  text: z.string(),
  confidence: z.number().min(0).max(1),
  words: z.array(VlogTranscriptWordSchema),
  speakerId: z.string().optional(),
}).refine((s) => s.endSeconds >= s.startSeconds, {
  message: "endSeconds must be greater than or equal to startSeconds",
});

/** Documento canónico de transcripción de voz (Whisper) */
export interface VlogTranscript {
  id: string;
  language: string; // ej. "es", "en"
  locale?: string; // ej. "es-MX"
  durationSeconds: number;
  confidence: number;
  segments: VlogTranscriptSegment[];
  rawText: string;
}

export const VlogTranscriptSchema = z.object({
  id: z.string().min(1),
  language: z.string().min(2),
  locale: z.string().optional(),
  durationSeconds: z.number().min(0),
  confidence: z.number().min(0).max(1),
  segments: z.array(VlogTranscriptSegmentSchema),
  rawText: z.string(),
});

/** Tipos de pausas acústicas en el habla humana */
export type PauseType =
  | "MICRO_PAUSE"
  | "BREATH"
  | "NARRATIVE"
  | "HESITATION"
  | "LONG_SILENCE"
  | "UNKNOWN";

export const PauseTypeSchema = z.enum([
  "MICRO_PAUSE",
  "BREATH",
  "NARRATIVE",
  "HESITATION",
  "LONG_SILENCE",
  "UNKNOWN",
]);

/** Evento acústico de pausa clasificada */
export interface SpeechPause {
  id: string;
  startSeconds: number;
  endSeconds: number;
  durationSeconds: number;
  type: PauseType;
  confidence: number;
  isRemovable: boolean;
  precedingWord?: string;
  succeedingWord?: string;
}

export const SpeechPauseSchema = z.object({
  id: z.string().min(1),
  startSeconds: z.number().min(0),
  endSeconds: z.number().min(0),
  durationSeconds: z.number().min(0),
  type: PauseTypeSchema,
  confidence: z.number().min(0).max(1),
  isRemovable: z.boolean(),
  precedingWord: z.string().optional(),
  succeedingWord: z.string().optional(),
});

/** Detección acústica de respiración entre palabras */
export interface BreathEvent {
  id: string;
  startSeconds: number;
  endSeconds: number;
  durationSeconds: number;
  confidence: number;
  peakDb: number;
  attenuationDb: number; // Ej. -6.0 dB
  retain: boolean;
}

export const BreathEventSchema = z.object({
  id: z.string().min(1),
  startSeconds: z.number().min(0),
  endSeconds: z.number().min(0),
  durationSeconds: z.number().min(0),
  confidence: z.number().min(0).max(1),
  peakDb: z.number(),
  attenuationDb: z.number(),
  retain: z.boolean(),
});

/** Región de silencio acústico continuo */
export interface SilenceRegion {
  startSeconds: number;
  endSeconds: number;
  durationSeconds: number;
  averageEnergyRms: number;
}

export const SilenceRegionSchema = z.object({
  startSeconds: z.number().min(0),
  endSeconds: z.number().min(0),
  durationSeconds: z.number().min(0),
  averageEnergyRms: z.number().min(0),
});

/** Anclaje de ojos para reencuadre dinámico y Punch-In */
export interface EyeAnchor {
  normalizedX: number; // 0.0 a 1.0 (pantalla normalizada)
  normalizedY: number; // 0.0 a 1.0
  interocularDistanceNormalized: number;
  confidence: number;
}

export const EyeAnchorSchema = z.object({
  normalizedX: z.number().min(0).max(1),
  normalizedY: z.number().min(0).max(1),
  interocularDistanceNormalized: z.number().min(0).max(1),
  confidence: z.number().min(0).max(1),
});

/** Muestra temporal de seguimiento facial */
export interface FaceSample {
  timeSeconds: number;
  boundingBox: {
    x: number; // Coordenadas normalizadas [0, 1]
    y: number;
    width: number;
    height: number;
  };
  eyes?: EyeAnchor;
  confidence: number;
}

export const FaceSampleSchema = z.object({
  timeSeconds: z.number().min(0),
  boundingBox: z.object({
    x: z.number().min(0).max(1),
    y: z.number().min(0).max(1),
    width: z.number().min(0).max(1),
    height: z.number().min(0).max(1),
  }),
  eyes: EyeAnchorSchema.optional(),
  confidence: z.number().min(0).max(1),
});

/** Trayectoria de rostro y orador activo */
export interface FaceTrack {
  trackId: string;
  sourceMediaId: string;
  samples: FaceSample[];
  isActiveSpeaker: boolean;
}

export const FaceTrackSchema = z.object({
  trackId: z.string().min(1),
  sourceMediaId: z.string().min(1),
  samples: z.array(FaceSampleSchema),
  isActiveSpeaker: z.boolean(),
});
