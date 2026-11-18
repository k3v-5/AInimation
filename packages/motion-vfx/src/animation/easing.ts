import { EasingFunction, EasingName } from "../core/types.js";

/**
 * Funciones de Easing cúbicas puras y deterministas para Fase 1.
 */

export const linear: EasingFunction = (t: number): number => {
  if (t <= 0) return 0;
  if (t >= 1) return 1;
  return t;
};

export const easeIn: EasingFunction = (t: number): number => {
  if (t <= 0) return 0;
  if (t >= 1) return 1;
  const res = t * t * t;
  return res <= 0 ? 0 : res >= 1 ? 1 : res;
};

export const easeOut: EasingFunction = (t: number): number => {
  if (t <= 0) return 0;
  if (t >= 1) return 1;
  const inv = 1 - t;
  const res = 1 - inv * inv * inv;
  return res <= 0 ? 0 : res >= 1 ? 1 : res;
};

export const easeInOut: EasingFunction = (t: number): number => {
  if (t <= 0) return 0;
  if (t >= 1) return 1;
  if (t === 0.5) return 0.5;
  const res = t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  return res <= 0 ? 0 : res >= 1 ? 1 : res;
};

const EASING_REGISTRY: Record<EasingName, EasingFunction> = {
  linear,
  easeIn,
  easeOut,
  easeInOut,
};

/**
 * Obtiene la función de easing correspondiente por nombre.
 * Si no se especifica o es desconocida, retorna linear.
 */
export function getEasing(name?: EasingName): EasingFunction {
  if (!name) {
    return linear;
  }
  return EASING_REGISTRY[name] || linear;
}

/**
 * Evalúa directamente una función de easing por nombre sobre el progreso [0, 1].
 */
export function evaluateEasing(name: EasingName | undefined, t: number): number {
  return getEasing(name)(t);
}
