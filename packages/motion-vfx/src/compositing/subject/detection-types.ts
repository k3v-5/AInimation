import { z } from "zod";

/**
 * Coordenadas de Bounding Box 2D (normalizadas en [0.0, 1.0] o en píxeles).
 */
export const BoundingBox2DSchema = z.object({
  x: z.number(),
  y: z.number(),
  width: z.number().positive(),
  height: z.number().positive(),
});

export type BoundingBox2D = z.infer<typeof BoundingBox2DSchema>;

/**
 * Punto 2D para trazados poligonales de silueta.
 */
export const Point2DSchema = z.object({
  x: z.number(),
  y: z.number(),
});

export type Point2D = z.infer<typeof Point2DSchema>;

/**
 * Etiquetas semánticas soportadas para detección.
 */
export const SubjectLabelSchema = z.enum(["PERSON", "FACE", "OBJECT", "ANIMAL"]);
export type SubjectLabel = z.infer<typeof SubjectLabelSchema>;

/**
 * Sujeto u objeto detectado en un fotograma individual.
 */
export const DetectedSubjectSchema = z.object({
  id: z.string().min(1),
  frameIndex: z.number().int().nonnegative(),
  timestampSeconds: z.number().nonnegative(),
  label: SubjectLabelSchema.default("PERSON"),
  confidence: z.number().min(0.0).max(1.0).default(1.0),
  boundingBox: BoundingBox2DSchema,
  contourPoints: z.array(Point2DSchema).optional(),
  trackId: z.string().min(1),
});

export type DetectedSubject = z.infer<typeof DetectedSubjectSchema>;

/**
 * Trayectoria temporal de un sujeto a lo largo de un intervalo de tiempo.
 */
export const SubjectTrackSchema = z.object({
  trackId: z.string().min(1),
  label: SubjectLabelSchema,
  startFrame: z.number().int().nonnegative(),
  endFrame: z.number().int().nonnegative(),
  samples: z.array(DetectedSubjectSchema),
  smoothedTrajectory: z.array(Point2DSchema),
  averageBounds: BoundingBox2DSchema,
});

export type SubjectTrack = z.infer<typeof SubjectTrackSchema>;

/**
 * Configuración para el efecto "Texto Detrás del Sujeto" (Depth Layering Sandwich).
 */
export const TextBehindSubjectConfigSchema = z.object({
  id: z.string().min(1),
  sourceAssetPath: z.string().min(1),
  text: z.string().min(1),
  typography: z.object({
    fontFamily: z.string().default("Impact"),
    fontSize: z.number().positive().default(140),
    colorHex: z.string().default("#FF1424"), // Crimson por USER_DESIGN_PREFERENCES
    verticalStretchPercent: z.number().min(100).max(200).default(130), // 130% por USER_DESIGN_PREFERENCES
    tracking: z.number().default(-25),
  }),
  position: z.object({
    x: z.number(),
    y: z.number(),
  }),
  featherPx: z.number().min(0.0).default(8.0),
  backgroundBlurPx: z.number().min(0.0).default(0.0),
  inTimeSeconds: z.number().nonnegative().default(0.0),
  outTimeSeconds: z.number().positive(),
  detectedSubject: DetectedSubjectSchema.optional(),
});

export type TextBehindSubjectConfig = z.infer<typeof TextBehindSubjectConfigSchema>;

/**
 * Zona espacial designada para un sujeto en la composición de clones.
 */
export const SubjectZoneSchema = z.enum(["LEFT", "CENTER", "RIGHT", "CUSTOM"]);
export type SubjectZone = z.infer<typeof SubjectZoneSchema>;

/**
 * Configuración de una toma individual en la composición de clones.
 */
export const CloneTakeSpecSchema = z.object({
  takeId: z.string().min(1),
  assetPath: z.string().min(1),
  subjectZone: SubjectZoneSchema.default("CENTER"),
  customSplitXNormalized: z.number().min(0.0).max(1.0).optional(),
  inPointSeconds: z.number().nonnegative().default(0.0),
  durationSeconds: z.number().positive(),
  volumeDb: z.number().default(0.0),
  isMasterBackground: z.boolean().default(false),
});

export type CloneTakeSpec = z.infer<typeof CloneTakeSpecSchema>;

/**
 * Configuración maestra para el efecto Clones Multi-Toma.
 */
export const MultiTakeCloneConfigSchema = z.object({
  id: z.string().min(1),
  compWidth: z.number().positive().default(1920),
  compHeight: z.number().positive().default(1080),
  fps: z.number().positive().default(30.0),
  takes: z.array(CloneTakeSpecSchema).min(2),
  edgeFeatherPx: z.number().min(0.0).default(25.0),
  totalDurationSeconds: z.number().positive(),
  audioMode: z.enum(["ACTIVE_SPEAKER", "ALL_MIXED", "MASTER_ONLY"]).default("ACTIVE_SPEAKER"),
});

export type MultiTakeCloneConfig = z.infer<typeof MultiTakeCloneConfigSchema>;

/**
 * Plan unificado de composición compilado.
 */
export const SubjectCompositingPlanSchema = z.object({
  id: z.string().min(1),
  type: z.enum(["TEXT_BEHIND_SUBJECT", "MULTI_TAKE_CLONES"]),
  totalDurationSeconds: z.number().positive(),
  layersCount: z.number().int().positive(),
  extendScriptLines: z.array(z.string()),
  checksumSha256: z.string().length(64),
});

export type SubjectCompositingPlan = z.infer<typeof SubjectCompositingPlanSchema>;
