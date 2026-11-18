import { BaseElement } from "../../elements/BaseElement.js";
import { BasicAnimation } from "../BasicAnimation.js";
import { animateProperty } from "./animateProperty.js";
import { DEFAULT_ROTATE_DURATION, DEFAULT_ROTATE_IN_FROM, DEFAULT_ROTATE_OUT_TO } from "./defaults.js";
import { RotateOptions } from "./types.js";

/**
 * Anima la rotación de un elemento hasta su ángulo base (rotate in).
 */
export function rotateIn(element: BaseElement, options: RotateOptions = {}): BasicAnimation {
  const currentRotation = element.transform?.rotation?.getValue() ?? 0;
  const from = options.from ?? DEFAULT_ROTATE_IN_FROM;
  const to = options.to ?? currentRotation;

  return animateProperty(element, "transform.rotation", from, to, {
    duration: options.duration ?? DEFAULT_ROTATE_DURATION,
    delay: options.delay,
    easing: options.easing,
    priority: options.priority,
    id: options.id,
    motion: options.motion,
  });
}

/**
 * Anima la rotación de un elemento hacia afuera desde su ángulo actual (rotate out).
 */
export function rotateOut(element: BaseElement, options: RotateOptions = {}): BasicAnimation {
  const currentRotation = element.transform?.rotation?.getValue() ?? 0;
  const from = options.from ?? currentRotation;
  const to = options.to ?? DEFAULT_ROTATE_OUT_TO;

  return animateProperty(element, "transform.rotation", from, to, {
    duration: options.duration ?? DEFAULT_ROTATE_DURATION,
    delay: options.delay,
    easing: options.easing,
    priority: options.priority,
    id: options.id,
    motion: options.motion,
  });
}
