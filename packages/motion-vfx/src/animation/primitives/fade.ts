import { BaseElement } from "../../elements/BaseElement.js";
import { BasicAnimation } from "../BasicAnimation.js";
import { animateProperty } from "./animateProperty.js";
import { DEFAULT_FADE_DURATION } from "./defaults.js";
import { FadeOptions } from "./types.js";

/**
 * Anima la opacidad de un elemento desde 0 (o from) hasta su valor base (o to).
 */
export function fadeIn(element: BaseElement, options: FadeOptions = {}): BasicAnimation {
  const currentOpacity = element.transform?.opacity?.getValue() ?? 1;
  const from = options.from ?? 0;
  const to = options.to ?? currentOpacity;

  return animateProperty(element, "transform.opacity", from, to, {
    duration: options.duration ?? DEFAULT_FADE_DURATION,
    delay: options.delay,
    easing: options.easing,
    priority: options.priority,
    id: options.id,
    motion: options.motion,
  });
}

/**
 * Anima la opacidad de un elemento desde su valor base (o from) hasta 0 (o to).
 */
export function fadeOut(element: BaseElement, options: FadeOptions = {}): BasicAnimation {
  const currentOpacity = element.transform?.opacity?.getValue() ?? 1;
  const from = options.from ?? currentOpacity;
  const to = options.to ?? 0;

  return animateProperty(element, "transform.opacity", from, to, {
    duration: options.duration ?? DEFAULT_FADE_DURATION,
    delay: options.delay,
    easing: options.easing,
    priority: options.priority,
    id: options.id,
    motion: options.motion,
  });
}
