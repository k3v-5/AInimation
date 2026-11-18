import { DatasetValidationError } from "./errors.js";
import { DataPoint, DataSet, NormalizedDataPoint } from "./types.js";
import { validateDataSet } from "./validators.js";

/**
 * REQ-025 §9: Normalization and Mathematical precision engine.
 */
export function normalizeNumber(value: number): number {
  if (!Number.isFinite(value)) {
    throw new DatasetValidationError(`Cannot normalize non-finite number: ${value}`, "NON_FINITE_NUMBER");
  }
  const rounded = Number(value.toFixed(4));
  return rounded === 0 ? 0 : rounded;
}

export interface NormalizedDatasetResult {
  dataset: DataSet;
  points: NormalizedDataPoint[];
  minValue: number;
  maxValue: number;
  valueRange: number;
  scaleWarning?: string;
}

export class DataNormalizer {
  public static calculateMin(points: DataPoint[]): number {
    if (points.length === 0) {
      throw new DatasetValidationError("Cannot calculate min on empty points array", "EMPTY_POINTS");
    }
    let min = points[0].value;
    for (let i = 1; i < points.length; i++) {
      if (points[i].value < min) {
        min = points[i].value;
      }
    }
    return normalizeNumber(min);
  }

  public static calculateMax(points: DataPoint[]): number {
    if (points.length === 0) {
      throw new DatasetValidationError("Cannot calculate max on empty points array", "EMPTY_POINTS");
    }
    let max = points[0].value;
    for (let i = 1; i < points.length; i++) {
      if (points[i].value > max) {
        max = points[i].value;
      }
    }
    return normalizeNumber(max);
  }

  public static calculateRange(points: DataPoint[]): number {
    const min = this.calculateMin(points);
    const max = this.calculateMax(points);
    return normalizeNumber(max - min);
  }

  public static normalizeValue(value: number, min: number, max: number): number {
    if (!Number.isFinite(value) || !Number.isFinite(min) || !Number.isFinite(max)) {
      throw new DatasetValidationError("Non-finite values passed to normalizeValue", "NON_FINITE_VALUE");
    }

    // REQ-025 §15: Constant dataset condition (min === max) -> 0.50
    if (max === min) {
      return 0.5;
    }

    const ratio = (value - min) / (max - min);
    const clamped = Math.max(0.0, Math.min(1.0, ratio));
    return normalizeNumber(clamped);
  }

  public static normalizeDataset(raw: DataSet): NormalizedDatasetResult {
    const validated = validateDataSet(raw);
    const min = this.calculateMin(validated.points);
    const max = this.calculateMax(validated.points);
    const range = this.calculateRange(validated.points);

    let scaleWarning: string | undefined;
    if (min === max) {
      scaleWarning = "CONSTANT_DOMAIN"; // REQ-025 §15
    }

    // Non-destructive mapping
    const points: NormalizedDataPoint[] = validated.points.map((p) => {
      const normVal = this.normalizeValue(p.value, min, max);
      let timestampSeconds: number | undefined;

      if (p.date) {
        // Parse year or ISO date
        if (/^\d{4}$/.test(p.date.trim())) {
          timestampSeconds = parseInt(p.date.trim(), 10);
        } else {
          const parsedTime = Date.parse(p.date);
          if (!Number.isNaN(parsedTime)) {
            timestampSeconds = parsedTime / 1000.0;
          }
        }
      }

      return {
        ...p,
        value: normalizeNumber(p.value),
        normalizedValue: normVal,
        timestampSeconds,
      };
    });

    return {
      dataset: validated,
      points,
      minValue: min,
      maxValue: max,
      valueRange: range,
      scaleWarning,
    };
  }
}
