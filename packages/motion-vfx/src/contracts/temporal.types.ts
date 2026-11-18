import { z } from "zod";

/**
 * ============================================================================
 * FASE 1: CONTRATO DE TIPOS DEL CORE TEMPORAL
 * ============================================================================
 */

// --- 1. TIEMPO Y FRAMERATE ---

export const RationalTimeSchema = z.object({
  numerator: z.number().int().nonnegative(),
  denominator: z.number().int().positive(),
});
export type RationalTime = z.infer<typeof RationalTimeSchema>;

export const FrameRateSchema = z.object({
  numerator: z.number().int().positive(),
  denominator: z.number().int().positive(),
  fps: z.number().positive(),
});
export type FrameRate = z.infer<typeof FrameRateSchema>;

export const TimeUnits = {
  FRAMES: "frames",
  SECONDS: "seconds",
} as const;
export type TimeUnit = (typeof TimeUnits)[keyof typeof TimeUnits];

// --- 2. VALORES DE PROPIEDADES ---

export type ScalarValue = number;
export type Vector2DValue = [number, number];
export type Vector3DValue = [number, number, number];
export type ColorRGBAValue = [number, number, number, number]; // [0.0, 1.0]

export const PathPointSchema = z.object({
  vertex: z.tuple([z.number(), z.number()]),
  inTangent: z.tuple([z.number(), z.number()]),
  outTangent: z.tuple([z.number(), z.number()]),
});
export type PathPoint = z.infer<typeof PathPointSchema>;

export const PathShapeValueSchema = z.object({
  points: z.array(PathPointSchema),
  closed: z.boolean(),
});
export type PathShapeValue = z.infer<typeof PathShapeValueSchema>;

export type PropertyValue =
  | ScalarValue
  | Vector2DValue
  | Vector3DValue
  | ColorRGBAValue
  | PathShapeValue
  | string
  | boolean;

// --- 3. KEYFRAMES E INTERPOLACIÓN ---

export const InterpolationTypeEnum = z.enum(["HOLD", "LINEAR", "BEZIER"]);
export type InterpolationType = z.infer<typeof InterpolationTypeEnum>;

export const KeyframeEaseSchema = z.object({
  speed: z.number(), // Velocidad en unidades de valor por segundo
  influence: z.number().min(0.1).max(100), // Porcentaje de influencia (0.1% a 100%)
});
export type KeyframeEase = z.infer<typeof KeyframeEaseSchema>;

export const SpatialTangentSchema = z.object({
  x: z.number(),
  y: z.number(),
  z: z.number().optional(),
});
export type SpatialTangent = z.infer<typeof SpatialTangentSchema>;

export const KeyframeSchema = z.object({
  id: z.string(),
  time: z.number(), // En segundos
  frame: z.number().int().optional(), // Cuadro equivalente
  value: z.any(), // Tipado según la propiedad
  interpolationIn: InterpolationTypeEnum.default("LINEAR"),
  interpolationOut: InterpolationTypeEnum.default("LINEAR"),
  easeIn: KeyframeEaseSchema.optional(),
  easeOut: KeyframeEaseSchema.optional(),
  spatialIn: SpatialTangentSchema.optional(),
  spatialOut: SpatialTangentSchema.optional(),
});
export type Keyframe<T = PropertyValue> = z.infer<typeof KeyframeSchema> & {
  value: T;
};

// --- 4. PROPIEDAD ANIMABLE ---

export const PropertyTypeEnum = z.enum([
  "SCALAR",
  "VECTOR2D",
  "VECTOR3D",
  "COLOR",
  "PATH",
  "BOOLEAN",
  "ENUM",
]);
export type PropertyType = z.infer<typeof PropertyTypeEnum>;

export interface Property<T = PropertyValue> {
  id: string;
  name: string;
  type: PropertyType;
  value: T; // Valor estático por defecto
  isAnimated: boolean;
  keyframes: Keyframe<T>[];
  expression?: string; // Expresión matemática o ExtendScript
}

// --- 5. TRANSFORMACIONES ESPACIALES Y CAPAS ---

export interface LayerTransform {
  anchorPoint: Property<Vector2DValue | Vector3DValue>;
  position: Property<Vector2DValue | Vector3DValue>;
  scale: Property<Vector2DValue | Vector3DValue>;
  rotation: Property<ScalarValue>;
  opacity: Property<ScalarValue>;
}

export const LayerTypeEnum = z.enum([
  "NULL",
  "SOLID",
  "TEXT",
  "SHAPE",
  "IMAGE",
  "VIDEO",
  "AUDIO",
  "PRECOMP",
  "ADJUSTMENT",
  "CAMERA",
  "LIGHT",
]);
export type LayerType = z.infer<typeof LayerTypeEnum>;

export interface LayerTimelineConfig {
  startTime: number; // Tiempo de inicio en la comp (segundos)
  inPoint: number; // Punto de entrada visible en la comp
  outPoint: number; // Punto de salida visible en la comp
  stretch: number; // Factor de velocidad temporal (100 = 1x)
  timeRemapEnabled: boolean;
  timeRemap?: Property<ScalarValue>;
}

export interface LayerMarker {
  time: number;
  duration: number;
  comment: string;
  labelColor?: number;
  chapter?: string;
  url?: string;
}

export interface BaseLayer {
  id: string;
  name: string;
  type: LayerType;
  index: number;
  parentId?: string; // ID de la capa padre (parenting)
  enabled: boolean;
  solo: boolean;
  locked: boolean;
  timeline: LayerTimelineConfig;
  transform: LayerTransform;
  markers: LayerMarker[];
  data: Record<string, any>; // Metadatos específicos del elemento (Fase 2)
}

// --- 6. COMPOSICIÓN ---

export interface Composition {
  id: string;
  name: string;
  width: number;
  height: number;
  pixelAspect: number;
  frameRate: FrameRate;
  duration: number; // Duración total en segundos
  backgroundColor: ColorRGBAValue;
  layers: BaseLayer[];
  markers: LayerMarker[];
}

// --- 7. EVALUACIÓN Y FRAME STATE ---

export interface EvaluatedLayerTransform {
  worldMatrix: number[]; // Matriz afín 3x3 o 4x4
  localMatrix: number[];
  worldOpacity: number;
  anchorPoint: Vector2DValue | Vector3DValue;
  position: Vector2DValue | Vector3DValue;
  scale: Vector2DValue | Vector3DValue;
  rotation: number;
}

export interface EvaluatedLayerState {
  layerId: string;
  layerName: string;
  type: LayerType;
  isActive: boolean;
  localTime: number; // Tiempo local normalizado
  transform: EvaluatedLayerTransform;
  properties: Record<string, PropertyValue>;
}

export interface EvaluatedFrameState {
  compositionId: string;
  time: number;
  frame: number;
  activeLayers: EvaluatedLayerState[];
}
