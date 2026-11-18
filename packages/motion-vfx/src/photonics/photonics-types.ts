import { z } from "zod";

/**
 * Operadores canónicos de ADBE Echo
 */
export const EchoOperatorSchema = z.enum(["MAXIMUM", "ADD", "SCREEN", "COMPOSITE_IN_BACK"]);
export type EchoOperator = z.infer<typeof EchoOperatorSchema>;

/**
 * Especificación de Shutter Drag & Kinetic Ghosting (arrastre de obturador lento)
 */
export const ShutterDragSpecSchema = z.object({
  id: z.string(),
  startTimeSeconds: z.number().nonnegative(),
  durationSeconds: z.number().positive(),
  echoCount: z.number().int().min(1).max(20).default(5),
  echoTimeStepSeconds: z.number().min(-0.2).max(-0.005).default(-0.033),
  decay: z.number().min(0.05).max(1.0).default(0.75),
  blendOperator: EchoOperatorSchema.default("MAXIMUM"),
  chromaticDispersion: z.boolean().default(false),
});
export type ShutterDragSpec = z.infer<typeof ShutterDragSpecSchema>;
export type ShutterDragSpecInput = z.input<typeof ShutterDragSpecSchema>;

/**
 * Especificación de Anamorphic Streak Flare (haz de luz anamórfico horizontal)
 */
export const AnamorphicStreakSpecSchema = z.object({
  id: z.string(),
  startTimeSeconds: z.number().nonnegative().optional(),
  durationSeconds: z.number().positive().optional(),
  thresholdPercent: z.number().min(40).max(99).default(80),
  streakLength: z.number().min(10).max(600).default(200),
  directionDegrees: z.number().default(90.0), // Horizontal anamórfico
  tintColor: z.tuple([
    z.number().min(0).max(1),
    z.number().min(0).max(1),
    z.number().min(0).max(1),
  ]).default([0.0, 0.9, 1.0]), // Cian neón por defecto
  intensity: z.number().positive().default(1.0),
});
export type AnamorphicStreakSpec = z.infer<typeof AnamorphicStreakSpecSchema>;
export type AnamorphicStreakSpecInput = z.input<typeof AnamorphicStreakSpecSchema>;

/**
 * Puntas de difracción para filtros de prisma estelar
 */
export const PrismStarPointsSchema = z.union([z.literal(4), z.literal(6)]);
export type PrismStarPoints = z.infer<typeof PrismStarPointsSchema>;

/**
 * Especificación de Prism Star Diffraction (Cross-Screen / Star Filter)
 */
export const PrismStarSpecSchema = z.object({
  id: z.string(),
  startTimeSeconds: z.number().nonnegative().optional(),
  durationSeconds: z.number().positive().optional(),
  points: PrismStarPointsSchema.default(4),
  thresholdPercent: z.number().min(40).max(99).default(85),
  starLength: z.number().min(10).max(300).default(80),
  intensity: z.number().positive().default(1.0),
  rotationDegrees: z.number().default(45.0),
});
export type PrismStarSpec = z.infer<typeof PrismStarSpecSchema>;
export type PrismStarSpecInput = z.input<typeof PrismStarSpecSchema>;

/**
 * Paletas de falso color FLIR / Térmico Infrarrojo
 */
export const FlirPaletteSchema = z.enum(["IRONBOW", "RAINBOW", "WHITE_HOT", "ARCTIC"]);
export type FlirPalette = z.infer<typeof FlirPaletteSchema>;

/**
 * Especificación de FLIR / Infrarrojo Thermal Vision
 */
export const FlirThermalSpecSchema = z.object({
  id: z.string(),
  startTimeSeconds: z.number().nonnegative().optional(),
  durationSeconds: z.number().positive().optional(),
  palette: FlirPaletteSchema.default("IRONBOW"),
  thermalNoiseIntensity: z.number().min(0).max(50).default(12),
  edgeEnhancement: z.boolean().default(true),
});
export type FlirThermalSpec = z.infer<typeof FlirThermalSpecSchema>;
export type FlirThermalSpecInput = z.input<typeof FlirThermalSpecSchema>;

/**
 * Plan de Cinematografía Fotónica Nocturna consolidado
 */
export const PhotonicsPlanSchema = z.object({
  id: z.string(),
  shutterDrag: ShutterDragSpecSchema.optional(),
  anamorphicStreak: AnamorphicStreakSpecSchema.optional(),
  prismStar: PrismStarSpecSchema.optional(),
  flirThermal: FlirThermalSpecSchema.optional(),
  extendScriptLines: z.array(z.string()),
  checksumSha256: z.string(),
});
export type PhotonicsPlan = z.infer<typeof PhotonicsPlanSchema>;
