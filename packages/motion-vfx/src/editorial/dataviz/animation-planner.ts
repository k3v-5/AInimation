import { normalizeNumber } from "./data-normalizer.js";
import { DataVizIssue } from "./errors.js";
import { DataVizAnimation, EasingCurve } from "./types.js";

/**
 * REQ-025 §44, §45, §46, §48: Mathematical Animation Planner & Easing Engine.
 */
export class AnimationPlanner {
  /**
   * Evaluates standard easing functions purely with mathematics.
   */
  public static evaluateEasing(t: number, easing: EasingCurve): number {
    const clampedT = Math.max(0.0, Math.min(1.0, t));

    switch (easing) {
      case "LINEAR":
        return normalizeNumber(clampedT);
      case "EASE_IN_CUBIC":
        return normalizeNumber(Math.pow(clampedT, 3));
      case "EASE_OUT_CUBIC":
        return normalizeNumber(1.0 - Math.pow(1.0 - clampedT, 3));
      case "EASE_IN_OUT_CUBIC":
        if (clampedT < 0.5) {
          return normalizeNumber(4.0 * Math.pow(clampedT, 3));
        } else {
          return normalizeNumber(1.0 - Math.pow(-2.0 * clampedT + 2.0, 3) / 2.0);
        }
      default:
        return normalizeNumber(clampedT);
    }
  }

  /**
   * Calculates progress for any timestamp against keyframe range.
   */
  public static evaluateProgress(
    timeSeconds: number,
    startSeconds: number,
    endSeconds: number,
    easing: EasingCurve = "EASE_OUT_CUBIC"
  ): number {
    if (timeSeconds <= startSeconds) return 0.0;
    if (timeSeconds >= endSeconds) return 1.0;
    const rawRatio = (timeSeconds - startSeconds) / (endSeconds - startSeconds);
    return this.evaluateEasing(rawRatio, easing);
  }

  /**
   * Interpolates values between from and to.
   */
  public static interpolate(
    from: number | number[],
    to: number | number[],
    progress: number
  ): number | number[] {
    const p = Math.max(0.0, Math.min(1.0, progress));

    if (Array.isArray(from) && Array.isArray(to)) {
      return from.map((f, i) => {
        const target = to[i] ?? f;
        return normalizeNumber(f + p * (target - f));
      });
    }

    const start = typeof from === "number" ? from : 0;
    const end = typeof to === "number" ? to : 0;
    return normalizeNumber(start + p * (end - start));
  }

  /**
   * REQ-025 §45: Validates animation timing invariants against composition duration.
   */
  public static validateAnimation(
    animation: DataVizAnimation,
    compositionDuration: number
  ): DataVizIssue[] {
    const issues: DataVizIssue[] = [];

    if (animation.startSeconds < 0) {
      issues.push({
        code: "NEGATIVE_START_TIME",
        path: `animations.${animation.id}.startSeconds`,
        message: `Animation start time (${animation.startSeconds}s) must be non-negative`,
        severity: "BLOCKING",
      });
    }

    if (animation.endSeconds <= animation.startSeconds) {
      issues.push({
        code: "INVALID_DURATION",
        path: `animations.${animation.id}.endSeconds`,
        message: `Animation end time (${animation.endSeconds}s) must be strictly greater than start time (${animation.startSeconds}s)`,
        severity: "BLOCKING",
      });
    }

    if (animation.endSeconds > compositionDuration + 1e-4) {
      issues.push({
        code: "ANIMATION_OUT_OF_BOUNDS",
        path: `animations.${animation.id}.endSeconds`,
        message: `Animation end time (${animation.endSeconds}s) exceeds composition duration (${compositionDuration}s)`,
        severity: "BLOCKING",
      });
    }

    return issues;
  }

  /**
   * REQ-025 §48: Computes deterministic stagger delays.
   */
  public static computeStaggerDelay(index: number, staggerSeconds: number): number {
    return normalizeNumber(index * staggerSeconds);
  }
}
