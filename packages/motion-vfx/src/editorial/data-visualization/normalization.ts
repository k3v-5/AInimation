import { DataPoint } from "./types.js";

/**
 * REQ-025 §7: Normalización numérica determinista y acotada en [0.0, 1.0].
 *
 * Fórmula:
 *   n = (x - min) / (max - min)
 *   n_clamped = clamp(n, 0, 1)
 *
 * Caso especial:
 *   max = min => normalizedValue = 0.5 (sin división por cero).
 */
export function normalizeValue(value: number, min: number, max: number): number {
  if (!Number.isFinite(value) || !Number.isFinite(min) || !Number.isFinite(max)) {
    return 0.5;
  }

  // Caso especial: dataset constante
  if (Math.abs(max - min) < 1e-12) {
    return 0.5;
  }

  const n = (value - min) / (max - min);

  // Clamping estricto en [0.0, 1.0] (Invariante A)
  if (n < 0.0) return 0.0;
  if (n > 1.0) return 1.0;
  return n;
}

/**
 * Normaliza un array de puntos sin mutar los originales (§2.1).
 */
export function normalizeDatasetPoints(
  points: DataPoint[],
  minVal?: number,
  maxVal?: number
): DataPoint[] {
  if (points.length === 0) return [];
  const vals = points.map((p) => p.value);
  const min = minVal ?? Math.min(...vals);
  const max = maxVal ?? Math.max(...vals);

  return points.map((p) => ({
    ...p,
    metadata: {
      ...p.metadata,
      normalizedValue: normalizeValue(p.value, min, max),
    },
  }));
}

export function denormalizeValue(
  normalized: number,
  min: number,
  max: number
): number {
  return min + normalized * (max - min);
}
