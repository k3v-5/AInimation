import {
  DataPoint,
  EditorialDataset,
} from "./types.js";
import { DatasetValidationError } from "./errors.js";
import { EditorialDatasetSchema } from "./schemas.js";

export interface NormalizedDataPoint extends DataPoint {
  normalizedValue: number;
  normalizedTimestamp?: number;
}

export interface NormalizedDataset extends Omit<EditorialDataset, "points"> {
  points: NormalizedDataPoint[];
  minValue: number;
  maxValue: number;
  valueRange: number;
  minTimestamp?: number;
  maxTimestamp?: number;
}

/**
 * REQ-4I-007: Dataset Normalization Engine.
 * Pure mathematical functions for dataset bounding, normalization and constant-dataset handling.
 */
export class DataNormalizer {
  public static calculateMin(points: DataPoint[]): number {
    if (points.length === 0) {
      throw new DatasetValidationError("Cannot calculate min on empty points array.");
    }
    let min = points[0].value;
    for (let i = 1; i < points.length; i++) {
      if (points[i].value < min) {
        min = points[i].value;
      }
    }
    return min;
  }

  public static calculateMax(points: DataPoint[]): number {
    if (points.length === 0) {
      throw new DatasetValidationError("Cannot calculate max on empty points array.");
    }
    let max = points[0].value;
    for (let i = 1; i < points.length; i++) {
      if (points[i].value > max) {
        max = points[i].value;
      }
    }
    return max;
  }

  public static calculateRange(points: DataPoint[]): number {
    const min = this.calculateMin(points);
    const max = this.calculateMax(points);
    return max - min;
  }

  public static normalizeValue(value: number, min: number, max: number): number {
    if (!Number.isFinite(value) || !Number.isFinite(min) || !Number.isFinite(max)) {
      throw new DatasetValidationError(`Non-finite numbers passed to normalizeValue: value=${value}, min=${min}, max=${max}`);
    }
    if (max === min) {
      return 0.5; // Constant dataset behavior specified by REQ-4I-007
    }
    const normalized = (value - min) / (max - min);
    return Math.max(0.0, Math.min(1.0, normalized));
  }

  public static normalizeTimestamp(timestamp: number, minTime: number, maxTime: number): number {
    if (!Number.isFinite(timestamp) || !Number.isFinite(minTime) || !Number.isFinite(maxTime)) {
      throw new DatasetValidationError(`Non-finite numbers passed to normalizeTimestamp: t=${timestamp}, min=${minTime}, max=${maxTime}`);
    }
    if (maxTime === minTime) {
      return 0.0;
    }
    const normalized = (timestamp - minTime) / (maxTime - minTime);
    return Math.max(0.0, Math.min(1.0, normalized));
  }

  public static normalizeDataset(dataset: EditorialDataset): NormalizedDataset {
    // Validate schema
    const parsed = EditorialDatasetSchema.parse(dataset);

    const min = this.calculateMin(parsed.points);
    const max = this.calculateMax(parsed.points);
    const range = max - min;

    // Check timestamps if present
    const timestamps = parsed.points
      .map((p) => p.timestampSeconds)
      .filter((t): t is number => t !== undefined);

    let minTime: number | undefined;
    let maxTime: number | undefined;

    if (timestamps.length > 0) {
      minTime = Math.min(...timestamps);
      maxTime = Math.max(...timestamps);
    }

    const normalizedPoints: NormalizedDataPoint[] = parsed.points.map((p) => {
      const normalizedValue = this.normalizeValue(p.value, min, max);
      let normalizedTimestamp: number | undefined;
      if (p.timestampSeconds !== undefined && minTime !== undefined && maxTime !== undefined) {
        normalizedTimestamp = this.normalizeTimestamp(p.timestampSeconds, minTime, maxTime);
      }
      return {
        ...p,
        normalizedValue,
        normalizedTimestamp,
      };
    });

    return {
      id: parsed.id,
      title: parsed.title,
      unit: parsed.unit ?? "",
      description: parsed.description,
      source: parsed.source as any,
      schemaVersion: parsed.schemaVersion,
      points: normalizedPoints,
      minValue: min,
      maxValue: max,
      valueRange: range,
      minTimestamp: minTime,
      maxTimestamp: maxTime,
    } as any;
  }
}
