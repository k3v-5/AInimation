/**
 * Tipos fundamentales del Core Temporal.
 */

/** Tiempo expresado en segundos continuos (>= 0). */
export type Time = number;

/** Vector bidimensional */
export interface Vector2 {
  x: number;
  y: number;
}

/** Vector tridimensional */
export interface Vector3 {
  x: number;
  y: number;
  z: number;
}

/** Color RGBA con canales normalizados en [0.0, 1.0] */
export interface Color {
  r: number;
  g: number;
  b: number;
  a: number;
}

/** Nombres de funciones de Easing soportadas en Fase 1 */
export type EasingName = "linear" | "easeIn" | "easeOut" | "easeInOut";

/** Función matemática de Easing pura */
export type EasingFunction = (progress: number) => number;

/** Tangente espacial 2D para trayectorias de movimiento curvilíneas */
export interface SpatialTangent2D {
  x: number;
  y: number;
}

/** Tangente espacial 3D */
export interface SpatialTangent3D {
  x: number;
  y: number;
  z: number;
}

export type SpatialTangent = SpatialTangent2D | SpatialTangent3D;

/** Tipo de interpolación espacial de trayectoria */
export type SpatialInterpolationType = "linear" | "bezier" | "hold";

/** Identificador de tipo de valor para serialización y validación */
export type PropertyTypeName = "number" | "vector2" | "vector3" | "color" | "string" | "boolean" | "unknown";
