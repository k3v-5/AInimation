import { BoundingBox } from "../../asset-library/types/index.js";
import { Time, Vector2 } from "../../core/types.js";

export type TrackTargetType = "point" | "object" | "face" | "person" | "camera";

export type TrackState = "active" | "occluded" | "lost" | "out-of-frame" | "ended";

export interface TrackSample {
  time: Time;
  position?: Vector2;
  bounds?: BoundingBox;
  rotation?: number;
  scale?: Vector2;
  confidence: number;
}

export interface Track {
  id: string;
  targetType: TrackTargetType;
  semanticClass?: string; // e.g. "laptop", "person", "phone"
  role?: "main_subject" | "secondary_subject" | "background";
  start: Time;
  end: Time;
  samples: TrackSample[];
  confidence: number;
  state: TrackState;
}

export interface RelativeBinding {
  offset: Vector2;
  followRotation?: boolean;
  followScale?: boolean;
}

export interface TrackBinding {
  trackId: string;
  targetLayerId: string;
  binding: RelativeBinding;
}

export interface RotoMask {
  id: string;
  trackId: string;
  feather: number; // Pixeles de desvanecimiento
  opacity: number; // [0, 1]
  invert: boolean;
}

export interface ObjectEffectConfig {
  id: string;
  type: "background-blur" | "object-blur" | "subject-pop" | "object-focus" | "highlight-outline";
  targetClass: string;
  parameters: Record<string, unknown>;
}

export interface SemanticTargetQuery {
  semanticClass: string;
  role?: "main_subject" | "secondary_subject";
  time?: Time;
}
