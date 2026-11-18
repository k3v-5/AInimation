import { z } from "zod";

/**
 * Esquema para modulación de tasa de cuadros (Posterize Time).
 */
export const PosterizeTimeSpecSchema = z.object({
  id: z.string().min(1),
  targetFps: z.number().int().min(1).max(120).default(12), // 8, 12, 15, 24
  inTimeSeconds: z.number().nonnegative().optional(),
  outTimeSeconds: z.number().positive().optional(),
});

export type PosterizeTimeSpec = z.infer<typeof PosterizeTimeSpecSchema>;

/**
 * Segmento individual dentro de una curva de Speed Ramping.
 */
export const SpeedRampSegmentSchema = z.object({
  startTimeSeconds: z.number().nonnegative(),
  endTimeSeconds: z.number().positive(),
  speedMultiplier: z.number().min(0.05).max(10.0), // ej. 3.0x (rápido) o 0.4x (cámara lenta)
  easing: z.enum(["BEZIER", "LINEAR", "EXPONENTIAL"]).default("BEZIER"),
});

export type SpeedRampSegment = z.infer<typeof SpeedRampSegmentSchema>;

/**
 * Esquema para Speed Ramping cuantizado y alineado a un drop o transiente musical.
 */
export const QuantizedSpeedRampSpecSchema = z.object({
  id: z.string().min(1),
  sourceClipDurationSeconds: z.number().positive(),
  targetBeatDropTimeSeconds: z.number().nonnegative(), // Momento donde clava la cámara lenta
  fastMultiplier: z.number().min(1.5).max(8.0).default(3.0), // 300%
  slowMultiplier: z.number().min(0.1).max(0.9).default(0.4), // 40%
  transitionDurationSeconds: z.number().positive().default(0.25),
  totalTimelineDurationSeconds: z.number().positive(),
});

export type QuantizedSpeedRampSpec = z.infer<typeof QuantizedSpeedRampSpecSchema>;

/**
 * Esquema para Stutter Freeze (micro-congelamiento percusivo).
 */
export const StutterFreezeSpecSchema = z.object({
  id: z.string().min(1),
  triggerTimeSeconds: z.number().nonnegative(),
  freezeDurationSeconds: z.number().positive().default(0.10), // ~3 fotogramas a 30fps
  postResumeSpeedMultiplier: z.number().positive().default(1.0),
});

export type StutterFreezeSpec = z.infer<typeof StutterFreezeSpecSchema>;

/**
 * Keyframe discreto para la propiedad Time Remap de After Effects.
 */
export const TimeRemapKeyframeSchema = z.object({
  timelineSeconds: z.number().nonnegative(),
  sourceSeconds: z.number().nonnegative(),
});

export type TimeRemapKeyframe = z.infer<typeof TimeRemapKeyframeSchema>;

/**
 * Plan consolidado de modulación temporal para After Effects.
 */
export const TemporalPlanSchema = z.object({
  id: z.string().min(1),
  posterizeTime: PosterizeTimeSpecSchema.optional(),
  speedRamps: z.array(QuantizedSpeedRampSpecSchema).default([]),
  stutters: z.array(StutterFreezeSpecSchema).default([]),
  timeRemapKeyframes: z.array(TimeRemapKeyframeSchema).default([]),
  extendScriptLines: z.array(z.string()),
  checksumSha256: z.string().length(64),
});

export type TemporalPlan = z.infer<typeof TemporalPlanSchema>;
