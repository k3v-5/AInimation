/**
 * REQ-025: Data Visualization Engine & Procedural Statistical Graphics
 * Canonical Type Definitions & Contracts
 */

export type VisualizationType =
  | "BAR_CHART"
  | "TREND_LINE"
  | "BIG_STAT"
  | "CHRONOLOGY";

export type ScaleType = "LINEAR" | "LOGARITHMIC" | "CATEGORICAL";

export type AxisPolicy = "ZERO_BASED" | "DATA_RANGE" | "EXPLICIT";

export type EasingType = "linear" | "easeIn" | "easeOut" | "easeInOut" | "cubic";

export interface DataSourceReference {
  type: "EVIDENCE" | "STATIC" | "URL";
  citationId?: string;
  uri?: string;
  description?: string;
}

export interface DatasetValue {
  label: string;
  value: number;
  timestamp?: number;
  category?: string;
  sourceRef?: string;
}

export interface Dataset {
  id: string;
  title?: string;
  description?: string;
  source?: DataSourceReference;
  unit?: string;
  values: DatasetValue[];
  metadata?: Record<string, unknown>;
}

export interface DatasetValidationError {
  code: string;
  severity: "BLOCKING" | "WARNING";
  field: string;
  index?: number;
  message: string;
}

export interface ValidationResult {
  valid: boolean;
  errors: DatasetValidationError[];
}

export interface NormalizedDataPoint {
  original: DatasetValue;
  normalizedValue: number;
  normalizedTime?: number;
}

export interface NormalizedVisualizationData {
  minValue: number;
  maxValue: number;
  range: number;
  isConstant: boolean;
  normalizedPoints: NormalizedDataPoint[];
}

export interface VisualizationCompileContext {
  width?: number;
  height?: number;
  fps?: number;
  editorialProfile?: string;
  safeZoneProfile?: "TIKTOK" | "INSTAGRAM" | "SHORTS" | "BROADCAST";
  [key: string]: unknown;
}

export interface DataVisualizationCompiler<TInput, TOutput> {
  readonly type: VisualizationType;
  validate(input: TInput): ValidationResult;
  normalize(input: TInput): NormalizedVisualizationData;
  compile(input: TInput, context: VisualizationCompileContext): TOutput;
}

export interface ColorPolicy {
  primary: string;
  secondary?: string;
  accent?: string;
  background?: string;
}

export interface DataPointAnnotation {
  type: "MINIMUM" | "MAXIMUM" | "LOCAL_MINIMUM" | "LOCAL_MAXIMUM";
  index: number;
  value: number;
}

export interface TimelineEvent {
  id: string;
  timestamp: number;
  label: string;
  description?: string;
  importance?: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  sourceRef?: string;
}

export interface AxisDisclosure {
  truncated: boolean;
  minimum: number;
  maximum: number;
  policy: AxisPolicy;
  reason?: string;
}

export interface VisualizationProvenance {
  datasetId: string;
  sourceRefs: string[];
  transformations: string[];
  compilerVersion: string;
  profileId: string;
}

export interface VisualizationEvidenceBinding {
  visualizationId: string;
  datasetId: string;
  sourceRefs: string[];
}

export interface VisualizationProposal {
  id: string;
  type:
    | "CHANGE_AXIS"
    | "REDUCE_LABEL_DENSITY"
    | "SHORTEN_ANIMATION"
    | "CHANGE_SCALE"
    | "RESIZE_LAYOUT";
  timestampSeconds?: number;
  reason: string;
  confidence: number;
}

export interface Rect {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface VisualizationStyle {
  primaryColor: string;
  secondaryColor?: string;
  accentColor: string;
  backgroundColor: string;
  fontFamily: string;
  fontWeight: number;
  labelSize: number;
  valueSize: number;
}

export interface BaseVisualizationNode {
  id: string;
  type: VisualizationType;
  startTimeSeconds: number;
  durationSeconds: number;
  bounds: Rect;
  style: VisualizationStyle;
  provenance: VisualizationProvenance;
  estimatedCognitiveLoad?: number;
  stimuli?: Array<{ type: string; coefficient: number }>;
}
