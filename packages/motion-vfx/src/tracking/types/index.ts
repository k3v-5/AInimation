import { Time } from "../../core/types.js";
import { Vec2 } from "../../masks/types/index.js";

export type TrackerType = "point" | "object" | "transform";
export type TrackingSmoothingMode = "none" | "moving-average" | "exponential";

export interface TransformSample {
  position: Vec2;
  scale: Vec2;
  rotation: number; // en grados
}

export interface TrackingSample {
  time: Time;
  transform: TransformSample;
  confidence?: number;
}

export interface TrackingData {
  samples: TrackingSample[];
}

export interface SmoothingSettings {
  mode: TrackingSmoothingMode;
  windowSize?: number; // Para moving-average (ej. 5 muestras)
  alpha?: number; // Para exponential smoothing [0, 1] (ej. 0.3)
}

export interface PropertyBinding {
  id: string;
  sourceTrackerId: string;
  targetElementId: string;
  targetProperty: "transform" | "position" | "scale" | "rotation";
  offset?: Vec2;
  scaleMultiplier?: Vec2;
  rotationOffset?: number;
}
