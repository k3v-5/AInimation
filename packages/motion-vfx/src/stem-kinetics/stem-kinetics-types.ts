import { z } from "zod";

/**
 * Especificación de reacción sísmica y física elástica a sub-bajos 808
 */
export const SubBassReactionSpecSchema = z.object({
  id: z.string(),
  hitTimesSeconds: z.array(z.number().nonnegative()).min(1),
  bounceScalePercent: z.number().min(1.0).max(30.0).default(8.0),
  decaySeconds: z.number().min(0.05).max(1.0).default(0.25),
  resonanceHz: z.number().min(4.0).max(30.0).default(12.0),
  chromaticAberrationPx: z.number().min(0).max(25.0).default(3.5),
});
export type SubBassReactionSpec = z.infer<typeof SubBassReactionSpecSchema>;
export type SubBassReactionSpecInput = z.input<typeof SubBassReactionSpecSchema>;

/**
 * Formatos canónicos de relación de aspecto
 */
export const AspectRatioFormatSchema = z.enum(["9:16", "1:1", "4:3", "16:9", "2.39:1"]);
export type AspectRatioFormat = z.infer<typeof AspectRatioFormatSchema>;

/**
 * Transición individual entre relaciones de aspecto
 */
export const AspectRatioTransitionSchema = z.object({
  targetFormat: AspectRatioFormatSchema,
  startTimeSeconds: z.number().nonnegative(),
  durationSeconds: z.number().positive(),
});
export type AspectRatioTransition = z.infer<typeof AspectRatioTransitionSchema>;

/**
 * Especificación de Dynamic Aspect Ratio Breathing & Letterboxing
 */
export const AspectRatioBreathingSpecSchema = z.object({
  id: z.string(),
  transitions: z.array(AspectRatioTransitionSchema).min(1),
  barColor: z.tuple([
    z.number().min(0).max(1),
    z.number().min(0).max(1),
    z.number().min(0).max(1),
  ]).default([0.0, 0.0, 0.0]),
});
export type AspectRatioBreathingSpec = z.infer<typeof AspectRatioBreathingSpecSchema>;
export type AspectRatioBreathingSpecInput = z.input<typeof AspectRatioBreathingSpecSchema>;

/**
 * Especificación de Datamosh Y2K & P-Frame Motion Vector Glitch
 */
export const DatamoshSpecSchema = z.object({
  id: z.string(),
  cutTimeSeconds: z.number().nonnegative(),
  durationSeconds: z.number().min(0.1).max(2.0).default(0.4),
  macroblockSize: z.union([z.literal(8), z.literal(16)]).default(16),
  displacementIntensity: z.number().min(5.0).max(250.0).default(60.0),
});
export type DatamoshSpec = z.infer<typeof DatamoshSpecSchema>;
export type DatamoshSpecInput = z.input<typeof DatamoshSpecSchema>;

/**
 * Plan unificado de Cinética de Stems de Audio, Aspect Ratio y Datamosh
 */
export const StemKineticsPlanSchema = z.object({
  id: z.string(),
  fps: z.number().default(30.0),
  subBass: SubBassReactionSpecSchema.optional(),
  aspectRatioBreathing: AspectRatioBreathingSpecSchema.optional(),
  datamosh: DatamoshSpecSchema.optional(),
  extendScriptLines: z.array(z.string()),
  checksumSha256: z.string(),
});
export type StemKineticsPlan = z.infer<typeof StemKineticsPlanSchema>;
