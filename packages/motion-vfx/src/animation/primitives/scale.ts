import { Vector2 } from "../../core/types.js";
import { BaseElement } from "../../elements/BaseElement.js";
import { BasicAnimation } from "../BasicAnimation.js";
import { animateProperty } from "./animateProperty.js";
import { DEFAULT_SCALE_DURATION, DEFAULT_SCALE_IN_FROM, DEFAULT_SCALE_OUT_TO } from "./defaults.js";
import { ScaleOptions } from "./types.js";

function normalizeScale(val: Vector2 | number | undefined, fallback: number | Vector2): Vector2 {
  if (val === undefined) {
    return typeof fallback === "number" ? { x: fallback, y: fallback } : { ...fallback };
  }
  if (typeof val === "number") {
    return { x: val, y: val };
  }
  return { ...val };
}

/**
 * Anima la escala de un elemento haciéndolo crecer hasta su tamaño base (scale in).
 */
export function scaleIn(element: BaseElement, options: ScaleOptions = {}): BasicAnimation {
  const currentScale = element.transform?.scale?.getValue() ?? { x: 1, y: 1 };
  const from = normalizeScale(options.from, DEFAULT_SCALE_IN_FROM);
  const to = normalizeScale(options.to, currentScale);

  return animateProperty(element, "transform.scale", from, to, {
    duration: options.duration ?? DEFAULT_SCALE_DURATION,
    delay: options.delay,
    easing: options.easing,
    priority: options.priority,
    id: options.id,
    motion: options.motion,
  });
}

/**
 * Anima la escala de un elemento reduciéndolo desde su tamaño actual (scale out).
 */
export function scaleOut(element: BaseElement, options: ScaleOptions = {}): BasicAnimation {
  const currentScale = element.transform?.scale?.getValue() ?? { x: 1, y: 1 };
  const from = normalizeScale(options.from, currentScale);
  const to = normalizeScale(options.to, DEFAULT_SCALE_OUT_TO);

  return animateProperty(element, "transform.scale", from, to, {
    duration: options.duration ?? DEFAULT_SCALE_DURATION,
    delay: options.delay,
    easing: options.easing,
    priority: options.priority,
    id: options.id,
    motion: options.motion,
  });
}
