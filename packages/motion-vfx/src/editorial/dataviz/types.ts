import { DataVizIssue } from "./errors.js";

export type VisualizationType =
  | "BAR_CHART"
  | "LINE_GRAPH"
  | "BIG_STAT"
  | "CHRONOLOGY";

export type ChartOrientation = "VERTICAL" | "HORIZONTAL";

export type CompositionPreset =
  | "LANDSCAPE_16_9"
  | "VERTICAL_9_16"
  | "SQUARE_1_1";

export type DataUnit =
  | "NONE"
  | "COUNT"
  | "PERCENT"
  | "CURRENCY"
  | "TIME"
  | "DISTANCE"
  | "WEIGHT"
  | "CUSTOM";

export type DataPointEmphasis = "NONE" | "PRIMARY" | "SECONDARY";

export interface DataPoint {
  id: string;
  label: string;
  value: number;
  category?: string;
  date?: string;
  unit?: string;
  source?: string;
  emphasis?: DataPointEmphasis;
}

export interface DataSet {
  id: string;
  title?: string;
  description?: string;
  unit?: string;
  points: DataPoint[];
  source?: string;
  sourceUrl?: string;
  updatedAt?: string;
}

export interface NormalizedDataPoint extends DataPoint {
  normalizedValue: number;
  timestampSeconds?: number;
}

export interface Point2D {
  x: number;
  y: number;
}

export interface Rect {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface Margins {
  top: number;
  right: number;
  bottom: number;
  left: number;
}

export interface DataVizLayout {
  bounds: Rect;
  margins: Margins;
  safeZone: Rect;
  contentBounds: Rect;
}

export type ScaleType = "LINEAR" | "TIME_LINEAR" | "CATEGORICAL";

export interface DataVizScale {
  id: string;
  type: ScaleType;
  domain: [number, number] | string[];
  range: [number, number];
  warning?: string;
}

export type AnimationProperty =
  | "OPACITY"
  | "POSITION"
  | "SCALE"
  | "PATH_PROGRESS"
  | "NUMERIC_VALUE";

export type EasingCurve =
  | "LINEAR"
  | "EASE_IN_CUBIC"
  | "EASE_OUT_CUBIC"
  | "EASE_IN_OUT_CUBIC";

export interface DataVizAnimation {
  id: string;
  targetId: string;
  property: AnimationProperty;
  startSeconds: number;
  endSeconds: number;
  easing: EasingCurve;
  from: number | number[];
  to: number | number[];
}

export type DataVizElementType =
  | "BAR"
  | "LINE"
  | "POINT"
  | "AXIS"
  | "TICK"
  | "LABEL"
  | "COUNTER"
  | "CARD"
  | "DIVIDER"
  | "NODE";

export interface DataBinding {
  datasetId: string;
  dataPointId: string;
  sourcePath: string;
}

export interface DataVizElement {
  id: string;
  type: DataVizElementType;
  position: Point2D;
  bounds?: Rect;
  dataBinding?: DataBinding;
  style?: Record<string, unknown>;
  properties: Record<string, unknown>;
}

export type MotionPreset =
  | "EDITORIAL"
  | "MINIMAL"
  | "FAST"
  | "DOCUMENTARY";

export interface DataVizStyleProfile {
  primaryColor: string;
  accentColor: string;
  backgroundColor: string;
  textColor: string;
  mutedColor: string;
  positiveColor: string;
  negativeColor: string;

  titleFontFamily: string;
  titleFontWeight: number;
  labelFontFamily: string;
  labelFontWeight: number;

  titleSize: number;
  labelSize: number;
  valueSize: number;

  tracking: number;
  cornerRadius: number;

  motionPreset: MotionPreset;
}

export interface DataVizIR {
  schemaVersion: "1.0.0";
  engineVersion: string;
  id: string;
  type: VisualizationType;

  composition: {
    width: number;
    height: number;
    fps: number;
    durationSeconds: number;
  };

  dataset: {
    id: string;
    points: NormalizedDataPoint[];
  };

  layout: DataVizLayout;
  scales: DataVizScale[];
  elements: DataVizElement[];
  animations: DataVizAnimation[];
  style: DataVizStyleProfile;

  metadata: {
    title?: string;
    source?: string;
    generatedAtDeterministic: boolean;
    datasetId: string;
    visualizationType: VisualizationType;
    editorialProfileId?: string;
    engineVersion: string;
  };

  checksumSha256?: string;
}

export interface DataVizReport {
  status: "VALID" | "VALID_WITH_WARNINGS" | "BLOCKED";
  visualizationType: VisualizationType;
  blockingIssues: DataVizIssue[];
  warnings: DataVizIssue[];
  elementCount: number;
  animationCount: number;
  checksumSha256: string;
  deterministic: true;
  metrics: {
    dataPointCount: number;
    occupiedAreaRatio: number;
    safeZoneCompliance: number;
    overlapCount: number;
    overflowCount: number;
  };
}

export interface TimelineEvent {
  id: string;
  date: string;
  label: string;
  description?: string;
  importance?: "LOW" | "MEDIUM" | "HIGH" | "PEAK";
}

export interface BigStatData {
  value: number | string;
  label: string;
  unit?: string;
  context?: string;
  source?: string;
  emphasis?: DataPointEmphasis;
}

export type DataVizExecutionMode = "VALIDATE_ONLY" | "IR_ONLY" | "COMPILE";

export interface DataVizCompilationResult {
  ir: DataVizIR;
  report: DataVizReport;
  jsx?: string;
}

export interface CommonChartOptions {
  composition?: CompositionPreset;
  fps?: 24 | 25 | 30 | 50 | 60;
  durationSeconds?: number;
  styleProfile?: Partial<DataVizStyleProfile>;
  executionMode?: DataVizExecutionMode;
  editorialProfileId?: string;
}

export interface BarChartOptions extends CommonChartOptions {
  orientation?: ChartOrientation;
  barWidthRatio?: number;
  showBaseline?: boolean;
  staggerSeconds?: number;
  showValues?: boolean;
  showLabels?: boolean;
}

export interface TrendLineOptions extends CommonChartOptions {
  strokeWidthPx?: number;
  writeOnDurationSeconds?: number;
  showPoints?: boolean;
  highlightPoints?: boolean;
  showBaseline?: boolean;
  sortByDate?: boolean;
}

export interface BigStatOptions extends CommonChartOptions {
  showAccentLine?: boolean;
  accentLineHeightPx?: number;
}

export interface ChronologyOptions extends CommonChartOptions {
  orientation?: ChartOrientation;
  staggerSeconds?: number;
  allowCollisionShifting?: boolean;
}

export interface DataVisualizationEngine {
  compileBarChart(dataset: DataSet, options?: BarChartOptions): DataVizCompilationResult;
  compileTrendLine(dataset: DataSet, options?: TrendLineOptions): DataVizCompilationResult;
  generateBigStat(data: BigStatData, options?: BigStatOptions): DataVizCompilationResult;
  generateChronology(events: TimelineEvent[], options?: ChronologyOptions): DataVizCompilationResult;
}
