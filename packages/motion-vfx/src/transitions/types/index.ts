import { EasingName, Time } from "../../core/types.js";

export interface TransitionParameterSchema {
  name: string;
  type: "number" | "boolean" | "string" | "enum" | "color";
  default: unknown;
  description: string;
  min?: number;
  max?: number;
  values?: string[];
}

export interface TransitionContext {
  progress: number; // Progreso normalizado [0, 1] tras aplicar easing
  rawProgress: number; // Progreso lineal puro [0, 1]
  time: Time; // Tiempo transcurrido dentro de la ventana de transición
  duration: Time; // Duración total de la transición
  params: Record<string, unknown>;
}

export interface TransformModifier {
  scale?: number;
  translateX?: number;
  translateY?: number;
  rotation?: number;
}

export interface ColorOverlay {
  color: { r: number; g: number; b: number; a?: number };
  opacity: number;
}

export interface TransitionResult {
  fromOpacity: number;
  toOpacity: number;
  fromTransform?: TransformModifier;
  toTransform?: TransformModifier;
  fromBlur?: number;
  toBlur?: number;
  colorOverlay?: ColorOverlay;
  custom?: Record<string, unknown>;
}

export interface TransitionSerialization {
  type: string;
  duration: Time;
  easing?: EasingName;
  params?: Record<string, unknown>;
}
