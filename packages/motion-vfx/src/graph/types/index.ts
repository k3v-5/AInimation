import { Time } from "../../core/types.js";

export interface RenderQuality {
  resolutionScale: number; // 0.5 (Draft), 1.0 (Final)
  effectsQuality: number;
  motionBlur: boolean;
  antialiasing: boolean;
}

export interface RenderContext {
  time: Time;
  frame: number;
  width: number;
  height: number;
  quality: RenderQuality;
}

export interface RenderNode {
  id: string;
  name?: string;
  type: string;
  inputs: string[]; // IDs de nodos de los que depende
  evaluate(context: RenderContext, inputs: Map<string, any>): any;
}
