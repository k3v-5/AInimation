import { z } from "zod";

/**
 * Dirección de rotación en giroscopio centrífugo.
 */
export const GyroDirectionSchema = z.enum(["CLOCKWISE", "COUNTER_CLOCKWISE"]);
export type GyroDirection = z.infer<typeof GyroDirectionSchema>;

/**
 * Esquema para Centrifugal Gyro Barrel Roll (rotación en eje Z estilo Hanumankind / Big Dawgs).
 */
export const CentrifugalGyroRollSpecSchema = z.object({
  id: z.string().default("gyro_roll"),
  startTimeSeconds: z.number().nonnegative().default(0.0),
  durationSeconds: z.number().min(0.2).max(10.0).default(1.5),
  totalRollDegrees: z.number().min(90).max(1440).default(360),       // 180, 360, 720
  direction: GyroDirectionSchema.default("CLOCKWISE"),
  mirrorEdges: z.boolean().default(true),                            // Motion Tile en espejo
  scaleBufferPercent: z.number().min(141.42).max(250).default(142.0), // Circunscrito sqrt(2) * 100
  easing: z.enum(["SMOOTH", "EXPONENTIAL", "LINEAR"]).default("SMOOTH"),
});

export type CentrifugalGyroRollSpec = z.output<typeof CentrifugalGyroRollSpecSchema>;
export type CentrifugalGyroRollSpecInput = z.input<typeof CentrifugalGyroRollSpecSchema>;

/**
 * Dirección del barrido rápido de cámara (Whip-Pan / Swish-Pan).
 */
export const WhipDirectionSchema = z.enum([
  "PAN_LEFT",
  "PAN_RIGHT",
  "TILT_UP",
  "TILT_DOWN",
]);
export type WhipDirection = z.infer<typeof WhipDirectionSchema>;

/**
 * Esquema para Directional Whip-Pan Match Cut (transición por barrido ultrarrápido).
 */
export const WhipPanMatchCutSpecSchema = z.object({
  id: z.string().default("whip_pan_match_cut"),
  cutTimeSeconds: z.number().positive(),
  transitionDurationSeconds: z.number().min(0.15).max(0.60).default(0.30),
  direction: WhipDirectionSchema.default("PAN_RIGHT"),
  maxBlurLengthPx: z.number().min(80).max(300).default(180),
  seamlessOffsetPx: z.number().min(300).max(1800).default(800),
});

export type WhipPanMatchCutSpec = z.output<typeof WhipPanMatchCutSpecSchema>;
export type WhipPanMatchCutSpecInput = z.input<typeof WhipPanMatchCutSpecSchema>;

/**
 * Dirección del tirón de foco (Lens Breathing).
 */
export const FocusPullDirectionSchema = z.enum(["NEAR_TO_FAR", "FAR_TO_NEAR"]);
export type FocusPullDirection = z.infer<typeof FocusPullDirectionSchema>;

/**
 * Esquema para emulación de respiración óptica analógica (Lens Breathing).
 */
export const LensBreathingSpecSchema = z.object({
  id: z.string().default("lens_breathing"),
  startTimeSeconds: z.number().nonnegative().default(0.0),
  durationSeconds: z.number().min(0.2).max(3.0).default(0.8),
  breatheScalePercent: z.number().min(0.5).max(4.0).default(1.8), // 1.8% de respiración focal
  focusPullDirection: FocusPullDirectionSchema.default("NEAR_TO_FAR"),
  lensRackBlurPx: z.number().min(0).max(30).default(8.0),
});

export type LensBreathingSpec = z.output<typeof LensBreathingSpecSchema>;
export type LensBreathingSpecInput = z.input<typeof LensBreathingSpecSchema>;

/**
 * Plan consolidado de mecánica de cámara y ópticas dinámicas.
 */
export const DynamicMechanicsPlanSchema = z.object({
  id: z.string().min(1),
  gyroRoll: CentrifugalGyroRollSpecSchema.optional(),
  whipPan: WhipPanMatchCutSpecSchema.optional(),
  lensBreathing: LensBreathingSpecSchema.optional(),
  extendScriptLines: z.array(z.string()),
  checksumSha256: z.string().length(64),
});

export type DynamicMechanicsPlan = z.infer<typeof DynamicMechanicsPlanSchema>;
