import { BaseElement } from "../../elements/BaseElement.js";
import { validateNonNegativeNumber, validatePositiveNumber } from "../../validation/validators.js";
import { BasicAnimation } from "../BasicAnimation.js";
import { DEFAULT_EASING } from "./defaults.js";
import { MotionOptions } from "./types.js";

/**
 * Función constructora genérica para animar cualquier propiedad tipada de un elemento.
 */
export function animateProperty<T = unknown>(
  element: BaseElement | { id: string },
  propertyPath: string,
  from: T,
  to: T,
  options: MotionOptions = {}
): BasicAnimation {
  const duration = options.duration !== undefined ? validatePositiveNumber(options.duration, "duration") : 0.4;
  const delay = options.delay !== undefined ? validateNonNegativeNumber(options.delay, "delay") : 0;
  const easing = options.easing ?? DEFAULT_EASING;

  return new BasicAnimation({
    id: options.id,
    target: { elementId: element.id, propertyPath },
    from,
    to,
    duration,
    delay,
    easing,
    priority: options.priority ?? 0,
    motion: options.motion,
  });
}
