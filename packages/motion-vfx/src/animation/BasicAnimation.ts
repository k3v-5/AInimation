import { EasingName, Time } from "../core/types.js";
import { validatePositiveNumber } from "../validation/validators.js";
import { AnimationNode } from "./AnimationNode.js";
import { AnimationResult } from "./AnimationResult.js";
import { evaluateEasing } from "./easing.js";
import { interpolate, interpolateUnclamped } from "./interpolation.js";
import { MotionFunction } from "./motion/types.js";
import { AnimationTrack, BasicAnimationOptions } from "./types.js";

/**
 * Nodo de animación atómico que interpola una o más pistas (tracks) desde un valor inicial hasta uno final.
 */
export class BasicAnimation extends AnimationNode {
  private _duration: Time;
  public easing: EasingName;
  public motion?: MotionFunction;
  public tracks: AnimationTrack<any>[] = [];

  constructor(options: BasicAnimationOptions<any>) {
    super(options);
    this._duration = validatePositiveNumber(options.duration, "duration");
    this.easing = options.easing ?? "linear";
    this.motion = options.motion;

    if (options.tracks && options.tracks.length > 0) {
      this.tracks = options.tracks.map((t) => ({ ...t }));
    } else if (options.target && options.from !== undefined && options.to !== undefined) {
      this.tracks.push({
        target: { ...options.target },
        from: options.from,
        to: options.to,
        easing: options.easing,
      });
    }
  }

  public get duration(): Time {
    return this._duration;
  }

  public evaluate(time: Time): AnimationResult {
    const result = new AnimationResult();

    // Calcular progreso normalizado acotado [0, 1]
    let progress = 0;
    if (time <= this.delay) {
      progress = 0;
    } else if (time >= this.totalDuration) {
      progress = 1;
    } else {
      progress = (time - this.delay) / this._duration;
    }

    const clampedProgress = Math.max(0, Math.min(1, progress));

    for (const track of this.tracks) {
      let finalProgress = clampedProgress;
      if (this.motion) {
        finalProgress = this.motion.evaluate(clampedProgress);
        const val = interpolateUnclamped(track.from, track.to, finalProgress);
        result.set(track.target, val, this.priority);
      } else {
        const easingName = track.easing ?? this.easing;
        finalProgress = evaluateEasing(easingName, clampedProgress);
        const val = interpolate(track.from, track.to, finalProgress);
        result.set(track.target, val, this.priority);
      }
    }

    return result;
  }
}
