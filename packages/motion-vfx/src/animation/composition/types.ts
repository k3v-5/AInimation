import { Time } from "../../core/types.js";
import { SerializedAnimationNode } from "../types.js";

export type StaggerMode = "forward" | "reverse";

export interface StaggerOptions {
  delay: Time;
  mode?: StaggerMode;
  seed?: number;
}

export interface SerializedDelayNode {
  type: "delay";
  id: string;
  duration: Time;
}

export interface SerializedHoldNode {
  type: "hold";
  id: string;
  duration: Time;
}

export interface SerializedRepeatNode {
  type: "repeat";
  id: string;
  count: number;
  child: SerializedAnimationNode;
}

export interface SerializedOffsetNode {
  type: "offset";
  id: string;
  offsetTime: Time;
  child: SerializedAnimationNode;
}
