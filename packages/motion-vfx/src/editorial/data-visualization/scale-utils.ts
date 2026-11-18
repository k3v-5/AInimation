import { ScaleType, VisualScale } from "./types.js";
import { ScaleCalculationError } from "./errors.js";
import { EPSILON } from "./constants.js";

/**
 * REQ-025 §13, §39, §40: Utilidades matemáticas de escalas.
 */

export function normalizeValue(value: number, min: number, max: number): number {
  if (Math.abs(max - min) < EPSILON) {
    return 0.5;
  }
  const norm = (value - min) / (max - min);
  return Math.max(0, Math.min(1, norm));
}

export function denormalizeValue(normalized: number, min: number, max: number): number {
  if (Math.abs(max - min) < EPSILON) {
    return min;
  }
  const clamped = Math.max(0, Math.min(1, normalized));
  return min + clamped * (max - min);
}

export function linearScale(
  domain: [number, number],
  range: [number, number]
): (val: number) => number {
  const [d0, d1] = domain;
  const [r0, r1] = range;

  return (val: number): number => {
    if (Math.abs(d1 - d0) < EPSILON) {
      return (r0 + r1) / 2;
    }
    const t = (val - d0) / (d1 - d0);
    return r0 + t * (r1 - r0);
  };
}

export function logScale(
  domain: [number, number],
  range: [number, number]
): (val: number) => number {
  const [d0, d1] = domain;
  const [r0, r1] = range;

  if (d0 <= 0 || d1 <= 0) {
    throw new ScaleCalculationError("La escala logarítmica requiere un dominio estrictamente positivo (> 0).");
  }

  const logD0 = Math.log10(d0);
  const logD1 = Math.log10(d1);

  return (val: number): number => {
    if (val <= 0) {
      throw new ScaleCalculationError(`Valor <= 0 (${val}) no admitido en escala logarítmica.`);
    }
    const logVal = Math.log10(val);
    const t = (logVal - logD0) / (logD1 - logD0);
    return r0 + t * (r1 - r0);
  };
}

export function sqrtScale(
  domain: [number, number],
  range: [number, number]
): (val: number) => number {
  const [d0, d1] = domain;
  const [r0, r1] = range;

  if (d0 < 0 || d1 < 0) {
    throw new ScaleCalculationError("La escala SQRT requiere valores no negativos (>= 0).");
  }

  const sqrtD0 = Math.sqrt(d0);
  const sqrtD1 = Math.sqrt(d1);

  return (val: number): number => {
    if (val < 0) {
      throw new ScaleCalculationError(`Valor negativo (${val}) no admitido en escala SQRT.`);
    }
    const sqrtVal = Math.sqrt(val);
    const t = (sqrtVal - sqrtD0) / (sqrtD1 - sqrtD0);
    return r0 + t * (r1 - r0);
  };
}

/**
 * Adapter para compatibilidad con suites preexistentes (Fase 4I / DataVisualization.test.ts)
 */
export class VisualScales {
  public static createScale(params: {
    min: number;
    max: number;
    pixelStart: number;
    pixelEnd: number;
  }): any {
    return params;
  }

  public static mapValueToPixel(value: number, scale: any): number {
    if (!Number.isFinite(value)) {
      throw new ScaleCalculationError(`Valor no finito proporcionado a mapValueToPixel: ${value}`);
    }
    if (scale.max === scale.min) {
      return (scale.pixelStart + scale.pixelEnd) / 2.0;
    }
    const t = (value - scale.min) / (scale.max - scale.min);
    const pixel = scale.pixelStart + t * (scale.pixelEnd - scale.pixelStart);
    return Number(pixel.toFixed(3));
  }

  public static createLinearScale(domain: [number, number], range: [number, number]): any {
    return {
      min: domain[0],
      max: domain[1],
      pixelStart: range[0],
      pixelEnd: range[1],
      domain,
      range,
      type: "LINEAR",
      clamped: true,
    };
  }

  public static applyScale(scale: any, value: number): number {
    const domain = scale.domain ?? [scale.min, scale.max];
    const range = scale.range ?? [scale.pixelStart, scale.pixelEnd];
    const fn = linearScale(domain, range);
    const res = fn(value);
    if (scale.clamped) {
      const minR = Math.min(range[0], range[1]);
      const maxR = Math.max(range[0], range[1]);
      return Math.max(minR, Math.min(maxR, res));
    }
    return res;
  }
}
