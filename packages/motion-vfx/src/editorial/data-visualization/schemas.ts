import { z } from "zod";

export const DataPointSchema = z.object({
  id: z.string().min(1),
  label: z.string().min(1),
  value: z.number().finite(),
  timestampSeconds: z.number().finite().nonnegative().optional(),
  category: z.string().min(1).optional(),
  sourceId: z.string().min(1).optional(),
  metadata: z.record(z.union([z.string(), z.number().finite(), z.boolean()])).optional(),
});

export const DatasetSourceSchema = z.object({
  type: z.enum(["CSV", "JSON", "MANUAL", "EVIDENCE"]),
  uri: z.string().min(1).optional(),
  checksumSha256: z.string().length(64).optional(),
  citationId: z.string().min(1).optional(),
});

export const EditorialDatasetSchema = z
  .object({
    id: z.string().min(1),
    title: z.string().min(1),
    unit: z.string().optional(),
    description: z.string().optional(),
    points: z.array(DataPointSchema).min(1),
    source: DatasetSourceSchema.optional(),
    schemaVersion: z.string().default("1.0.0"),
  })
  .superRefine((data, ctx) => {
    const ids = new Set<string>();
    for (let i = 0; i < data.points.length; i++) {
      const p = data.points[i];
      if (ids.has(p.id)) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: `Duplicate point id '${p.id}' detected at index ${i}.`,
          path: ["points", i, "id"],
        });
      }
      ids.add(p.id);
    }
  });

export const VisualScaleSchema = z.object({
  min: z.number().finite(),
  max: z.number().finite(),
  pixelStart: z.number().finite(),
  pixelEnd: z.number().finite(),
});

export const BarChartConfigSchema = z.object({
  orientation: z.enum(["VERTICAL", "HORIZONTAL"]).default("VERTICAL"),
  durationSeconds: z.number().finite().positive().default(4.0),
  staggerSeconds: z.number().finite().nonnegative().default(0.15),
  showValues: z.boolean().default(true),
  showLabels: z.boolean().default(true),
  showBaseline: z.boolean().default(true),
  accentColor: z.string().regex(/^#[0-9A-Fa-f]{6}$/).default("#FF1424"),
  backgroundColor: z.string().regex(/^#[0-9A-Fa-f]{6}$/).default("#000000"),
});

export const BarGeometrySchema = z.object({
  id: z.string().min(1),
  x: z.number().finite(),
  y: z.number().finite(),
  width: z.number().finite().nonnegative(),
  height: z.number().finite().nonnegative(),
  value: z.number().finite(),
  label: z.string(),
  color: z.string().regex(/^#[0-9A-Fa-f]{6}$/),
});

export const CounterAnimationSchema = z.object({
  startValue: z.number().finite(),
  endValue: z.number().finite(),
  startSeconds: z.number().finite().nonnegative(),
  endSeconds: z.number().finite().positive(),
  decimals: z.number().int().nonnegative().default(0),
});

export const GraphPointSchema = z.object({
  sourceId: z.string().min(1),
  x: z.number().finite(),
  y: z.number().finite(),
  value: z.number().finite(),
  timestampSeconds: z.number().finite().nonnegative(),
});

export const StrokeAnimationSchema = z.object({
  startSeconds: z.number().finite().nonnegative(),
  endSeconds: z.number().finite().positive(),
  progressFunction: z.enum(["LINEAR", "EASE_IN_OUT", "EASE_OUT"]).default("EASE_IN_OUT"),
});

export const KeyPointSchema = z.object({
  sourceId: z.string().min(1),
  timestampSeconds: z.number().finite().nonnegative(),
  value: z.number().finite(),
  label: z.string().min(1),
  type: z.enum(["MIN", "MAX", "FIRST", "LAST", "SIGNIFICANT_DELTA"]),
});

export const DividerSpecSchema = z.object({
  color: z.string().regex(/^#[0-9A-Fa-f]{6}$/),
  thicknessPx: z.number().finite().positive(),
  widthPx: z.number().finite().positive(),
});

export const BigStatCardSchema = z.object({
  value: z.union([z.number().finite(), z.string().min(1)]),
  label: z.string().min(1),
  unit: z.string().optional(),
  sourceId: z.string().optional(),
  accentColor: z.string().regex(/^#[0-9A-Fa-f]{6}$/),
  divider: DividerSpecSchema,
});

export const TimelineEventSchema = z.object({
  id: z.string().min(1),
  timestamp: z.number().finite().nonnegative(),
  label: z.string().min(1),
  description: z.string().optional(),
  sourceId: z.string().optional(),
  importance: z.number().finite().min(0.0).max(1.0).default(0.5),
});

export const LabelCollisionSchema = z.object({
  firstId: z.string().min(1),
  secondId: z.string().min(1),
  overlapPx: z.number().finite().positive(),
});

export const VisualizationElementSchema = z.object({
  id: z.string().min(1),
  type: z.enum([
    "BAR",
    "AXIS",
    "LABEL",
    "COUNTER",
    "LINE_SEGMENT",
    "KEY_POINT",
    "STAT_CARD",
    "TIMELINE_NODE",
  ]),
  startTimeSeconds: z.number().finite().nonnegative(),
  durationSeconds: z.number().finite().positive(),
  geometry: z.record(z.unknown()),
  sourcePointId: z.string().optional(),
  datasetId: z.string().optional(),
  citationId: z.string().optional(),
});

export const DataVisualizationIRSchema = z.object({
  id: z.string().min(1),
  type: z.enum(["BAR_CHART", "TREND_LINE", "BIG_STAT", "CHRONOLOGY"]),
  durationSeconds: z.number().finite().positive(),
  elements: z.array(VisualizationElementSchema),
  sourceDatasetId: z.string().optional(),
  checksumSha256: z.string().length(64).optional(),
  schemaVersion: z.string().default("1.0.0"),
});
