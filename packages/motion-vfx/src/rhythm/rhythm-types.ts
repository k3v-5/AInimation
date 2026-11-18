import { z } from "zod";

/**
 * Modos de destello o corte rápido en ráfaga (Machine-Gun Flash Cut).
 */
export const FlashCutModeSchema = z.enum([
  "MEDIA_INTERLEAVE",   // Alternancia cíclica entre diferentes clips de video
  "WHITE_STROBE",      // Fotogramas de destello en blanco puro
  "CRIMSON_STROBE",    // Fotogramas de destello en rojo carmesí (#FF1424 TIME style)
  "CHROMATIC_INVERT",  // Inversión cromática estroboscópica (diferencia clásica)
]);

export type FlashCutMode = z.infer<typeof FlashCutModeSchema>;

/**
 * Subdivisión de métrica musical cuantizada.
 */
export const MusicalSubdivisionSchema = z.enum([
  "WHOLE",             // Redonda (1 bar)
  "HALF",              // Blanca (1/2 bar)
  "QUARTER",           // Negra (1 beat)
  "EIGHTH",            // Corchea (1/2 beat)
  "SIXTEENTH",         // Semicorchea (1/4 beat)
  "THIRTY_SECOND",     // Fusa (1/8 beat)
  "QUARTER_TRIPLET",   // Tresillo de negra
  "EIGHTH_TRIPLET",    // Tresillo de corchea
  "SIXTEENTH_TRIPLET", // Tresillo de semicorchea
]);

export type MusicalSubdivision = z.infer<typeof MusicalSubdivisionSchema>;

/**
 * Intervalo de corte atómico generado dentro de una ráfaga.
 */
export const AtomicCutSliceSchema = z.object({
  sliceIndex: z.number().int().nonnegative(),
  startTimeSeconds: z.number().nonnegative(),
  endTimeSeconds: z.number().positive(),
  durationFrames: z.number().int().positive(),
  assignedLayerIndex: z.number().int().nonnegative().optional(),
  colorHex: z.string().optional(),
});

export type AtomicCutSlice = z.infer<typeof AtomicCutSliceSchema>;

/**
 * Especificación de una ráfaga de cortes ultra-rápidos (Machine-Gun Flash Cuts).
 */
export const MachineGunBurstSpecSchema = z.object({
  id: z.string().default("burst"),
  startTimeSeconds: z.number().nonnegative(),
  durationSeconds: z.number().positive(),
  frameHold: z.number().int().min(1).max(6).default(1), // 1 a 3 fotogramas por corte
  mode: FlashCutModeSchema.default("WHITE_STROBE"),
  mediaLayerIndices: z.array(z.number().int().nonnegative()).optional(),
  colorHex: z.string().default("#FFFFFF"),
});

export type MachineGunBurstSpec = z.output<typeof MachineGunBurstSpecSchema>;
export type MachineGunBurstSpecInput = z.input<typeof MachineGunBurstSpecSchema>;

/**
 * Especificación para Blackout Drop y Audio Vacuum (apagón y succión previa al drop).
 */
export const BlackoutVacuumSpecSchema = z.object({
  id: z.string().default("blackout_vacuum"),
  dropTimeSeconds: z.number().positive(),
  vacuumDurationSeconds: z.number().min(0.04).max(1.0).default(0.16), // Ventana de vacío
  impactFlashFrame: z.boolean().default(true),                       // Flash de 1 fotograma en el drop
  flashColorHex: z.string().default("#FFFFFF"),
});

export type BlackoutVacuumSpec = z.output<typeof BlackoutVacuumSpecSchema>;
export type BlackoutVacuumSpecInput = z.input<typeof BlackoutVacuumSpecSchema>;

/**
 * Punto de corte sincopado individual sobre la línea de tiempo.
 */
export const SyncopatedCutPointSchema = z.object({
  timeSeconds: z.number().nonnegative(),
  mediaAssetPath: z.string().min(1),
  sourceInPointSeconds: z.number().nonnegative().default(0.0),
  durationSeconds: z.number().positive(),
});

export type SyncopatedCutPoint = z.output<typeof SyncopatedCutPointSchema>;
export type SyncopatedCutPointInput = z.input<typeof SyncopatedCutPointSchema>;

/**
 * Especificación de secuencia rítmica sincopada.
 */
export const SyncopatedSequenceSpecSchema = z.object({
  id: z.string().default("syncopated_sequence"),
  bpm: z.number().positive().default(120.0),
  fps: z.number().positive().default(30.0),
  cuts: z.array(SyncopatedCutPointSchema),
});

export type SyncopatedSequenceSpec = z.output<typeof SyncopatedSequenceSpecSchema>;
export type SyncopatedSequenceSpecInput = z.input<typeof SyncopatedSequenceSpecSchema>;

/**
 * Plan unificado de ritmo y montaje ultra-rápido.
 */
export const RhythmPlanSchema = z.object({
  id: z.string().min(1),
  bpm: z.number().positive(),
  fps: z.number().positive(),
  bursts: z.array(MachineGunBurstSpecSchema).default([]),
  blackouts: z.array(BlackoutVacuumSpecSchema).default([]),
  syncopatedCuts: z.array(SyncopatedCutPointSchema).default([]),
  extendScriptLines: z.array(z.string()),
  checksumSha256: z.string().length(64),
});

export type RhythmPlan = z.infer<typeof RhythmPlanSchema>;
