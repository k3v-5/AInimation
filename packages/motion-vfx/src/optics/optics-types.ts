import { z } from "zod";

/**
 * Esquema para un Snap / Crash Zoom percusivo con rebote inercial.
 */
export const SnapZoomSpecSchema = z.object({
  id: z.string().min(1),
  triggerTimeSeconds: z.number().nonnegative(),
  durationSeconds: z.number().positive().default(0.20),
  startScalePercent: z.number().positive().default(100.0),
  peakScalePercent: z.number().positive().default(185.0),
  settleScalePercent: z.number().positive().default(106.0),
  dampingRatio: z.number().min(0.1).max(2.0).default(0.55),
  frequencyHz: z.number().positive().default(6.0),
  overshootPercent: z.number().min(0.0).default(15.0),
});

export type SnapZoomSpec = z.infer<typeof SnapZoomSpecSchema>;

/**
 * Esquema para emulación de lente Fisheye y óptica gran angular extrema.
 */
export const FisheyeLensSpecSchema = z.object({
  id: z.string().min(1),
  distortionFactor: z.number().min(-100.0).max(100.0).default(65.0), // Factor de abombamiento de barril
  chromaticAberrationPx: z.number().min(0.0).max(50.0).default(8.0), // Separación radial RGB en bordes
  vignetteAmount: z.number().min(0.0).max(1.0).default(0.45),
  centerOffsetX: z.number().default(0.0),
  centerOffsetY: z.number().default(0.0),
});

export type FisheyeLensSpec = z.infer<typeof FisheyeLensSpecSchema>;

/**
 * Esquema para el efecto Dolly Zoom (Vértigo).
 */
export const DollyZoomSpecSchema = z.object({
  id: z.string().min(1),
  startTimeSeconds: z.number().nonnegative(),
  durationSeconds: z.number().positive(),
  initialFovDegrees: z.number().min(10.0).max(120.0).default(35.0), // Teleobjetivo
  finalFovDegrees: z.number().min(10.0).max(140.0).default(85.0),   // Gran angular
  subjectScaleLock: z.boolean().default(true),
});

export type DollyZoomSpec = z.infer<typeof DollyZoomSpecSchema>;

/**
 * Esquema para latigazo de cámara (Whip Pan) con desenfoque de movimiento direccional.
 */
export const WhipPanSpecSchema = z.object({
  id: z.string().min(1),
  triggerTimeSeconds: z.number().nonnegative(),
  durationSeconds: z.number().positive().default(0.18),
  direction: z.enum(["LEFT", "RIGHT", "UP", "DOWN"]).default("RIGHT"),
  travelAngleDegrees: z.number().default(0.0),
  blurIntensityPx: z.number().positive().default(45.0),
});

export type WhipPanSpec = z.infer<typeof WhipPanSpecSchema>;

/**
 * Plan unificado de ópticas y cámara para After Effects.
 */
export const OpticsPlanSchema = z.object({
  id: z.string().min(1),
  targetCompWidth: z.number().positive().default(1920),
  targetCompHeight: z.number().positive().default(1080),
  fps: z.number().positive().default(30.0),
  snapZooms: z.array(SnapZoomSpecSchema).default([]),
  fisheye: FisheyeLensSpecSchema.optional(),
  dollyZooms: z.array(DollyZoomSpecSchema).default([]),
  whipPans: z.array(WhipPanSpecSchema).default([]),
  extendScriptLines: z.array(z.string()),
  checksumSha256: z.string().length(64),
});

export type OpticsPlan = z.infer<typeof OpticsPlanSchema>;
