import { Time } from "../../core/types.js";
import { Marker } from "../../timeline/types/index.js";

export type SemanticSceneRole =
  | "hook"
  | "intro"
  | "explanation"
  | "example"
  | "reaction"
  | "cta"
  | "outro"
  | "custom";

export interface SceneMetadata {
  name?: string;
  tags?: string[];
  semanticRole?: SemanticSceneRole | string;
  description?: string;
}

export interface SceneSerialization {
  id: string;
  duration: Time;
  metadata?: SceneMetadata;
  markers?: Marker[];
  composition: unknown;
}

export interface EvaluatedSceneState {
  id: string;
  localTime: Time;
  active: boolean;
  metadata?: SceneMetadata;
  elements: unknown[];
}
