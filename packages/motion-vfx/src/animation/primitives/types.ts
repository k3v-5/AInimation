import { EasingName, Time, Vector2 } from "../../core/types.js";

export type SlideDirection = "left" | "right" | "up" | "down";

export interface MotionOptions {
  duration?: Time;
  delay?: Time;
  easing?: EasingName;
  priority?: number;
  id?: string;
  motion?: import("../motion/types.js").MotionFunction;
}

export interface FadeOptions extends MotionOptions {
  from?: number;
  to?: number;
}

export interface SlideOptions extends MotionOptions {
  direction?: SlideDirection;
  distance?: number;
  from?: Vector2;
  to?: Vector2;
}

export interface ScaleOptions extends MotionOptions {
  from?: Vector2 | number;
  to?: Vector2 | number;
}

export interface RotateOptions extends MotionOptions {
  from?: number;
  to?: number;
}
