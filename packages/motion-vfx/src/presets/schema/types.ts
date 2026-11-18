import { ElementType } from "../../elements/types.js";
import { BaseElement } from "../../elements/BaseElement.js";
import { AnimationNode } from "../../animation/AnimationNode.js";

export type PresetCategory =
  | "entrance"
  | "exit"
  | "emphasis"
  | "transition"
  | "text"
  | "camera"
  | "utility";

export type PresetParameterType =
  | "number"
  | "boolean"
  | "string"
  | "enum"
  | "duration"
  | "distance"
  | "color";

export interface PresetParameterSchema {
  name: string;
  type: PresetParameterType;
  default: unknown;
  description: string;
  min?: number;
  max?: number;
  values?: string[]; // Para tipo 'enum'
}

export interface PresetContext {
  target: BaseElement | { id: string; type?: ElementType };
  parameters: Record<string, unknown>;
  id?: string;
  delay?: number;
  priority?: number;
}

export interface PresetDefinition {
  id: string;
  name: string;
  category: PresetCategory;
  version: number;
  description: string;
  tags: string[];
  parameters: PresetParameterSchema[];
  compatibleWith?: ElementType[];
  requires?: string[];
  dependencies?: string[];
  build(context: PresetContext): AnimationNode;
}

export interface PresetSearchQuery {
  category?: PresetCategory;
  tags?: string[];
  compatibleWith?: ElementType;
}
