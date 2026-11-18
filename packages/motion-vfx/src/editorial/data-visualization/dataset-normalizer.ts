import { DataSet, DataRow, NullValuePolicy, EditorialDataset } from "./types.js";
import { DatasetValidationError } from "./errors.js";

/**
 * REQ-025 §12, §13, §38: Normalización determinista de datasets.
 */

export interface NormalizedDatasetResult {
  rows: DataRow[];
  minValue: number;
  maxValue: number;
  rowCount: number;
}

export function normalizeDataset(
  dataset: DataSet,
  valueColumnKey: string,
  options: {
    nullPolicy?: NullValuePolicy;
    min?: number;
    max?: number;
  } = {}
): NormalizedDatasetResult {
  const nullPolicy = options.nullPolicy ?? "REJECT";
  const processedRows: DataRow[] = [];
  const rawValues: number[] = [];

  for (let r = 0; r < dataset.rows.length; r++) {
    const row = dataset.rows[r];
    const val = row[valueColumnKey];

    if (val === null || val === undefined) {
      if (nullPolicy === "REJECT") {
        throw new DatasetValidationError(
          `Valor nulo no permitido en fila ${r}, columna '${valueColumnKey}' bajo política REJECT.`
        );
      } else if (nullPolicy === "SKIP") {
        continue;
      } else if (nullPolicy === "ZERO") {
        rawValues.push(0);
        processedRows.push({ ...row, [valueColumnKey]: 0 });
      }
    } else {
      const numVal = Number(val);
      if (Number.isNaN(numVal) || !Number.isFinite(numVal)) {
        throw new DatasetValidationError(
          `Valor no numérico '${val}' en fila ${r}, columna '${valueColumnKey}'.`
        );
      }
      rawValues.push(numVal);
      processedRows.push({ ...row, [valueColumnKey]: numVal });
    }
  }

  if (rawValues.length === 0) {
    return {
      rows: [],
      minValue: 0,
      maxValue: 0,
      rowCount: 0,
    };
  }

  const vMin = options.min !== undefined ? options.min : Math.min(...rawValues);
  const vMax = options.max !== undefined ? options.max : Math.max(...rawValues);
  const isConstant = Math.abs(vMax - vMin) < 1e-10;

  const normalizedRows: DataRow[] = processedRows.map((row) => {
    const val = Number(row[valueColumnKey]);
    let norm: number;
    if (isConstant) {
      norm = 0.5;
    } else {
      norm = (val - vMin) / (vMax - vMin);
    }
    const clampedNorm = Math.max(0, Math.min(1, Number(norm.toFixed(4))));
    return {
      ...row,
      _normalizedValue: clampedNorm,
    };
  });

  return {
    rows: normalizedRows,
    minValue: vMin,
    maxValue: vMax,
    rowCount: normalizedRows.length,
  };
}

/**
 * Adapter para compatibilidad con suites preexistentes (Fase 4I / DataVisualization.test.ts)
 */
export class DataNormalizer {
  public static normalizeDataset(dataset: EditorialDataset): any {
    const points = dataset.points ?? [];
    if (points.length === 0) {
      return { ...dataset, minValue: 0, maxValue: 0, points: [] };
    }

    const values = points.map((p) => p.value);
    const minValue = Math.min(...values);
    const maxValue = Math.max(...values);
    const isConstant = Math.abs(maxValue - minValue) < 1e-10;

    const normalizedPoints = points.map((p) => {
      let norm = isConstant ? 0.5 : (p.value - minValue) / (maxValue - minValue);
      norm = Math.max(0, Math.min(1, Number(norm.toFixed(4))));
      return {
        ...p,
        normalizedValue: norm,
      };
    });

    return {
      ...dataset,
      minValue,
      maxValue,
      points: normalizedPoints,
    };
  }
}
