import { Camera } from "../../camera/types/index.js";
import { Time } from "../../core/types.js";
import { EffectSerialization } from "../../effects/types/index.js";
import { Mask } from "../../masks/types/index.js";
import { Transform } from "../../transform/Transform.js";

export type LayerType =
  | "video"
  | "image"
  | "text"
  | "shape"
  | "composition"
  | "particle"
  | "adjustment"
  | "controller";

export type BlendMode =
  | "normal"
  | "multiply"
  | "screen"
  | "overlay"
  | "add"
  | "darken"
  | "lighten";

export type AlphaMode = "straight" | "premultiplied";

export type SemanticMarkerType =
  | "HOOK"
  | "EMPHASIS"
  | "PUNCHLINE"
  | "CTA"
  | "BROLL"
  | "GENERIC";

export interface SceneMarker {
  id: string;
  name: string;
  time: Time;
  type: SemanticMarkerType;
  metadata?: Record<string, any>;
}

export interface LayerOptions {
  id?: string;
  name?: string;
  type: LayerType;
  start?: Time;
  duration?: Time;
  transform?: Transform;
  opacity?: number;
  visible?: boolean;
  blendMode?: BlendMode;
  alphaMode?: AlphaMode;
  parentId?: string;
  effectStack?: EffectSerialization[];
  masks?: Mask[];
  compositionId?: string; // Para CompositionLayer
}

export interface SceneOptions {
  id?: string;
  name?: string;
  duration: Time;
  width: number;
  height: number;
  layers?: LayerOptions[];
  camera?: Camera;
  markers?: SceneMarker[];
}
