import {
  DataVisualizationDataset,
  NormalizedDataset,
  NormalizedDataRow,
  NumericRange,
  TemporalRange,
} from "./types.js";
import { assertValidDataset } from "./validation.js";

/**
 * REQ-025 §8: Normalización determinista de datasets tabulares.
 * Garantiza inmutabilidad estricta del input y acotamiento en [0.0, 1.0].
 */

export function normalizeDataset(
  dataset: DataVisualizationDataset
): NormalizedDataset {
  assertValidDataset(dataset);

  const numericRanges: Record<string, NumericRange> = {};
  const categoryDomains: Record<string, Set<string>> = {};
  let minTime = Infinity;
  let maxTime = -Infinity;
  let hasDates = false;

  // 1. Identificar columnas numéricas, categóricas y temporales
  for (const col of dataset.columns) {
    if (col.type === "NUMBER") {
      numericRanges[col.key] = {
        min: Infinity,
        max: -Infinity,
        hasZero: false,
      };
    } else if (col.type === "STRING" || col.type === "BOOLEAN") {
      categoryDomains[col.key] = new Set<string>();
    } else if (col.type === "DATE") {
      hasDates = true;
    }
  }

  // 2. Primera pasada: extraer rangos numéricos y categorías
  for (const row of dataset.rows) {
    for (const col of dataset.columns) {
      const val = row[col.key];
      if (val === null || val === undefined) continue;

      if (col.type === "NUMBER" && typeof val === "number" && Number.isFinite(val)) {
        const range = numericRanges[col.key];
        if (val < range.min) range.min = val;
        if (val > range.max) range.max = val;
        if (val === 0) range.hasZero = true;
      } else if (col.type === "STRING" || col.type === "BOOLEAN") {
        categoryDomains[col.key].add(String(val));
      } else if (col.type === "DATE") {
        const t = typeof val === "number" ? val : Date.parse(String(val));
        if (!Number.isNaN(t)) {
          if (t < minTime) minTime = t;
          if (t > maxTime) maxTime = t;
        }
      }
    }
  }

  // 3. Ajustar rangos vacíos o constantes
  for (const key of Object.keys(numericRanges)) {
    const range = numericRanges[key];
    if (range.min === Infinity) {
      range.min = 0;
      range.max = 0;
      range.hasZero = true;
    } else {
      if (range.min <= 0 && range.max >= 0) {
        range.hasZero = true;
      }
    }
  }

  // Ordenar dominios categóricos de forma determinista
  const sortedDomains: Record<string, string[]> = {};
  for (const [key, set] of Object.entries(categoryDomains)) {
    sortedDomains[key] = Array.from(set).sort((a, b) => a.localeCompare(b));
  }

  let temporalDomain: TemporalRange | undefined = undefined;
  if (hasDates && Number.isFinite(minTime) && Number.isFinite(maxTime)) {
    temporalDomain = {
      minTimestamp: minTime,
      maxTimestamp: maxTime,
      minIso: new Date(minTime).toISOString(),
      maxIso: new Date(maxTime).toISOString(),
    };
  }

  // 4. Segunda pasada: normalización acotada de cada fila
  const normalizedRows: NormalizedDataRow[] = [];

  for (let r = 0; r < dataset.rows.length; r++) {
    const row = dataset.rows[r];
    const normRow: NormalizedDataRow = {};

    for (const col of dataset.columns) {
      const val = row[col.key];
      if (val === null || val === undefined) {
        normRow[col.key] = { raw: null, normalized: undefined, display: "—" };
        continue;
      }

      if (col.type === "NUMBER" && typeof val === "number" && Number.isFinite(val)) {
        const range = numericRanges[col.key];
        let normVal: number;
        if (range.max === range.min) {
          normVal = 0.5; // Caso dataset constante: punto medio exacto
        } else {
          normVal = (val - range.min) / (range.max - range.min);
          if (normVal < 0) normVal = 0;
          if (normVal > 1) normVal = 1;
        }
        normRow[col.key] = {
          raw: val,
          normalized: Math.round(normVal * 10000) / 10000,
          display: val.toString(),
        };
      } else {
        normRow[col.key] = {
          raw: val,
          display: String(val),
        };
      }
    }

    normalizedRows.push(normRow);
  }

  return {
    datasetId: dataset.id,
    rows: normalizedRows,
    numericRanges,
    categoryDomains: sortedDomains,
    temporalDomain,
  };
}

/**
 * REQ-025 §6: Normalización numérica determinista acotada en [0, 1].
 * Para series constantes (min === max), aplica la política canónica de 0.5 sin división por cero.
 */
export function normalizeRange(value: number, min: number, max: number): number {
  if (!Number.isFinite(value) || !Number.isFinite(min) || !Number.isFinite(max)) {
    throw new Error(`normalizeRange: inputs must be finite numbers (${value}, ${min}, ${max})`);
  }
  if (min === max) {
    return 0.5;
  }
  const normalized = (value - min) / (max - min);
  return Math.max(0.0, Math.min(1.0, normalized));
}
