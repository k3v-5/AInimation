import {
  VisualizationAnimation,
  VisualizationKeyframe,
  EasingType,
} from "./types.js";

/**
 * REQ-025 §13, §14, §29: Generador determinista de animaciones y keyframes monotónicos.
 */

export function createGrowAnimation(
  elementId: string,
  targetScale: number,
  durationSeconds: number,
  delaySeconds = 0,
  easing: EasingType = "EASE_OUT"
): VisualizationAnimation {
  const start = Math.max(0, delaySeconds);
  const end = Number((start + Math.max(0.1, durationSeconds)).toFixed(4));

  return {
    id: `anim-grow-${elementId}`,
    elementId,
    property: "scale",
    easing,
    keyframes: [
      { timeSeconds: start, value: 0 },
      { timeSeconds: end, value: Number(targetScale.toFixed(4)) },
    ],
  };
}

export function createWriteOnAnimation(
  elementId: string,
  durationSeconds: number,
  delaySeconds = 0,
  easing: EasingType = "EASE_OUT"
): VisualizationAnimation {
  const start = Math.max(0, delaySeconds);
  const end = Number((start + Math.max(0.1, durationSeconds)).toFixed(4));

  return {
    id: `anim-writeon-${elementId}`,
    elementId,
    property: "trimPathEnd",
    easing,
    keyframes: [
      { timeSeconds: start, value: 0 },
      { timeSeconds: end, value: 100 },
    ],
  };
}

export function createFadeInAnimation(
  elementId: string,
  durationSeconds = 0.5,
  delaySeconds = 0,
  easing: EasingType = "EASE_OUT"
): VisualizationAnimation {
  const start = Math.max(0, delaySeconds);
  const end = Number((start + Math.max(0.1, durationSeconds)).toFixed(4));

  return {
    id: `anim-fade-${elementId}`,
    elementId,
    property: "opacity",
    easing,
    keyframes: [
      { timeSeconds: start, value: 0 },
      { timeSeconds: end, value: 1 },
    ],
  };
}

export function createCounterAnimation(
  elementId: string,
  fromValue: number,
  toValue: number,
  durationSeconds: number,
  delaySeconds = 0,
  precision = 0,
  easing: EasingType = "EASE_OUT"
): VisualizationAnimation {
  const start = Math.max(0, delaySeconds);
  const end = Number((start + Math.max(0.1, durationSeconds)).toFixed(4));

  return {
    id: `anim-counter-${elementId}`,
    elementId,
    property: "text",
    easing,
    keyframes: [
      { timeSeconds: start, value: fromValue.toFixed(precision) },
      { timeSeconds: end, value: toValue.toFixed(precision) },
    ],
  };
}

/**
 * Valida que una animación cumpla la invariante de monotonicidad temporal.
 */
export function validateAnimationMonotonicity(animation: VisualizationAnimation): boolean {
  if (!animation.keyframes || animation.keyframes.length === 0) return true;

  for (let i = 0; i < animation.keyframes.length; i++) {
    const kf = animation.keyframes[i];
    if (kf.timeSeconds < 0) return false;
    if (i > 0) {
      if (kf.timeSeconds < animation.keyframes[i - 1].timeSeconds) {
        return false;
      }
    }
  }
  return true;
}
