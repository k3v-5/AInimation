import { z } from "zod";

/**
 * REQ-019 & REQ-056: Jerarquía Canónica de 8 Buses de Audio
 */
export const AudioBusTypeSchema = z.enum([
  "MASTER",
  "VOICE",
  "DIALOGUE",
  "MUSIC",
  "AMBIENCE",
  "ROOM_TONE",
  "SFX",
  "CRITICAL_SFX",
  "ARCHIVE_AUDIO",
]);

export type AudioBusType = z.infer<typeof AudioBusTypeSchema>;

/**
 * REQ-067: Estratificación del Paisaje Sonoro (3 Planos)
 */
export const SoundscapeLayerSchema = z.enum([
  "FOREGROUND",
  "MIDGROUND",
  "BACKGROUND",
]);

export type SoundscapeLayer = z.infer<typeof SoundscapeLayerSchema>;

/**
 * REQ-069: Puntuación Sintáctica de Audio
 */
export const AudioPunctuationTypeSchema = z.enum([
  "COMMA",
  "PAUSE",
  "EMPHASIS",
  "FULL_STOP",
  "TRANSITION",
  "REVELATION",
]);

export type AudioPunctuationType = z.infer<typeof AudioPunctuationTypeSchema>;

/**
 * REQ-046 & EBU R128: Objetivos de Loudness
 */
export const LoudnessStandardSchema = z.enum(["WEB_SOCIAL", "BROADCAST"]);
export type LoudnessStandard = z.infer<typeof LoudnessStandardSchema>;

export interface LoudnessTarget {
  standard: LoudnessStandard;
  targetLufs: number; // -16 para WEB_SOCIAL, -23 para BROADCAST
  maxTruePeakDb: number; // <= -1.0 dBTP
  loudnessRangeTarget?: number; // LRA
}

export interface LoudnessMeasurement {
  integratedLufs: number;
  shortTermLufs: number;
  momentaryLufs: number;
  loudnessRange: number;
  truePeakDb: number;
  isCompliant: boolean;
  violations: string[];
}

/**
 * Automatización de Parámetros de Audio
 */
export interface AudioAutomationPoint {
  timestampSeconds: number;
  value: number;
  easing?: "LINEAR" | "BEZIER" | "EXPONENTIAL" | "HOLD";
}

export interface AudioAutomation {
  parameter: "gainDb" | "pan" | "lowpassCutoff" | "highpassCutoff";
  points: AudioAutomationPoint[];
}

/**
 * Efectos de Audio Declarativos
 */
export interface AudioEqBand {
  type: "LOW_SHELF" | "PEAK" | "HIGH_SHELF" | "NOTCH" | "HIGHPASS" | "LOWPASS";
  frequencyHz: number;
  gainDb: number;
  qFactor: number;
}

export interface AudioEffect {
  id: string;
  type: "EQ" | "COMPRESSOR" | "LIMITER" | "DE_ESSER" | "NOISE_GATE" | "REVERB";
  enabled: boolean;
  parameters: Record<string, unknown>;
}

/**
 * Bus de Audio Jerárquico
 */
export interface AudioBus {
  id: AudioBusType;
  name: string;
  parentBusId?: AudioBusType;
  gainDb: number;
  pan: number; // -1.0 (L) a 1.0 (R)
  mute: boolean;
  solo: boolean;
  layer?: SoundscapeLayer;
  effects: AudioEffect[];
  automations: AudioAutomation[];
}

/**
 * Clip y Región de Audio
 */
export interface AudioRegion {
  id: string;
  clipId: string;
  busId: AudioBusType;
  timelineRange: {
    startSeconds: number;
    durationSeconds: number;
  };
  sourceRange: {
    startSeconds: number;
    durationSeconds: number;
  };
  gainDb: number;
  pan: number;
  fadeInSeconds: number;
  fadeOutSeconds: number;
  layer: SoundscapeLayer;
  isRoomTonePatch?: boolean;
}

/**
 * Transición de Audio (J-Cut / L-Cut)
 */
export interface AudioTransition {
  id: string;
  type: "J_CUT" | "L_CUT" | "CROSSFADE" | "HARD_CUT";
  visualCutTimestampSeconds: number;
  audioLeadSeconds: number;
  audioTailSeconds: number;
  fromClipId: string;
  toClipId: string;
  reason: string;
}

/**
 * Propuesta no destructiva de reparación de diálogo (REQ-064)
 */
export type DialogueIssueType =
  | "CLIPPING"
  | "PLOSIVE"
  | "HUM"
  | "NOISE_FLOOR_DISCONTINUITY"
  | "ROOM_ECHO"
  | "ABRUPT_LEVEL_CHANGE"
  | "EXCESSIVE_SIBILANCE";

export interface DialogueRepairProposal {
  id: string;
  type: DialogueIssueType;
  confidence: number;
  affectedRegion: {
    clipId: string;
    startSeconds: number;
    durationSeconds: number;
  };
  suggestedParameters: {
    targetGainDb?: number;
    highpassCutoffHz?: number;
    notchFrequencyHz?: number;
    eqBands?: AudioEqBand[];
    reductionDb?: number;
  };
  rationale: string;
  reversible: boolean;
  requiresHumanReview: boolean;
}

/**
 * Perfil de Room Tone por Localización (REQ-063)
 */
export interface RoomToneProfile {
  locationId: string;
  noiseFloorDb: number;
  dominantFrequencyHz?: number;
  spectralBalanceScore?: number;
  ambientAssetId?: string;
  suggestedPatchGainDb: number;
  patchIntervals: Array<{
    startSeconds: number;
    durationSeconds: number;
  }>;
}

/**
 * Puente Sonoro Diegético o Ambiental (REQ-062)
 */
export interface SoundBridge {
  id: string;
  assetId: string;
  fromSceneId: string;
  toSceneId: string;
  visualCutTimestamp: number;
  leadDurationSeconds: number;
  tailDurationSeconds: number;
  attenuationDb: number;
  category: "ENVIRONMENTAL" | "TRAFFIC" | "WEATHER" | "MECHANICAL" | "CROWD" | "MUSIC_REVERB";
}

/**
 * Evento de Puntuación de Audio (REQ-069)
 */
export interface AudioPunctuationEvent {
  id: string;
  type: AudioPunctuationType;
  timestampSeconds: number;
  associatedBeatType: string;
  assetId?: string;
  gainDb: number;
  durationSeconds: number;
}
