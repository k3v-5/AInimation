import { z } from "zod";
import {
  MAX_DATA_POINTS,
  MAX_DESCRIPTION_LENGTH,
  MAX_LABEL_LENGTH,
  MAX_TIMELINE_EVENTS,
} from "./constants.js";
import { DatasetTooLargeError, DatasetValidationError } from "./errors.js";
import { BigStatData, DataPoint, DataSet, TimelineEvent } from "./types.js";

export const DataPointSchema = z.object({
  id: z.string().min(1, "DataPoint id cannot be empty"),
  label: z.string().min(1, "DataPoint label cannot be empty").max(MAX_LABEL_LENGTH, "Label too long"),
  value: z.number().refine((v) => Number.isFinite(v), {
    message: "Value must be a finite number (no NaN or Infinity)",
  }),
  category: z.string().optional(),
  date: z.string().optional(),
  unit: z.string().optional(),
  source: z.string().optional(),
  emphasis: z.enum(["NONE", "PRIMARY", "SECONDARY"]).default("NONE"),
});

export const DataSetSchema = z.object({
  id: z.string().min(1, "DataSet id cannot be empty"),
  title: z.string().optional(),
  description: z.string().max(MAX_DESCRIPTION_LENGTH, "Description too long").optional(),
  unit: z.string().optional(),
  points: z.array(DataPointSchema).min(1, "DataSet points array cannot be empty"),
  source: z.string().optional(),
  sourceUrl: z.string().optional(),
  updatedAt: z.string().optional(),
});

export const TimelineEventSchema = z.object({
  id: z.string().min(1, "TimelineEvent id cannot be empty"),
  date: z.string().min(1, "TimelineEvent date cannot be empty"),
  label: z.string().min(1, "TimelineEvent label cannot be empty").max(MAX_LABEL_LENGTH, "Label too long"),
  description: z.string().max(MAX_DESCRIPTION_LENGTH, "Description too long").optional(),
  importance: z.enum(["LOW", "MEDIUM", "HIGH", "PEAK"]).default("MEDIUM"),
});

export const BigStatDataSchema = z.object({
  value: z.union([
    z.number().refine((v) => Number.isFinite(v), "Value must be finite number"),
    z.string().min(1, "Value string cannot be empty"),
  ]),
  label: z.string().min(1, "Label cannot be empty").max(MAX_LABEL_LENGTH, "Label too long"),
  unit: z.string().optional(),
  context: z.string().max(MAX_DESCRIPTION_LENGTH, "Context too long").optional(),
  source: z.string().optional(),
  emphasis: z.enum(["NONE", "PRIMARY", "SECONDARY"]).default("PRIMARY"),
});

/**
 * Validates raw DataSet ensuring bounds, types, and uniqueness.
 */
export function validateDataSet(raw: unknown): DataSet {
  if (!raw || typeof raw !== "object") {
    throw new DatasetValidationError("Input dataset must be an object", "INVALID_DATASET_TYPE");
  }

  const ds = raw as Partial<DataSet>;
  if (Array.isArray(ds.points) && ds.points.length > MAX_DATA_POINTS) {
    throw new DatasetTooLargeError(
      `Dataset points count (${ds.points.length}) exceeds maximum allowed limit (${MAX_DATA_POINTS})`
    );
  }

  const result = DataSetSchema.safeParse(raw);
  if (!result.success) {
    const issue = result.error.issues[0];
    const path = issue.path.join(".");
    throw new DatasetValidationError(issue.message, "DATASET_SCHEMA_VIOLATION", path);
  }

  // Check ID uniqueness
  const seenIds = new Set<string>();
  for (let i = 0; i < result.data.points.length; i++) {
    const pt = result.data.points[i];
    if (seenIds.has(pt.id)) {
      throw new DatasetValidationError(
        `Duplicate DataPoint id detected: '${pt.id}' at index ${i}`,
        "DUPLICATE_POINT_ID",
        `points.${i}.id`
      );
    }
    seenIds.add(pt.id);
  }

  return result.data;
}

/**
 * Validates timeline events array.
 */
export function validateTimelineEvents(raw: unknown): TimelineEvent[] {
  if (!Array.isArray(raw)) {
    throw new DatasetValidationError("Timeline events must be an array", "INVALID_TIMELINE_TYPE");
  }

  if (raw.length === 0) {
    throw new DatasetValidationError("Timeline events array cannot be empty", "EMPTY_TIMELINE_EVENTS");
  }

  if (raw.length > MAX_TIMELINE_EVENTS) {
    throw new DatasetTooLargeError(
      `Timeline events count (${raw.length}) exceeds maximum allowed limit (${MAX_TIMELINE_EVENTS})`
    );
  }

  const validated: TimelineEvent[] = [];
  const seenIds = new Set<string>();

  for (let i = 0; i < raw.length; i++) {
    const res = TimelineEventSchema.safeParse(raw[i]);
    if (!res.success) {
      const issue = res.error.issues[0];
      throw new DatasetValidationError(issue.message, "TIMELINE_SCHEMA_VIOLATION", `events.${i}.${issue.path.join(".")}`);
    }
    if (seenIds.has(res.data.id)) {
      throw new DatasetValidationError(`Duplicate TimelineEvent id detected: '${res.data.id}'`, "DUPLICATE_EVENT_ID", `events.${i}.id`);
    }
    seenIds.add(res.data.id);
    validated.push(res.data);
  }

  return validated;
}

/**
 * Validates BigStat data.
 */
export function validateBigStatData(raw: unknown): BigStatData {
  const res = BigStatDataSchema.safeParse(raw);
  if (!res.success) {
    const issue = res.error.issues[0];
    throw new DatasetValidationError(issue.message, "BIG_STAT_SCHEMA_VIOLATION", issue.path.join("."));
  }
  return res.data;
}
