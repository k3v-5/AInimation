import { z } from "zod";

/**
 * Calibre de película analógica emulado.
 */
export const FilmGaugeSchema = z.enum(["16MM", "35MM"]);
export type FilmGauge = z.infer<typeof FilmGaugeSchema>;

/**
 * Esquema para grano de película analógica procedural.
 */
export const FilmGrainSpecSchema = z.object({
  id: z.string().default("film_grain"),
  gauge: FilmGaugeSchema.default("16MM"),
  intensity: z.number().min(0.0).max(1.0).default(0.35),
  luminanceCoupling: z.boolean().default(true), // Modulación por tonos medios
  colorNoise: z.boolean().default(false),       // false = monocromático (haluros puros)
});

export type FilmGrainSpec = z.output<typeof FilmGrainSpecSchema>;
export type FilmGrainSpecInput = z.input<typeof FilmGrainSpecSchema>;

/**
 * Esquema para Film Halation (destellos carmesí en bordes de altas luces).
 */
export const FilmHalationSpecSchema = z.object({
  id: z.string().default("film_halation"),
  threshold: z.number().min(0.50).max(0.98).default(0.82), // Umbral de altas luces
  radiusPx: z.number().min(5.0).max(80.0).default(26.0),    // Radio de dispersión
  intensity: z.number().min(0.0).max(1.0).default(0.70),
  tintRgb: z.tuple([z.number(), z.number(), z.number()]).default([1.0, 0.08, 0.05]), // Rojo carmesí
});

export type FilmHalationSpec = z.output<typeof FilmHalationSpecSchema>;
export type FilmHalationSpecInput = z.input<typeof FilmHalationSpecSchema>;

/**
 * Esquema para fluctuación de obturador rotativo (Shutter Flicker) y Gate Weave.
 */
export const ShutterFlickerSpecSchema = z.object({
  id: z.string().default("shutter_flicker"),
  frequencyHz: z.number().min(6.0).max(30.0).default(18.0),
  amplitudeEv: z.number().min(0.01).max(0.15).default(0.04), // Fluctuación de exposición
  gateWeavePx: z.number().min(0.0).max(5.0).default(1.2),    // Micro-vaivén de arrastre
});

export type ShutterFlickerSpec = z.output<typeof ShutterFlickerSpecSchema>;
export type ShutterFlickerSpecInput = z.input<typeof ShutterFlickerSpecSchema>;

/**
 * Perfiles cromáticos de autor inspirados en directores y artistas de culto.
 */
export const AuteurProfileSchema = z.enum([
  "TYLER_PASTEL_70S",        // Tonos cálidos, verdes menta, sombras sepia/turquesa
  "KENDRICK_BLEACH_BYPASS_BW",// Retención de plata, alto contraste, negros profundos
  "RALPHIE_MINIDV_ACID",     // Y2K analógico/digital, saturación ácida, grano marcado
  "CUSTOM",
]);

export type AuteurProfile = z.infer<typeof AuteurProfileSchema>;

/**
 * Esquema para graduación de color de autor.
 */
export const AuteurColorGradingSpecSchema = z.object({
  id: z.string().default("auteur_grading"),
  profile: AuteurProfileSchema.default("TYLER_PASTEL_70S"),
  saturation: z.number().min(0.0).max(2.5).default(1.15),
  contrast: z.number().min(0.5).max(2.5).default(1.10),
  liftPedestal: z.number().min(-0.2).max(0.3).default(0.04), // Sombras levantadas
  shadowTintRgb: z.tuple([z.number(), z.number(), z.number()]).optional(),
  highlightTintRgb: z.tuple([z.number(), z.number(), z.number()]).optional(),
});

export type AuteurColorGradingSpec = z.output<typeof AuteurColorGradingSpecSchema>;
export type AuteurColorGradingSpecInput = z.input<typeof AuteurColorGradingSpecSchema>;

/**
 * Plan consolidado de emulación de película y color de autor.
 */
export const FilmPlanSchema = z.object({
  id: z.string().min(1),
  grain: FilmGrainSpecSchema.optional(),
  halation: FilmHalationSpecSchema.optional(),
  flicker: ShutterFlickerSpecSchema.optional(),
  colorGrading: AuteurColorGradingSpecSchema.optional(),
  extendScriptLines: z.array(z.string()),
  checksumSha256: z.string().length(64),
});

export type FilmPlan = z.infer<typeof FilmPlanSchema>;

