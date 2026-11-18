import { Vector2 } from "../../core/types.js";
import { BaseElement } from "../../elements/BaseElement.js";
import { validateNonNegativeNumber } from "../../validation/validators.js";
import { BasicAnimation } from "../BasicAnimation.js";
import { animateProperty } from "./animateProperty.js";
import { DEFAULT_SLIDE_DIRECTION, DEFAULT_SLIDE_DISTANCE, DEFAULT_SLIDE_DURATION } from "./defaults.js";
import { SlideOptions } from "./types.js";

function calculateOffset(direction: string, distance: number): Vector2 {
  switch (direction) {
    case "left":
      return { x: -distance, y: 0 };
    case "right":
      return { x: distance, y: 0 };
    case "up":
      return { x: 0, y: -distance };
    case "down":
      return { x: 0, y: distance };
    default:
      return { x: -distance, y: 0 };
  }
}

/**
 * Anima la posición de un elemento deslizándolo hacia su posición objetivo (slide in).
 */
export function slideIn(element: BaseElement, options: SlideOptions = {}): BasicAnimation {
  const currentPos = element.transform?.position?.getValue() ?? { x: 0, y: 0 };
  const distance =
    options.distance !== undefined
      ? validateNonNegativeNumber(options.distance, "distance")
      : DEFAULT_SLIDE_DISTANCE;
  const direction = options.direction ?? DEFAULT_SLIDE_DIRECTION;

  const offset = calculateOffset(direction, distance);
  const from = options.from ?? { x: currentPos.x + offset.x, y: currentPos.y + offset.y };
  const to = options.to ?? { x: currentPos.x, y: currentPos.y };

  return animateProperty(element, "transform.position", from, to, {
    duration: options.duration ?? DEFAULT_SLIDE_DURATION,
    delay: options.delay,
    easing: options.easing,
    priority: options.priority,
    id: options.id,
    motion: options.motion,
  });
}

/**
 * Anima la posición de un elemento deslizándolo hacia afuera desde su posición actual (slide out).
 */
export function slideOut(element: BaseElement, options: SlideOptions = {}): BasicAnimation {
  const currentPos = element.transform?.position?.getValue() ?? { x: 0, y: 0 };
  const distance =
    options.distance !== undefined
      ? validateNonNegativeNumber(options.distance, "distance")
      : DEFAULT_SLIDE_DISTANCE;
  const direction = options.direction ?? DEFAULT_SLIDE_DIRECTION;

  const offset = calculateOffset(direction, distance);
  const from = options.from ?? { x: currentPos.x, y: currentPos.y };
  const to = options.to ?? { x: currentPos.x + offset.x, y: currentPos.y + offset.y };

  return animateProperty(element, "transform.position", from, to, {
    duration: options.duration ?? DEFAULT_SLIDE_DURATION,
    delay: options.delay,
    easing: options.easing,
    priority: options.priority,
    id: options.id,
    motion: options.motion,
  });
}
