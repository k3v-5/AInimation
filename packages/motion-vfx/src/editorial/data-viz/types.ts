/**
 * REQ-025: Data Visualization Engine — Contratos de tipos principales.
 * v4.0.0-editorial-master
 */

export type DataColumnType = "STRING" | "NUMBER" | "DATE" | "BOOLEAN";

export type DataValue = string | number | boolean | null;

export interface DataColumn {
  key: string;
  label: string;
  type: DataColumnType;
}

export interface DataRow {
  [column: string]: DataValue;
}

export interface DataSource {
  id: string;
  title: string;
  publisher?: string;
  url?: string;
  accessedAt?: string;
  citationText?: string;
}

export interface DataEvidenceLink {
  evidenceId: string;
  claimIds: string[];
}

export interface DataVisualizationDataset {
  id: string;
  title?: string;
  description?: string;
  unit?: string;
  source?: DataSource;
  columns: DataColumn[];
  rows: DataRow[];
}

export type DuplicatePolicy =
  | "REJECT"
  | "AGGREGATE_SUM"
  | "AGGREGATE_AVERAGE"
  | "KEEP_LAST";

export interface NumericRange {
  min: number;
  max: number;
  hasZero: boolean;
}

export interface TemporalRange {
  minTimestamp: number;
  maxTimestamp: number;
  minIso: string;
  maxIso: string;
}

export interface NormalizedDataCell {
  raw: DataValue;
  normalized?: number;
  display?: string;
}

export type NormalizedDataRow = Record<string, NormalizedDataCell>;

export interface NormalizedDataset {
  datasetId: string;
  rows: NormalizedDataRow[];
  numericRanges: Record<string, NumericRange>;
  categoryDomains: Record<string, string[]>;
  temporalDomain?: TemporalRange;
}

export type ScaleType = "LINEAR" | "LOGARITHMIC" | "TIME" | "BAND";

export type VisualizationElementType =
  | "RECT"
  | "LINE"
  | "PATH"
  | "CIRCLE"
  | "TEXT"
  | "GROUP"
  | "RULE";

export interface VisualizationElement {
  id: string;
  type: VisualizationElementType;
  x: number;
  y: number;
  width?: number;
  height?: number;
  rotation?: number;
  opacity?: number;
  fill?: string;
  stroke?: string;
  strokeWidth?: number;
  text?: string;
  fontSize?: number;
  fontFamily?: string;
  fontWeight?: string | number;
  textAnchor?: "start" | "middle" | "end";
  children?: VisualizationElement[];
  metadata?: Record<string, any>;
}

export type AnimationProperty =
  | "X"
  | "Y"
  | "WIDTH"
  | "HEIGHT"
  | "OPACITY"
  | "SCALE"
  | "PATH_PROGRESS";

export interface AnimationInstruction {
  targetId: string;
  property: AnimationProperty;
  from: number;
  to: number;
  startSeconds: number;
  endSeconds: number;
  easing: string;
}

export interface AnimationPlan {
  animations: AnimationInstruction[];
}

export interface BarChartSpec {
  categoryColumn: string;
  valueColumns: string[];
  orientation: "VERTICAL" | "HORIZONTAL";
  sort: "INPUT" | "ASCENDING" | "DESCENDING";
  showValues: boolean;
  showLabels: boolean;
  showAxis: boolean;
  animationDurationSeconds: number;
  baselineZero?: boolean;
}

export interface TrendLineSpec {
  xColumn: string;
  yColumn: string;
  showPoints: boolean;
  showLabels: boolean;
  showAxis: boolean;
  showGrid: boolean;
  highlightExtrema: boolean;
  animationDurationSeconds: number;
}

export interface BigStatSpec {
  valueColumn?: string;
  staticValue?: number | string;
  label: string;
  unit?: string;
  prefix?: string;
  suffix?: string;
  sourceLabel?: string;
  animationDurationSeconds: number;
}

export interface ChronologyEvent {
  date: string;
  title: string;
  description?: string;
  category?: string;
  evidenceId?: string;
}

export interface ChronologyTimelineSpec {
  events: ChronologyEvent[];
  orientation: "HORIZONTAL" | "VERTICAL";
  animationDurationSeconds: number;
  undatedPolicy?: "REJECT" | "ALLOW_UNDATED_AT_END";
}

export type VisualizationSpec =
  | { type: "BAR_CHART"; spec: BarChartSpec }
  | { type: "TREND_LINE"; spec: TrendLineSpec }
  | { type: "BIG_STAT"; spec: BigStatSpec }
  | { type: "CHRONOLOGY"; spec: ChronologyTimelineSpec };

export interface VisualizationMetadata {
  datasetId: string;
  sourceId?: string;
  evidenceIds?: string[];
  generatedBy: "DATA_VISUALIZATION_ENGINE";
  engineVersion: string;
  schemaVersion: string;
  editorialProfile?: string;
  complexity?: {
    elementCount: number;
    textElementCount: number;
    dataSeriesCount: number;
    categoryCount: number;
  };
  attention?: {
    visualNovelty: number;
    dataReveal: number;
  };
}

export interface DataVisualizationIR {
  id: string;
  type: "BAR_CHART" | "TREND_LINE" | "BIG_STAT" | "CHRONOLOGY";
  width: number;
  height: number;
  durationSeconds: number;
  elements: VisualizationElement[];
  animation: AnimationPlan;
  metadata: VisualizationMetadata;
  checksumSha256: string;
}

export interface DataVisualizationDiagnostic {
  severity: "ERROR" | "WARNING" | "INFO";
  code: string;
  message: string;
  path?: string;
  rowIndex?: number;
  column?: string;
}

export interface DataVisualizationCompilationResult {
  status: "SUCCESS" | "FAILED";
  visualization?: DataVisualizationIR;
  diagnostics: DataVisualizationDiagnostic[];
  checksumSha256?: string;
}
