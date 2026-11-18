import { EasingName, Time } from "../core/types.js";

export type AnimationLifecycleState = "before" | "active" | "after";

/**
 * Destino canónico de una propiedad dentro de un elemento animable.
 */
export interface AnimationTarget {
  elementId: string;
  propertyPath: string; // ej. "transform.position", "transform.scale", "transform.opacity", "volume"
}

/**
 * Pista de animación individual para una propiedad tipada.
 */
export interface AnimationTrack<T = unknown> {
  target: AnimationTarget;
  from: T;
  to: T;
  easing?: EasingName;
}

export interface BaseAnimationOptions {
  id?: string;
  delay?: Time;
  priority?: number;
}

export interface BasicAnimationOptions<T = unknown> extends BaseAnimationOptions {
  target?: AnimationTarget;
  from?: T;
  to?: T;
  duration: Time;
  easing?: EasingName;
  tracks?: AnimationTrack<T>[];
  motion?: import("./motion/types.js").MotionFunction;
}

export interface ParallelAnimationOptions extends BaseAnimationOptions {
  children?: import("./AnimationNode.js").AnimationNode[];
}

export interface SequenceAnimationOptions extends BaseAnimationOptions {
  children?: import("./AnimationNode.js").AnimationNode[];
}

export interface SerializedAnimationTarget {
  elementId: string;
  propertyPath: string;
}

export interface SerializedAnimationTrack {
  target: SerializedAnimationTarget;
  from: unknown;
  to: unknown;
  easing?: EasingName;
}

export interface SerializedBasicAnimation {
  type: "basic";
  id: string;
  delay: Time;
  duration: Time;
  priority: number;
  easing: EasingName;
  tracks: SerializedAnimationTrack[];
  motion?: Record<string, unknown>;
}

export interface SerializedParallelAnimation {
  type: "parallel";
  id: string;
  delay: Time;
  priority: number;
  children: SerializedAnimationNode[];
}

export interface SerializedSequenceAnimation {
  type: "sequence";
  id: string;
  delay: Time;
  priority: number;
  children: SerializedAnimationNode[];
}

export type SerializedAnimationNode =
  | SerializedBasicAnimation
  | SerializedParallelAnimation
  | SerializedSequenceAnimation;
