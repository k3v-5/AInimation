import { z } from "zod";

/**
 * Modos de renderizado de fotogramas de impacto manga
 */
export const ImpactFrameModeSchema = z.enum(["INVERT_NEGATIVE", "HIGH_CONTRAST_BW", "CHROMATIC_FLASH"]);
export type ImpactFrameMode = z.infer<typeof ImpactFrameModeSchema>;

/**
 * Especificación de 1-Frame Manga Impact Frame
 */
export const ImpactFrameSpecSchema = z.object({
  id: z.string(),
  impactTimeSeconds: z.number().nonnegative(),
  frameDuration: z.union([z.literal(1), z.literal(2)]).default(1),
  mode: ImpactFrameModeSchema.default("INVERT_NEGATIVE"),
});
export type ImpactFrameSpec = z.infer<typeof ImpactFrameSpecSchema>;
export type ImpactFrameSpecInput = z.input<typeof ImpactFrameSpecSchema>;

/**
 * Especificación de Speed Lines Radiales Procedurales (Anime Kinetics)
 */
export const SpeedLinesSpecSchema = z.object({
  id: z.string(),
  startTimeSeconds: z.number().nonnegative(),
  durationSeconds: z.number().positive(),
  centerPoint: z.tuple([z.number(), z.number()]).default([540, 960]),
  innerRadiusPx: z.number().min(20).max(1200).default(280),
  lineCount: z.number().int().min(15).max(180).default(60),
  color: z.tuple([
    z.number().min(0).max(1),
    z.number().min(0).max(1),
    z.number().min(0).max(1),
  ]).default([1.0, 1.0, 1.0]),
  boilFps: z.number().min(6).max(30).default(12),
  density: z.number().min(0.1).max(1.0).default(0.6),
});
export type SpeedLinesSpec = z.infer<typeof SpeedLinesSpecSchema>;
export type SpeedLinesSpecInput = z.input<typeof SpeedLinesSpecSchema>;

/**
 * Calibre de película y márgenes para perforaciones
 */
export const FilmGaugeSchema = z.enum(["35MM", "16MM"]);
export type FilmGauge = z.infer<typeof FilmGaugeSchema>;

export const SprocketSideSchema = z.enum(["LEFT", "RIGHT", "BOTH"]);
export type SprocketSide = z.infer<typeof SprocketSideSchema>;

/**
 * Especificación de 35mm / 16mm Sprocket Holes y Gate Weave Jitter
 */
export const SprocketHolesSpecSchema = z.object({
  id: z.string(),
  gauge: FilmGaugeSchema.default("35MM"),
  side: SprocketSideSchema.default("BOTH"),
  gateWeaveJitterPx: z.number().min(0).max(10).default(2.5),
  keyKodeText: z.string().default("EASTMAN 5219 48 1024"),
  opacity: z.number().min(0).max(100).default(90),
});
export type SprocketHolesSpec = z.infer<typeof SprocketHolesSpecSchema>;
export type SprocketHolesSpecInput = z.input<typeof SprocketHolesSpecSchema>;

/**
 * Dirección del rasgado de papel para transición de collage
 */
export const PaperTearDirectionSchema = z.enum(["HORIZONTAL", "VERTICAL", "DIAGONAL"]);
export type PaperTearDirection = z.infer<typeof PaperTearDirectionSchema>;

/**
 * Especificación de Paper Tear & Collage Cutout Wipe
 */
export const PaperTearSpecSchema = z.object({
  id: z.string(),
  startTimeSeconds: z.number().nonnegative(),
  durationSeconds: z.number().positive(),
  direction: PaperTearDirectionSchema.default("HORIZONTAL"),
  tearRoughness: z.number().min(5).max(100).default(35),
  fiberFringePx: z.number().min(1).max(50).default(12),
});
export type PaperTearSpec = z.infer<typeof PaperTearSpecSchema>;
export type PaperTearSpecInput = z.input<typeof PaperTearSpecSchema>;

/**
 * Especificación de Stop-Motion Doodle Boil
 */
export const DoodleBoilSpecSchema = z.object({
  id: z.string(),
  startTimeSeconds: z.number().nonnegative(),
  durationSeconds: z.number().positive(),
  boilFps: z.union([z.literal(8), z.literal(12)]).default(12),
  jitterAmplitudePx: z.number().min(1).max(20).default(4),
  strokeColor: z.tuple([
    z.number().min(0).max(1),
    z.number().min(0).max(1),
    z.number().min(0).max(1),
  ]).default([1.0, 1.0, 0.0]), // Amarillo neón
  strokeWidthPx: z.number().min(1).max(20).default(4),
});
export type DoodleBoilSpec = z.infer<typeof DoodleBoilSpecSchema>;
export type DoodleBoilSpecInput = z.input<typeof DoodleBoilSpecSchema>;

/**
 * Plan consolidado de Mixed-Media y Anime Kinetics
 */
export const MixedMediaPlanSchema = z.object({
  id: z.string(),
  fps: z.number().default(30.0),
  impactFrame: ImpactFrameSpecSchema.optional(),
  speedLines: SpeedLinesSpecSchema.optional(),
  sprocketHoles: SprocketHolesSpecSchema.optional(),
  paperTear: PaperTearSpecSchema.optional(),
  doodleBoil: DoodleBoilSpecSchema.optional(),
  extendScriptLines: z.array(z.string()),
  checksumSha256: z.string(),
});
export type MixedMediaPlan = z.infer<typeof MixedMediaPlanSchema>;
