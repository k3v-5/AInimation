import { z } from "zod";

/**
 * REQ-025: Esquemas Zod para Data Visualization Engine.
 */

export const DataColumnTypeSchema = z.enum(["STRING", "NUMBER", "DATE", "BOOLEAN"]);

export const DataValueSchema = z.union([
  z.string(),
  z.number(),
  z.boolean(),
  z.null(),
]);

export const DataColumnSchema = z.object({
  key: z.string().min(1),
  label: z.string().min(1),
  type: DataColumnTypeSchema,
});

export const DataRowSchema = z.record(z.string(), DataValueSchema);

export const DataSourceSchema = z.object({
  id: z.string().min(1),
  title: z.string().min(1),
  publisher: z.string().optional(),
  url: z.string().optional(),
  accessedAt: z.string().optional(),
  citationText: z.string().optional(),
});

export const DataEvidenceLinkSchema = z.object({
  evidenceId: z.string().min(1),
  claimIds: z.array(z.string().min(1)),
});

export const DataVisualizationDatasetSchema = z.object({
  id: z.string().min(1),
  title: z.string().optional(),
  description: z.string().optional(),
  unit: z.string().optional(),
  source: DataSourceSchema.optional(),
  columns: z.array(DataColumnSchema).min(1),
  rows: z.array(DataRowSchema),
});

export const DuplicatePolicySchema = z.enum([
  "REJECT",
  "AGGREGATE_SUM",
  "AGGREGATE_AVERAGE",
  "KEEP_LAST",
]);

export const BarChartSpecSchema = z.object({
  categoryColumn: z.string().min(1),
  valueColumns: z.array(z.string().min(1)).min(1),
  orientation: z.enum(["VERTICAL", "HORIZONTAL"]),
  sort: z.enum(["INPUT", "ASCENDING", "DESCENDING"]),
  showValues: z.boolean(),
  showLabels: z.boolean(),
  showAxis: z.boolean(),
  animationDurationSeconds: z.number().positive(),
  baselineZero: z.boolean().optional(),
});

export const TrendLineSpecSchema = z.object({
  xColumn: z.string().min(1),
  yColumn: z.string().min(1),
  showPoints: z.boolean(),
  showLabels: z.boolean(),
  showAxis: z.boolean(),
  showGrid: z.boolean(),
  highlightExtrema: z.boolean(),
  animationDurationSeconds: z.number().positive(),
});

export const BigStatSpecSchema = z.object({
  valueColumn: z.string().optional(),
  staticValue: z.union([z.number(), z.string()]).optional(),
  label: z.string().min(1),
  unit: z.string().optional(),
  prefix: z.string().optional(),
  suffix: z.string().optional(),
  sourceLabel: z.string().optional(),
  animationDurationSeconds: z.number().positive(),
});

export const ChronologyEventSchema = z.object({
  date: z.string().min(1),
  title: z.string().min(1),
  description: z.string().optional(),
  category: z.string().optional(),
  evidenceId: z.string().optional(),
});

export const ChronologyTimelineSpecSchema = z.object({
  events: z.array(ChronologyEventSchema).min(1),
  orientation: z.enum(["HORIZONTAL", "VERTICAL"]),
  animationDurationSeconds: z.number().positive(),
  undatedPolicy: z.enum(["REJECT", "ALLOW_UNDATED_AT_END"]).optional(),
});
