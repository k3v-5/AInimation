import { z } from "zod";

/**
 * Paletas para emulación de shader de Cromo Líquido.
 */
export const ChromePaletteSchema = z.enum([
  "PLATINUM",      // Espejo cromado puro plateado de alta reflexión
  "ACID_EMERALD",  // Cromo verdoso fluorescente experimental (Ralphie Choo / Y2K)
  "MOLTEN_GOLD",   // Oro líquido pulido
  "CUSTOM",
]);

export type ChromePalette = z.infer<typeof ChromePaletteSchema>;

/**
 * Esquema para tipografía brutalista editorial (TIME / Tyler Style).
 */
export const BrutalistTypeSpecSchema = z.object({
  id: z.string().default("brutalist_title"),
  text: z.string().min(1),
  fontFamily: z.string().default("Impact"),
  fontSizePx: z.number().min(40).max(600).default(220),
  verticalStretchPercent: z.number().min(100).max(200).default(135), // Estiramiento anamórfico Y (135%)
  tracking: z.number().min(-200).max(100).default(-60),              // Interletraje negativo editorial
  colorHex: z.string().default("#FF1424"),                           // Rojo carmesí TIME / Tyler
  allCaps: z.boolean().default(true),
  boxPaddingPercent: z.number().min(0).max(50).default(5),
});

export type BrutalistTypeSpec = z.output<typeof BrutalistTypeSpecSchema>;
export type BrutalistTypeSpecInput = z.input<typeof BrutalistTypeSpecSchema>;

/**
 * Esquema para emulación de Cromo Líquido reflectante (Liquid Chrome Shader).
 */
export const LiquidChromeSpecSchema = z.object({
  id: z.string().default("liquid_chrome"),
  bevelDepthPx: z.number().min(1.0).max(12.0).default(4.5),
  turbulentAmount: z.number().min(0.0).max(40.0).default(14.0),
  turbulentSize: z.number().min(5.0).max(60.0).default(20.0),
  evolutionSpeed: z.number().min(0.0).max(10.0).default(1.5),
  chromePalette: ChromePaletteSchema.default("PLATINUM"),
  tintRgb: z.tuple([z.number(), z.number(), z.number()]).optional(),
});

export type LiquidChromeSpec = z.output<typeof LiquidChromeSpecSchema>;
export type LiquidChromeSpecInput = z.input<typeof LiquidChromeSpecSchema>;

/**
 * Esquema para anclaje en perspectiva 3D (Spatial Geometry Anchoring).
 */
export const PerspectiveAnchorSpecSchema = z.object({
  id: z.string().default("perspective_anchor"),
  position3D: z.tuple([z.number(), z.number(), z.number()]).default([540, 960, 0]),
  rotation3D: z.tuple([z.number(), z.number(), z.number()]).default([0, 0, 0]), // [RotX, RotY, RotZ]
  vanishingPointAlign: z.enum(["CENTER", "FLOOR_RECEDING", "WALL_LEFT", "WALL_RIGHT"]).default("CENTER"),
});

export type PerspectiveAnchorSpec = z.output<typeof PerspectiveAnchorSpecSchema>;
export type PerspectiveAnchorSpecInput = z.input<typeof PerspectiveAnchorSpecSchema>;

/**
 * Esquema para animación de impacto percusivo (Word Slam con rebote subamortiguado).
 */
export const WordSlamSpecSchema = z.object({
  id: z.string().default("word_slam"),
  triggerTimeSeconds: z.number().nonnegative().default(0.0),
  durationSeconds: z.number().min(0.15).max(1.0).default(0.35),
  initialScalePercent: z.number().min(150).max(400).default(260),
  dampingRatio: z.number().min(0.2).max(0.95).default(0.55),
  naturalFrequency: z.number().min(10.0).max(50.0).default(24.0),
});

export type WordSlamSpec = z.output<typeof WordSlamSpecSchema>;
export type WordSlamSpecInput = z.input<typeof WordSlamSpecSchema>;

/**
 * Plan consolidado de tipografía cinética de vanguardia.
 */
export const KineticTypographyPlanSchema = z.object({
  id: z.string().min(1),
  brutalist: BrutalistTypeSpecSchema,
  chrome: LiquidChromeSpecSchema.optional(),
  perspective: PerspectiveAnchorSpecSchema.optional(),
  slam: WordSlamSpecSchema.optional(),
  extendScriptLines: z.array(z.string()),
  checksumSha256: z.string().length(64),
});

export type KineticTypographyPlan = z.infer<typeof KineticTypographyPlanSchema>;
