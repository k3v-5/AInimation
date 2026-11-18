import { z } from "zod";

/**
 * Representa un transiente o impacto percusivo detectado en la señal de audio.
 */
export const AudioTransientSchema = z.object({
  id: z.string().min(1),
  timestampSeconds: z.number().nonnegative(),
  strength: z.number().min(0.0).max(1.0),
  isDownbeat: z.boolean().default(false),
  frequencyBand: z.enum(["SUB_BASS", "LOW", "MID", "HIGH", "FULL_SPECTRUM"]).default("FULL_SPECTRUM"),
  confidence: z.number().min(0.0).max(1.0).default(1.0),
});

export type AudioTransient = z.infer<typeof AudioTransientSchema>;

/**
 * Especificación de la cuadrícula musical de tempo (BPM Grid).
 */
export const BeatGridSpecSchema = z.object({
  bpm: z.number().min(20).max(300),
  timeSignature: z.enum(["4/4", "3/4", "6/8"]).default("4/4"),
  offsetSeconds: z.number().nonnegative().default(0.0),
  totalDurationSeconds: z.number().positive(),
  subdivision: z.number().int().min(1).max(8).default(1),
});

export type BeatGridSpec = z.infer<typeof BeatGridSpecSchema>;

/**
 * Modos de sincronización rítmica para corte audiovisual.
 */
export const BeatSyncModeSchema = z.enum([
  "EVERY_BEAT",       // Corta en cada tiempo (1, 2, 3, 4)
  "DOWNBEAT_ONLY",    // Corta solo al inicio de compás (tiempo 1)
  "HALF_BAR",         // Corta cada medio compás (tiempos 1 y 3 en 4/4)
  "SUBDIVISION_8TH",  // Corta en corcheas (ritmo rápido / acción)
  "DYNAMIC_ENERGY",   // Modula según la energía musical
]);

export type BeatSyncMode = z.infer<typeof BeatSyncModeSchema>;

/**
 * Decisión de corte alineada a un beat de la música.
 */
export const BeatSyncCutDecisionSchema = z.object({
  id: z.string().min(1),
  clipId: z.string().min(1),
  assetId: z.string().min(1),
  timelineStart: z.number().nonnegative(),
  timelineEnd: z.number().positive(),
  durationSeconds: z.number().positive(),
  sourceStart: z.number().nonnegative(),
  sourceEnd: z.number().positive(),
  snappedBeatTime: z.number().nonnegative(),
  driftSeconds: z.number(),
  isDownbeat: z.boolean(),
  pulseScale: z.number().optional(),
});

export type BeatSyncCutDecision = z.infer<typeof BeatSyncCutDecisionSchema>;

/**
 * Keyframe de pulsación reactiva de escala (Punch-in rítmico).
 */
export const ScalePulseKeyframeSchema = z.object({
  timeSeconds: z.number().nonnegative(),
  scalePercent: z.number().positive(),
});

export type ScalePulseKeyframe = z.infer<typeof ScalePulseKeyframeSchema>;

/**
 * Marcador de beat para ExtendScript y NLEs.
 */
export const BeatMarkerSchema = z.object({
  timeSeconds: z.number().nonnegative(),
  name: z.string().min(1),
  isDownbeat: z.boolean(),
  measureNumber: z.number().int().positive(),
  beatInMeasure: z.number().int().positive(),
});

export type BeatMarker = z.infer<typeof BeatMarkerSchema>;

/**
 * Plan completo de sincronización rítmica compilado.
 */
export const BeatSyncPlanSchema = z.object({
  id: z.string().min(1),
  bpm: z.number().positive(),
  timeSignature: z.string(),
  totalDurationSeconds: z.number().positive(),
  totalCuts: z.number().int().nonnegative(),
  cuts: z.array(BeatSyncCutDecisionSchema),
  markers: z.array(BeatMarkerSchema),
  scalePulses: z.array(ScalePulseKeyframeSchema),
  checksumSha256: z.string().length(64),
});

export type BeatSyncPlan = z.infer<typeof BeatSyncPlanSchema>;
