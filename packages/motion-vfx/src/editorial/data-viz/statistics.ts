/**
 * REQ-025 §7 & §15.4: Utilidades estadísticas deterministas.
 */

export interface NumericSummary {
  min: number;
  max: number;
  mean: number;
  median: number;
  sum: number;
  count: number;
}

export function computeNumericSummary(values: number[]): NumericSummary {
  const filtered = values.filter((v) => typeof v === "number" && Number.isFinite(v));
  if (filtered.length === 0) {
    return { min: 0, max: 0, mean: 0, median: 0, sum: 0, count: 0 };
  }

  const sorted = [...filtered].sort((a, b) => a - b);
  const count = sorted.length;
  const min = sorted[0];
  const max = sorted[count - 1];
  const sum = sorted.reduce((acc, v) => acc + v, 0);
  const mean = sum / count;

  let median: number;
  const mid = Math.floor(count / 2);
  if (count % 2 === 0) {
    median = (sorted[mid - 1] + sorted[mid]) / 2;
  } else {
    median = sorted[mid];
  }

  return {
    min,
    max,
    mean: Math.round(mean * 10000) / 10000,
    median: Math.round(median * 10000) / 10000,
    sum: Math.round(sum * 10000) / 10000,
    count,
  };
}

export function findExtremaIndices(values: number[]): { minIndex: number; maxIndex: number } {
  let minIndex = 0;
  let maxIndex = 0;
  let minVal = Infinity;
  let maxVal = -Infinity;

  for (let i = 0; i < values.length; i++) {
    const v = values[i];
    if (typeof v === "number" && Number.isFinite(v)) {
      if (v < minVal) {
        minVal = v;
        minIndex = i;
      }
      if (v > maxVal) {
        maxVal = v;
        maxIndex = i;
      }
    }
  }

  return { minIndex, maxIndex };
}
