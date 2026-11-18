import { Color, Time, Vector2 } from "../../core/types.js";

export type EffectCategory =
  | "blur"
  | "color"
  | "light"
  | "distortion"
  | "stylization"
  | "shadow"
  | "transform"
  | "mask"
  | "noise"
  | "utility";

export type BlendMode =
  | "normal"
  | "add"
  | "screen"
  | "multiply"
  | "overlay"
  | "softLight";

export type EffectScope = "element" | "group" | "composition" | "layer";

export interface Resolution {
  width: number;
  height: number;
}

export interface EffectContext {
  time: Time;
  frame?: number;
  resolution?: Resolution;
  scope?: EffectScope;
  targetId?: string;
}

export type EffectParameterType =
  | "number"
  | "boolean"
  | "string"
  | "enum"
  | "color"
  | "vector2";

export interface EffectParameterSchema {
  name: string;
  type: EffectParameterType;
  default: unknown;
  description: string;
  min?: number;
  max?: number;
  values?: string[]; // Para tipo 'enum'
}

export interface EvaluatedEffect {
  id: string;
  name: string;
  type: string;
  category: EffectCategory;
  enabled: boolean;
  blendMode: BlendMode;
  params: Record<string, unknown>;
}

export interface EvaluatedEffectStack {
  effects: EvaluatedEffect[];
}

export interface EffectSerialization {
  id: string;
  name: string;
  type: string;
  enabled: unknown;
  blendMode?: BlendMode;
  params: Record<string, unknown>;
}
