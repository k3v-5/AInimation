import { z } from "zod";

/**
 * Esquema para Snorricam Body Lock (cámara anclada rígidamente al torso/cabeza del sujeto).
 */
export const SnorricamSpecSchema = z.object({
  id: z.string().default("snorricam_lock"),
  subjectAnchorPoint: z.tuple([z.number(), z.number()]).default([540, 800]), // [X, Y] inicial del sujeto
  compensateRotation: z.boolean().default(true),                            // Cancelar giros de cabeza
  stabilizationSmoothingFrames: z.number().int().min(0).max(30).default(0), // 0 = rigidez robótica absoluta
  scaleBufferPercent: z.number().min(100).max(200).default(125),           // Margen para evitar bordes vacíos
  motionTileMirror: z.boolean().default(true),                              // Espejado procedural en bordes
});

export type SnorricamSpec = z.output<typeof SnorricamSpecSchema>;
export type SnorricamSpecInput = z.input<typeof SnorricamSpecSchema>;

/**
 * Esquema para Infinite Zoom Portal (transición de agujero de gusano super-exponencial).
 */
export const InfiniteZoomPortalSpecSchema = z.object({
  id: z.string().default("infinite_zoom_portal"),
  startTimeSeconds: z.number().nonnegative().default(0.0),
  durationSeconds: z.number().min(0.2).max(4.0).default(1.5),
  portalCenterPoint: z.tuple([z.number(), z.number()]).default([540, 960]), // Punto focal hacia donde colapsa
  maxScalePercent: z.number().min(500).max(20000).default(6000),             // Zoom de hasta 6000%
  accelerationExponent: z.number().min(1.5).max(6.0).default(3.0),          // Super-aceleración cúbica
  destinationSceneOpacityTrigger: z.number().min(0.5).max(1.0).default(0.85),
});

export type InfiniteZoomPortalSpec = z.output<typeof InfiniteZoomPortalSpecSchema>;
export type InfiniteZoomPortalSpecInput = z.input<typeof InfiniteZoomPortalSpecSchema>;

/**
 * Dirección de avance del oclusor en Parallax Occlusion Wipe.
 */
export const OcclusionDirectionSchema = z.enum([
  "LEFT_TO_RIGHT",
  "RIGHT_TO_LEFT",
  "TOP_TO_BOTTOM",
  "BOTTOM_TO_TOP",
]);

export type OcclusionDirection = z.infer<typeof OcclusionDirectionSchema>;

/**
 * Esquema para Parallax Occlusion Wipe (corte por oclusión de transeúnte o columna estilo Hiro Murai).
 */
export const ParallaxOcclusionWipeSpecSchema = z.object({
  id: z.string().default("parallax_occlusion_wipe"),
  startTimeSeconds: z.number().nonnegative().default(0.0),
  durationSeconds: z.number().min(0.15).max(3.0).default(0.75),
  direction: OcclusionDirectionSchema.default("LEFT_TO_RIGHT"),
  featherPx: z.number().min(0).max(120).default(35),                 // Calado suave en el borde del oclusor
  curvatureDistortion: z.number().min(0.0).max(100.0).default(15.0), // Silueta orgánica curva
});

export type ParallaxOcclusionWipeSpec = z.output<typeof ParallaxOcclusionWipeSpecSchema>;
export type ParallaxOcclusionWipeSpecInput = z.input<typeof ParallaxOcclusionWipeSpecSchema>;

/**
 * Plan unificado de cinematografía espacial de autor.
 */
export const SpatialCinematographyPlanSchema = z.object({
  id: z.string().min(1),
  snorricam: SnorricamSpecSchema.optional(),
  portal: InfiniteZoomPortalSpecSchema.optional(),
  occlusionWipe: ParallaxOcclusionWipeSpecSchema.optional(),
  extendScriptLines: z.array(z.string()),
  checksumSha256: z.string().length(64),
});

export type SpatialCinematographyPlan = z.infer<typeof SpatialCinematographyPlanSchema>;
