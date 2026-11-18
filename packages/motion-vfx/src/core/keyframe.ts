import { EasingName, SpatialInterpolationType, SpatialTangent, Time } from "./types.js";

/**
 * Representación inmutable de un Keyframe como dato puro.
 * Permite metadatos de interpolación temporal y espacial sin romper compatibilidad.
 */
export interface Keyframe<T> {
  readonly time: Time;
  readonly value: T;
  readonly easing?: EasingName;
  /** Tangente espacial de entrada para trayectorias de curvas de posición */
  readonly spatialIn?: SpatialTangent;
  /** Tangente espacial de salida para trayectorias de curvas de posición */
  readonly spatialOut?: SpatialTangent;
  /** Modo de interpolación espacial */
  readonly spatialInterpolation?: SpatialInterpolationType;
}
